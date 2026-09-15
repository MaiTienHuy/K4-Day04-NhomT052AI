# v2 vs v0 — chỉ đổi tools.yaml

- v0: 21/30, case_accuracy **0.70**, wrong_tool 3, missing_info 3, wrong_boundary 3
- v2: 25/30, case_accuracy **0.8333**, wrong_tool 2, wrong_arg 1, wrong_boundary 1, missing_info 1
- Prompt giữ `artifacts/baselines/v0_system_prompt.md`. `provider_error_cases=0`.

## Kỳ vọng lab: wrong_tool / wrong_arg giảm

| | v0 | v2 |
|---|---:|---:|
| H04 extra inspect | FAIL | **PASS** |
| H13 `check=vpn` | FAIL (`None`) | **PASS** |
| H17 `check=vpn` | FAIL | FAIL (`all` thay `vpn`) |
| H03 KB category | PASS | FAIL (`account` thay `email`) |
| M03 correct asset | PASS | FAIL (extra inspect) |

Tách shared service ≠ một máy + enum `check` hết H04/H13. H17/H03 còn arg.

## Side effect (prompt gốc, không phải mục tiêu v2)

H10/H11/H12/M09 PASS nhờ description `clarify` / `inspect_device` / `create_ticket`. M05 và H19 vẫn FAIL.
