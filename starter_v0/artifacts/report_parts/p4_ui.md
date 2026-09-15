# P4 — UI + Transcript + Report (Hoàng Ngọc Đức)

## A1. Agent này làm được gì

Agent helpdesk nội bộ Northstar Labs: đọc status dịch vụ dùng chung, snapshot asset, directory nhân viên, KB, policy, format incident, tạo ticket local sau xác nhận, và tìm thông tin model công khai. Không đoán identifier, không gửi dữ liệu nội bộ ra web, không làm việc ngoài IT helpdesk.

**Link dùng thử:** chạy local `streamlit run app.py` (không deploy). Repo: https://github.com/MaiTienHuy/K4-Day04-NhomT052AI

## A3. Câu hỏi mẫu

1. Kiểm tra trạng thái printing production.
2. Laptop của mình mất Wi-Fi, mình chưa nhớ mã máy.
3. Tạo ticket high cho PR-404 — chưa xác nhận.

## A4. Kịch bản demo đã rehearse

| Scenario | Tool trace cần thấy | Cải thiện version | Fallback |
|---|---|---|---|
| Hội thoại bình thường | `check_service_status` printing/production | v1/v3 routing | `artifacts/transcripts/v3_normal_status_20260915T210053.transcript.json` |
| Thiếu thông tin | `clarify` text, không đoán asset | v1 rule không đoán ID | `v3_missing_info_clarify_20260915T210053.transcript.json` |
| Multi-turn correction | `inspect_device` LT-411 software | v1 latest-turn-wins | `v3_multiturn_correction_20260915T210053.transcript.json` |
| Action boundary | `clarify` yes_no, không `create_ticket` | v1/v2 confirmation | `v3_action_boundary_ticket_20260915T210053.transcript.json` |

## B4. Live chat evidence

| Scenario/turn | Version | Tool calls + args | Transcript | Outcome |
|---|---|---|---|---|
| Normal status | v3 | `check_service_status(service=printing, environment=production)` | `v3_normal_status_20260915T210053.transcript.json` | PASS — đúng dịch vụ dùng chung |
| Missing info | v3 | `clarify(response_type=text)` | `v3_missing_info_clarify_20260915T210053.transcript.json` | PASS — hỏi mã máy, không đoán |
| Multi-turn | v3 | turn 2: `inspect_device(asset_id=LT-411, check=software)` | `v3_multiturn_correction_20260915T210053.transcript.json` | PASS — mã mới thắng LT-240 |
| Ticket boundary | v3 | `clarify(response_type=yes_no)` | `v3_action_boundary_ticket_20260915T210053.transcript.json` | PASS — chưa gọi `create_ticket` |

UI: `starter_v0/app.py`. Bắt buộc dùng `run_model_tool_loop` từ `chat.py`.
Hiện user text, assistant text, từng tool + args, result/error, `artifact_version` và hash.
Transcript ghi vào `artifacts/transcripts/` (không dùng thư mục `transcripts/` bị gitignore).

## B7. Technical reflection

- Fix thuộc `system_prompt.md`: rule toàn cục (không đoán ID, latest turn, confirmation, trust).
- Fix thuộc `tools.yaml`: ranh giới capability, enum, side effect, cấm field external.
- Failure không thấy nếu chỉ nhìn automatic score: secret trong ticket, ID lọt ra Tavily, instruction trong KB, file ticket được tạo dù routing PASS.
- Vòng thêm: đọc `tool_results` của adversarial rồi siết prompt/schema cho đúng 1 failure mode.
