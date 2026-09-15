"""Paced Gemini runner for the P3 eval suites (P3-owned helper).

Why this file exists
--------------------
`starter_v0/.env` on this machine has only a Gemini **free-tier** key.
`run_eval.py` sends one `generate_content` call per case and has **no retry**,
so the free-tier limits bite immediately:

* per-minute limit  -> `429 RESOURCE_EXHAUSTED` with
  `GenerateRequestsPerMinutePerProjectPerModel-FreeTier` (limit 5/min), and
* per-day limit     -> `429 RESOURCE_EXHAUSTED` with
  `GenerateRequestsPerDayPerProjectPerModel-FreeTier` (quotaId); the free-tier
  daily budget is counted **per model**, which is why a model whose daily
  budget is spent has to be replaced by a sibling model of the same family
  (see `artifacts/report_parts/p3_eval.md`, "Run evidence").

Every 429 that `run_eval.py` sees becomes a `provider_error` case, and a run is
only usable as lab evidence when `provider_error_cases == 0` and
`measured_cases == total_cases`. This wrapper therefore only wraps
`providers.make_provider` to add:

1. spacing between calls (`--spacing`, default 14s) so the per-minute limit is
   never tripped, and
2. retry with backoff while the API keeps answering 429/5xx,
3. **abort before writing a run file** when a *daily* quota error shows up, so
   `runs/` never contains a run that looks like an eval result but is actually
   a quota artifact.

Everything else is `run_eval.py` unchanged: case loading, `failure_type`
allow-list, `validate_expected_tools`, `evaluate_phase_b` grading, run_id /
artifact hashes and the run JSON shape are all the starter grader's.

Usage (run from `starter_v0/`):

    python scripts/p3_paced_gemini_run.py --spacing 14 --model gemini-3.6-flash \
        --provider gemini --version v0 --suite group --eval-cases data/eval_group.json

Without `--spacing`/`--model` this is exactly `run_eval.py`.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import run_eval  # noqa: E402  (path bootstrap must happen first)
from providers import make_provider as real_make_provider  # noqa: E402

DEFAULT_SPACING = 14.0
BACKOFFS = [15.0, 20.0, 30.0, 45.0, 60.0, 60.0, 60.0, 60.0]
RETRYABLE_TOKENS = ("429", "RESOURCE_EXHAUSTED", "500", "503", "UNAVAILABLE", "INTERNAL", "overloaded")
DAILY_QUOTA_TOKENS = ("GenerateRequestsPerDay", "PerDay")


def parse_wrapper_args(argv: list[str]) -> tuple[float, list[str]]:
    spacing = DEFAULT_SPACING
    rest: list[str] = []
    index = 0
    while index < len(argv):
        token = argv[index]
        if token == "--spacing":
            spacing = float(argv[index + 1])
            index += 2
            continue
        if token.startswith("--spacing="):
            spacing = float(token.split("=", 1)[1])
            index += 1
            continue
        rest.append(token)
        index += 1
    return spacing, rest


class PacedProvider:
    """Same provider, but calls are spaced out and rate limits are retried."""

    def __init__(self, inner, spacing: float) -> None:
        self._inner = inner
        self._spacing = spacing
        self._last_call = 0.0

    def __getattr__(self, item):
        return getattr(self._inner, item)

    def complete(self, *args, **kwargs):
        attempts = len(BACKOFFS) + 1
        for attempt in range(attempts):
            wait = self._spacing - (time.monotonic() - self._last_call)
            if wait > 0:
                time.sleep(wait)
            try:
                response = self._inner.complete(*args, **kwargs)
                self._last_call = time.monotonic()
                return response
            except Exception as exc:  # noqa: BLE001 - quota/transport errors only
                message = f"{type(exc).__name__}: {exc}"
                if any(token in message for token in DAILY_QUOTA_TOKENS):
                    print(
                        "[paced] DAILY free-tier quota exhausted for this model "
                        "-> aborting before a run file is written",
                        flush=True,
                    )
                    raise SystemExit(3) from exc
                retryable = any(token in message for token in RETRYABLE_TOKENS)
                if not retryable or attempt == attempts - 1:
                    raise
                pause = BACKOFFS[attempt]
                print(f"[paced] rate limited (attempt {attempt + 1}/{attempts}), sleeping {pause:.0f}s", flush=True)
                time.sleep(pause)
                self._last_call = 0.0
        raise RuntimeError("unreachable")


def effective_model(run_eval_argv: list[str], fallback: object) -> object:
    """`--model` from the forwarded run_eval args wins over the provider default."""
    for index, token in enumerate(run_eval_argv):
        if token == "--model" and index + 1 < len(run_eval_argv):
            return run_eval_argv[index + 1]
        if token.startswith("--model="):
            return token.split("=", 1)[1]
    return fallback


def main() -> None:
    spacing, run_eval_argv = parse_wrapper_args(sys.argv[1:])

    def paced_make_provider(name: str):
        provider = real_make_provider(name)
        model = effective_model(run_eval_argv, getattr(provider, "default_model", None))
        print(f"[paced] provider={name} model={model} spacing={spacing:.0f}s", flush=True)
        return PacedProvider(provider, spacing)

    run_eval.make_provider = paced_make_provider
    sys.argv = ["run_eval.py", *run_eval_argv]
    run_eval.main()


if __name__ == "__main__":
    main()
