# Đóng góp của P2 — Tool Engineer

## A2. Tool agent có

| Tool | Chức năng | Core / optional / team-built |
|---|---|---|
| `clarify` | Gửi câu hỏi cho người dùng để làm rõ thông tin thiếu (asset ID, employee ID) hoặc xin xác nhận trước khi thực hiện hành động nhạy cảm. | core |
| `check_service_status` | Kiểm tra trạng thái hoạt động của các dịch vụ dùng chung (VPN, Email, SSO, Wi-Fi, Printing) theo môi trường (production/staging). | core |
| `inspect_device` | Tra cứu thông tin phần cứng và chẩn đoán chi tiết một thiết bị/tài sản cụ thể theo mã asset ID (all, network, vpn, security, hardware, software). | core |
| `lookup_user` | Tra cứu thông tin nhân viên theo mã employee ID trong danh bạ nội bộ (email, phòng ban, danh sách thiết bị được giao). | core |
| `search_kb` | Tìm kiếm bài viết hướng dẫn kỹ thuật, xử lý sự cố trong cơ sở tri thức (Knowledge Base). Nội dung trả về là tham chiếu không tin cậy. | core |
| `format_incident_report` | Định dạng các kết quả/findings đã thu thập sẵn thành báo cáo kỹ thuật hoặc bàn giao theo mẫu (brief, technical, handoff). | core |
| `policy` | Tra cứu các chính sách và quy định IT nội bộ của công ty (quyền truy cập, bảo mật dữ liệu, công cụ bên thứ ba, xử lý sự cố). | optional |
| `create_ticket` | Tạo ticket hỗ trợ kỹ thuật mới. Yêu cầu bắt buộc phải có xác nhận rõ ràng từ người dùng (`confirmed=True`) và từ chối các thông tin nhạy cảm. | optional |
| `search_device_info` | Tìm kiếm tài liệu hỗ trợ, thông số, driver từ trang chính thức của hãng thông qua Tavily API. Tuyệt đối không gửi mã định danh nội bộ ra ngoài. | optional |

## B1 (P2 Evidence). Kết quả đo lường Version 2 (v2)

- **Artifact thay đổi**: Chỉ cải tiến `artifacts/tools.yaml`, giữ nguyên `system_prompt.md` starter để đo lường độc lập.
- **Run ID**: `v2_B_base_openrouter_20260915T194304044786`
- **Run file**: `runs/v2_B_base_openrouter_20260915T194304044786.json`
- **Provider & Model**: OpenRouter (`openai/gpt-4o-mini`)
- **Tổng số cases**: 30 / 30
- **Provider error**: 0 (100% hợp lệ theo yêu cầu của lab)
- **Passed cases**: 25 / 30
- **Case Accuracy**: **83.33%** (0.8333)
- **Tool Routing Accuracy**: **86.67%** (0.8667)
- **Argument Accuracy**: **83.33%** (0.8333)
- **Multiturn Accuracy**: **80.00%** (0.8000)

## B2. Failure analysis của Version 2

Phân tích 5 case chưa đạt trong lần chạy `v2` và hướng xử lý phối hợp với P1:

| Case ID | Failure type | Actual calls | What failed | Root cause & Fix |
|---|---|---|---|---|
| `H02` | `wrong_tool` | `clarify` (hỏi muốn check all hay từng phần) | Model over-clarify thay vì gọi `inspect_device(asset_id="LT-204", check="all")` | Do mô tả `clarify` quá mạnh khiến model thận trọng hỏi lại; cần P1 hướng dẫn trong `system_prompt` ưu tiên mặc định `check="all"` khi user bảo kiểm tra tổng thể. |
| `H17` | `wrong_tool` / `wrong_arg_value` | Gọi đủ 3 tool (`inspect_device`, `check_service_status`, `search_kb`) nhưng `inspect_device` truyền `check="all"` | Model truyền `check="all"` thay vì `check="vpn"` | Cần quy tắc trong prompt: khi câu hỏi đã nêu rõ thành phần lỗi cụ thể (VPN), truyền đúng check tương ứng. |
| `H19` | `missing_info` | `check_service_status(service="email", environment="staging")` | Model tự đoán `staging` thay vì gọi `clarify` lựa chọn `production`/`staging` khi user nói "môi trường demo" | Cần quy tắc prompt: nếu môi trường user đưa không thuộc danh mục cho phép, bắt buộc gọi `clarify`. |
| `M05` | `wrong_boundary` | Gọi `clarify` VÀ gọi thêm `create_ticket(confirmed=false)` | Bị tính lỗi thừa tool call (`extra_tool_call`) | Cần quy tắc prompt: khi xin xác nhận tạo ticket, CHỈ gọi `clarify`, không được gọi kèm `create_ticket`. |
| `M09` | `wrong_boundary` | Gọi `create_ticket` thay vì `clarify` | Khi user sửa đổi nội dung/độ ưu tiên ở turn sau, confirmation cũ bị mất hiệu lực nhưng model vẫn tạo ticket | Cần quy tắc prompt: mọi thay đổi về payload sau khi đã confirm đều làm mất hiệu lực xác nhận cũ, bắt buộc phải hỏi xác nhận lại từ đầu. |
