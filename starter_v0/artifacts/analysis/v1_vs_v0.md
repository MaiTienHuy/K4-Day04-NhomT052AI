# v1 vs v0 — chỉ đổi system_prompt.md

- v0: `artifacts/runs/v0_B_base_openrouter_20260915T192745909789.json` — 21/30, case_accuracy **0.70**
- v1: `artifacts/runs/v1_B_base_openrouter_20260915T194139710401.json` — 24/30, case_accuracy **0.80**
- Tools giữ `artifacts/baselines/v0_tools.yaml`. `provider_error_cases=0`.

## Nhóm missing-info / confirm (mục tiêu v1)

| Case | v0 | v1 |
|---|---|---|
| H10_missing_asset | FAIL `inspect_device("laptop")` | **PASS** `clarify` |
| H11_missing_employee | FAIL `lookup_user` | **PASS** `clarify` |
| H12_confirm_before_ticket | FAIL `create_ticket` | **PASS** `clarify` |
| M05_ticket_confirmation | FAIL extra `create_ticket` | **PASS** |
| M09_confirmation_invalidated | FAIL | **PASS** |
| H19_ambiguous_environment | FAIL | FAIL (vẫn `check_service_status`) |

Hypothesis H10 đúng: không đoán ID + `clarify` hết H10/H11; confirm hết H12/M05/M09.

## Regression / còn lại (hướng v2 — tools.yaml)

| Case | v1 | Ghi chú |
|---|---|---|
| H02_device_routing | FAIL (v0 PASS) | Đúng `inspect_device`, thiếu `check=all` |
| H03_kb_routing | FAIL (v0 PASS) | Đúng `search_kb`, `category=account` thay `email` |
| H04_user_routing | FAIL | Extra `inspect_device` |
| H13 / H17 | FAIL | `check` kỳ vọng `vpn`, actual `None` |
