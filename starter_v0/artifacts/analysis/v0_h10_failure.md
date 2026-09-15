# v0 failure note — H10_missing_asset

Nguồn: `artifacts/runs/v0_B_base_openrouter_20260915T192745909789.json`
Provider/model: openrouter / `openai/gpt-4o-mini`
Baseline: `artifacts/baselines/v0_system_prompt.md` + `v0_tools.yaml`
Suite: base, 30/30 measured, `provider_error_cases=0`, case_accuracy=0.70

```text
Case: H10_missing_asset
Expected calls: clarify(response_type=text)
Actual calls: inspect_device(asset_id="laptop", check="network")
Observed mismatch: missing_tool_call
Tool execution result: inspect_device → error=asset_not_found (asset_id normalized to LAPTOP)
Giả thuyết nguyên nhân: Prompt/tool v0 không cấm đoán identifier. User nói "laptop của mình" (không có LT-…); model bịa asset_id="laptop" rồi inspect thay vì clarify.
Artifact dự định sửa: system_prompt.md (rule toàn cục: thiếu asset ID thì clarify, không đoán/bịa mã)
Metric dự kiến thay đổi: case_accuracy tăng; FAIL missing_info (H10, H11, H19) giảm
Rủi ro regression: nếu viết "luôn clarify" quá rộng, các case đã có ID (H02, H05, M01) có thể bị thừa clarify
```

Các FAIL v0 khác (cùng run): H04 extra `inspect_device`; H11 đoán employee; H12/`M05`/`M09` tạo ticket hoặc bỏ confirm; H13/H17 sai arg `check`; H19 không hỏi environment.
