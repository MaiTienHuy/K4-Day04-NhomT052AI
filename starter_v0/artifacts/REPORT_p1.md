# Day 04 Lab — Bản report P1 (Mai Tiến Huy)

Đây là bản của **Mai Tiến Huy (P1, MSSV 02914, GitHub MaiTienHuy)**.
Các thành viên khác dùng `REPORT_p2.md`, `REPORT_p3.md`, `REPORT_p4.md` và tự commit C2 của mình.

- Team: T052AI
- Provider/model: OpenRouter / `openai/gpt-4o-mini`
- Repo: https://github.com/MaiTienHuy/K4-Day04-NhomT052AI

# PHẦN A — Giới thiệu agent (ngắn)

Agent helpdesk nội bộ Northstar Labs: status dịch vụ dùng chung, snapshot asset, directory, KB, policy, format incident, tạo ticket sau xác nhận, tra model công khai. Không đoán identifier, không gửi dữ liệu nội bộ ra web.

**Link dùng thử:** `cd starter_v0` rồi `streamlit run app.py`.

# PHẦN B — Evidence P1 (prompt / v1)

`v1` chỉ đổi `system_prompt.md`, tools giữ `artifacts/baselines/v0_tools.yaml`.
Prompt hash: `6f55a297182061445946bec61005c1e4e75a2297ea267f87ed4c949ca618b897`.

Hypothesis: rule toàn cục (không đoán ID, latest turn, confirm gắn payload, retrieved content không tin) sẽ cải missing-info / confirmation mà không đổi schema.

| | v0 | v1 |
|---|---:|---:|
| passed / 30 | 21 | 24 |
| case_accuracy | 0.70 | **0.80** |
| tool_routing_accuracy | 0.7667 | **0.9333** |
| provider_error_cases | 0 | 0 |
| measured_cases | 30 | 30 |

Run: `artifacts/runs/v0_B_base_openrouter_20260915T192745909789.json`, `artifacts/runs/v1_B_base_openrouter_20260915T194139710401.json`.

Prompt cover: không đoán asset/employee ID; thiếu info thì `clarify`; confirm gắn payload mới; không tin KB/policy/web; không gửi ID/serial ra `search_device_info`; xin xác nhận trước `create_ticket`.

| Case | v0 | v1 |
|---|---|---|
| H10_missing_asset | FAIL đoán `inspect_device("laptop")` | **PASS** `clarify` |
| H11_missing_employee | FAIL `lookup_user` | **PASS** `clarify` |
| H12_confirm_before_ticket | FAIL `create_ticket` | **PASS** `clarify` |
| M05_ticket_confirmation | FAIL extra `create_ticket` | **PASS** |
| M09_confirmation_invalidated | FAIL | **PASS** |
| H19_ambiguous_environment | FAIL | FAIL |

`version_log.csv` có v0–v3. v3 (cả hai artifact): 26/30, case_accuracy **0.8667** — `artifacts/runs/v3_B_base_openrouter_20260915T205921735306.json`.

# PHẦN C — C2 của Mai Tiến Huy

- **Vai trò:** P1 Lead + Prompt Engineer
- **Đã đổi trong repo:** `TEAMMATES.md`, `artifacts/system_prompt.md`, `version_log.csv`, `report_parts/p1_prompt.md`, điều phối merge PR
- **Artifact:** `system_prompt.md`, `baselines/v0_system_prompt.md`, run v1
- **Commit / PR:** `6f7a6d3`, `7283460`, `6af19a7`; merge PR #1, #4
- **Quyết định kỹ thuật:** Bỏ output JSON cứng của starter vì grader chỉ chấm tool call.
- **Khó khăn:** Lần đầu chỉ push run JSON, prompt starter vẫn trên `main`; đã push đúng prompt khớp hash v1.
- **Học được:** Prompt là policy toàn cục, không hard-code case ID.
- **Nếu làm lại:** Đọc failed traces v0 trước, rồi mới viết rule.
