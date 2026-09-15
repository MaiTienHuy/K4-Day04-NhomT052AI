# Đóng góp của P2 — Tool Engineer

## A2. Tool agent có

| Tool | Chức năng | Core / optional / team-built |
|---|---|---|
| `clarify` | Gửi câu hỏi cho người dùng để làm rõ thông tin thiếu (asset ID, employee ID) hoặc xin xác nhận trước khi thực hiện hành động nhạy cảm. | core |
| `check_service_status` | Kiểm tra trạng thái hoạt động của các dịch vụ dùng chung (VPN, Email, SSO, Wi-Fi, Printing) theo môi trường (production/staging). | core |
| `inspect_device` | Tra cứu thông tin phần cứng và chẩn đoán chi tiết một thiết bị/tài sản cụ thể theo mã asset ID (all, network, vpn, security, hardware, software). | core |
| `lookup_user` | Tra cứu thông tin nhân viên theo mã employee ID trong danh bạ nội bộ (email, phòng ban, danh sách thiết bị được giao). | core |
| `search_kb` | Tìm kiếm bài viết hướng dẫn kỹ thuật, xử lý sự cố trong cơ sở tri thức (Knowledge Base). Nội dung trả về là tham chiếu không đáng tin. | core |
| `format_incident_report` | Định dạng các kết quả/findings đã thu thập sẵn thành báo cáo kỹ thuật hoặc bàn giao theo mẫu (brief, technical, handoff). | core |
| `policy` | Tra cứu các chính sách và quy định IT nội bộ của công ty (quyền truy cập, bảo mật dữ liệu, công cụ bên thứ ba, xử lý sự cố). | optional |
| `create_ticket` | Tạo ticket hỗ trợ kỹ thuật mới. Yêu cầu bắt buộc phải có xác nhận rõ ràng từ người dùng (`confirmed=True`) và từ chối các thông tin nhạy cảm. | optional |
| `search_device_info` | Tìm kiếm tài liệu hỗ trợ, thông số, driver từ trang chính thức của hãng thông qua Tavily API. Tuyệt đối không gửi mã định danh nội bộ ra ngoài. | optional |

## B1 (P2 Evidence). Kết quả đo lường Version 2 (v2)

- **Artifact thay đổi**: Chỉ cải tiến `artifacts/tools.yaml`, giữ nguyên prompt starter (`artifacts/baselines/v0_system_prompt.md`).
- **Run ID**: `v2_B_base_openrouter_20260915T194707650337`
- **Run file**: `artifacts/runs/v2_B_base_openrouter_20260915T194707650337.json`
- **Provider & Model**: OpenRouter (`openai/gpt-4o-mini`)
- **Tổng số cases**: 30 / 30
- **Provider error**: 0
- **Passed cases**: 25 / 30
- **Case Accuracy**: **0.8333**
- **Tool Routing Accuracy**: **0.90**
- **Argument Accuracy**: **0.8333**
- **Multiturn Accuracy**: **0.80**

So với v0 (0.70 / wrong_tool 3): v2 tăng case_accuracy lên 0.8333 và giảm wrong_tool xuống 2.

## B2. Failure analysis của Version 2

Năm case FAIL trên run v2 base ở trên:

| Case ID | Failure type | Actual calls | What failed | Root cause |
|---|---|---|---|---|
| `H03` | `wrong_tool` (arg) | `search_kb(category=account)` | Kỳ vọng `category=email` | Enum KB còn mơ hồ giữa account/email |
| `M03` | `wrong_tool` | extra `inspect_device` | Thừa call sau khi user sửa asset | Description chưa siết “chỉ latest asset” |
| `M05` | `wrong_boundary` | `clarify` + `create_ticket(confirmed=false)` | Extra write-tool khi đang xin xác nhận | Schema còn field `confirmed` nên model vừa hỏi vừa gọi |
| `H17` | `wrong_arg_value` | `inspect_device(check=all)` | Kỳ vọng `check=vpn` | Default `all` thắng khi user đã nêu VPN |
| `H19` | `missing_info` | `check_service_status(email, staging)` | Phải `clarify` khi “demo” không thuộc enum | Environment không hợp lệ vẫn bị đoán |
