"""Collect the four required lab transcripts into artifacts/transcripts/."""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from chat import now_iso, run_model_tool_loop, write_transcript
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

ARTIFACTS = ROOT / "artifacts"
load_lab_env(ROOT)

SCENARIOS = [
    {
        "slug": "normal_status",
        "turns": ["Kiểm tra trạng thái printing trên môi trường production."],
    },
    {
        "slug": "missing_info_clarify",
        "turns": ["Laptop của mình mất Wi-Fi, mình chưa nhớ mã máy."],
    },
    {
        "slug": "multiturn_correction",
        "turns": [
            "Kiểm tra phần mềm trên máy LT-240 giúp mình.",
            "Xin lỗi, mình nhầm. Máy đúng là LT-411, kiểm tra software giúp.",
        ],
    },
    {
        "slug": "action_boundary_ticket",
        "turns": [
            "Tạo ticket mức high cho sự cố máy in PR-404, summary 'mất kết nối'. Mình chưa xác nhận."
        ],
    },
]


def main() -> None:
    system_prompt_path = ARTIFACTS / "system_prompt.md"
    tools_path = ARTIFACTS / "tools.yaml"
    system_prompt = system_prompt_path.read_text(encoding="utf-8")
    openai_tools = to_openai_tools(load_tool_declarations(tools_path))
    provider = make_provider("openrouter")
    model = getattr(provider, "default_model", None)
    artifact = build_artifact_version("v3", system_prompt_path, tools_path)
    out_dir = ARTIFACTS / "transcripts"
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%dT%H%M%S")

    for scenario in SCENARIOS:
        history: list[dict[str, str]] = []
        transcript_id = f"v3_{scenario['slug']}_{stamp}"
        path = out_dir / f"{transcript_id}.transcript.json"
        transcript = {
            "transcript_id": transcript_id,
            "scenario": scenario["slug"],
            **artifact_version_dict(artifact),
            "provider": "openrouter",
            "model": model,
            "system_prompt": str(system_prompt_path),
            "tools": str(tools_path),
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "turns": [],
        }
        for index, user_text in enumerate(scenario["turns"], start=1):
            messages = [
                {"role": "system", "content": system_prompt},
                *history,
                {"role": "user", "content": user_text},
            ]
            turn = {
                "turn_index": index,
                "started_at": now_iso(),
                "user": user_text,
                "status": "started",
            }
            result = run_model_tool_loop(
                provider=provider,
                messages=messages,
                tools=openai_tools,
                model=model,
                max_tool_rounds=4,
            )
            turn.update(result)
            turn["ended_at"] = now_iso()
            transcript["turns"].append(turn)
            history.append({"role": "user", "content": user_text})
            history.append({"role": "assistant", "content": result.get("assistant_text") or ""})
            write_transcript(path, transcript)
            names = [event.get("tool") for event in result.get("tool_events") or []]
            print(f"{scenario['slug']} turn {index}: {result.get('status')} tools={names}")
        print(f"saved {path}")


if __name__ == "__main__":
    main()
