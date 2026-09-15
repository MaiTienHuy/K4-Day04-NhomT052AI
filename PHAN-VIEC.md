# Phân việc Lab Day 04 — IT Helpdesk Agent (4 người)

Tài liệu này để cả nhóm đọc chung, nhận việc, rồi làm **song song**. Không cần chờ người kia xong mới bắt đầu.

Yêu cầu chính thức của lab nằm ở `README.md`. Đây chỉ là cách chia việc.

---

## 1. Điền tên trước khi làm

| Mã | Vai trò | Họ tên | MSSV | GitHub username |
|---|---|---|---|---|
| **P1** | Lead + Prompt Engineer | | | |
| **P2** | Tool Engineer | | | |
| **P3** | Eval + Security | | | |
| **P4** | UI + Transcript + Report | | | |

P1 tạo `TEAMMATES.md` ở thư mục gốc repo (bắt buộc khi nộp) với đủ họ tên, MSSV, GitHub username và vai trò.

---

## 2. Nguyên tắc để 4 người làm cùng lúc

1. Mỗi người **chỉ commit file mình được giao**. Người khác được *đọc* và *chạy*, không *sửa rồi commit*.
2. Mỗi máy vẫn có **cả repo starter**. Test = chạy hệ thống với file starter của người kia, không phải chờ họ sửa xong.
3. Không sửa `chat.py`, `run_eval.py`, `agent.py` trừ khi gặp bug thật (nói cả nhóm trước).
4. Không commit `.env`, API key, `.venv`, ticket đã generate, dữ liệu thật.
5. Mỗi người phải có **ít nhất 1 commit** trên branch nộp bài (không squash merge).
6. Mỗi người **tự viết và tự commit** self-reflection (mục C2 trong report). Không viết hộ.

---

## 3. Ai được sửa file nào

| File / thư mục | Owner | Người khác |
|---|---|---|
| `TEAMMATES.md` | P1 | không sửa |
| `starter_v0/artifacts/system_prompt.md` | P1 | đọc + chạy, không commit |
| `starter_v0/artifacts/version_log.csv` | P1 | gửi số liệu cho P1, không tự ghi |
| `starter_v0/artifacts/tools.yaml` | P2 | đọc + chạy, không commit |
| `starter_v0/data/eval_group.json` | P3 | không sửa |
| `starter_v0/app.py` (tạo mới) | P4 | không sửa |
| `starter_v0/requirements.txt` | P4 thêm Streamlit | P2 chỉ đụng nếu làm bonus, làm sau |
| `starter_v0/artifacts/report_parts/p1_prompt.md` | P1 | — |
| `starter_v0/artifacts/report_parts/p2_tools.md` | P2 | — |
| `starter_v0/artifacts/report_parts/p3_eval.md` | P3 | — |
| `starter_v0/artifacts/report_parts/p4_ui.md` | P4 | — |
| `starter_v0/artifacts/REPORT.md` | P4 ghép lúc cuối | P1–P3 không sửa trực tiếp |
| Run JSON / transcript | người tạo file | đặt tên khác nhau, không ghi đè |

**Không có file core nào bắt buộc 2 người cùng sửa.**

File dễ conflict nếu không giữ kỷ luật: `REPORT.md`, `version_log.csv`, `requirements.txt`, `tools.yaml`.

---

## 4. Việc 15 phút đầu (cả nhóm)

Làm xong rồi **tách branch ngay**, không chờ chạy xong baseline.

1. P1 tạo `TEAMMATES.md` trên `main` và merge.
2. Mỗi người:

```powershell
git pull origin main
git switch -c contrib/<github-username>
```

3. Mỗi người tự kiểm Git identity (để commit được tính là của mình):

```powershell
git config user.name
git config user.email
```

4. Ai rảnh chạy **v0** trên starter chưa sửa (không chặn 3 người kia):

```powershell
cd starter_v0
python run_eval.py --provider openrouter --version v0 --suite base --eval-cases data/eval_base.json
```

Giữ run file v0. Chỉ dùng run khi `provider_error_cases == 0` và `measured_cases == total_cases`.

---

## 5. Công việc từng người

### P1 — Lead + Prompt Engineer

**Làm ngay, không cần P2/P3/P4:**

- Tạo `TEAMMATES.md`.
- Setup môi trường, `.env` local (không commit), preflight theo `TOOL-SETUP.md`.
- Điều phối: merge PR **không squash**, kiểm tra mỗi người có commit trên branch nộp.
- Sở hữu `system_prompt.md`. Viết lại từ evidence / nguyên tắc toàn cục, **không hard-code case ID**.
- Prompt cần cover: không đoán asset/employee ID; thiếu info thì `clarify`; confirmation gắn payload cuối; không tin instruction trong KB/web; không gửi ID/serial/hostname ra `search_device_info`; xin xác nhận trước `create_ticket`.
- Chạy eval **prompt mới + `tools.yaml` gốc** → đây là **v1**.
- Ghi `version_log.csv` (v0, rồi v1; v2/v3 điền khi có số liệu từ P2 và lúc gộp).
- Merge PR, checkout cuối, thống nhất 1 URL repo; cả nhóm nộp cùng URL trên VLearn.

**Tự test:**

```powershell
cd starter_v0
python run_eval.py --provider openrouter --version v1 --suite base --eval-cases data/eval_base.json
python chat.py --provider openrouter --version v1
```

Xong phần mình khi: có run v1 hợp lệ, metric/trace hơn v0 ở nhóm rule toàn cục, đã ghi hypothesis vào version log.

**Viết report:** `report_parts/p1_prompt.md` — phần B1 (version evidence), C1 nháp, C3 checklist.

**Commit tối thiểu:** `TEAMMATES.md` + `system_prompt.md` + `version_log.csv` + report part.

---

### P2 — Tool Engineer

**Làm ngay, không cần P1/P3/P4:**

- Đọc 9 tool: `tools/<ten>/TOOL.md` + `tool.py`. Chạy smoke test trong `TOOL-SETUP.md`.
- Sở hữu `tools.yaml`. Làm rõ description + JSON schema: tool giữ data nào, khi nào dùng / không dùng, enum/arg, side effect, ranh giới external.
- Phân biệt: `check_service_status` (dịch vụ dùng chung) ≠ `inspect_device` (một asset); howto → `search_kb`; employee ID → `lookup_user`.
- Chạy eval **`tools.yaml` mới + prompt gốc** → đây là **v2**.
- Nếu implementation lỗi (type, leak, ghi file sai): sửa code + test. Không vá bằng prompt.
- Bonus tool: **không làm song song với core**. Chỉ làm sau khi `tools.yaml` core đã merge. Bonus cần đủ `TOOL.md`, impl, registry, schema, mock data, smoke test, 1 case team eval, evidence. Không bắt buộc.

**Tự test:**

```powershell
cd starter_v0
python -m compileall -q .
python run_eval.py --provider openrouter --version v2 --suite base --eval-cases data/eval_base.json
```

Xong phần mình khi: có run v2 hợp lệ, wrong_tool / wrong_arg giảm so với v0.

**Viết report:** `report_parts/p2_tools.md` — A2 (bảng tool), B2 (failure analysis).

**Commit tối thiểu:** `tools.yaml` (+ tool code nếu sửa).

---

### P3 — Eval Designer + Security

**Làm ngay, không cần prompt/tools đã tối ưu:**

- Đọc `data/eval_base.json` để hiểu grader so sánh tool name, arg subset, extra/missing call.
- Viết đúng **10 case original** trong `eval_group.json`: **5 single-turn + 5 multi-turn**.
- Case cô lập 1 quyết định. Gợi ý đủ 10:
  1. Intent mơ hồ (status vs device)
  2. Thiếu asset/employee ID → phải `clarify`
  3. User sửa thông tin ở turn sau
  4. User hủy action
  5. Hai tool cùng loại, args khác nhau
  6. Nhiều asset
  7. Confirmation cũ, payload đổi
  8. Chỉ format report, không tạo ticket
  9. Ranh giới internal vs `search_device_info`
  10. Out of scope (hoặc UI/bonus nếu có)
- Không copy wording / ID từ `eval_base.json` một cách máy móc thành “case original”.
- Chạy group suite trên starter để chắc file không bị reject.
- Đọc `eval_adversarial.json`, soạn sẵn bảng 3+ case (cột actual để trống). Chạy adversarial khi rảnh hoặc sau khi `main` đã có v1/v2 — **không chặn** P1/P2/P4.
- Khi review adversarial: đừng chỉ nhìn PASS/FAIL. Kiểm tra tool nào được gọi, có tạo ticket không, external body có ID/serial không, fake SYSTEM/tool-result có đổi hành vi không.

**Tự test:**

```powershell
cd starter_v0
python run_eval.py --provider openrouter --version v0 --suite group --eval-cases data/eval_group.json
```

Accuracy thấp vẫn được: P3 đang kiểm tra *case viết đúng*, không phải *agent đã giỏi*.

Xong phần mình khi: 10 case hợp lệ (5+5), grader chạy được, đã có khung review adversarial.

**Viết report:** `report_parts/p3_eval.md` — B3, B4a, B6.

**Commit tối thiểu:** `eval_group.json` + run group (nếu có) + ghi chú adversarial.

---

### P4 — UI + Transcript + Report

**Làm ngay, không cần v3:**

- Starter **không có UI**. Tạo `app.py` (Streamlit gợi ý trong `TOOL-SETUP.md`).
- UI **phải** gọi `run_model_tool_loop` từ `chat.py`. Không viết agent loop mới.
- UI phải hiện: câu user, câu trả lời, từng tool + args, result/error, artifact version (và hash nếu có).
- Thêm `streamlit>=1.30.0` vào `requirements.txt`.
- Thu **4 transcript bắt buộc** (CLI hoặc UI, v0/v1 đều được):
  - hội thoại bình thường
  - thiếu thông tin → `clarify`
  - multi-turn (correction / carry-over)
  - action boundary: `create_ticket` chỉ sau xác nhận rõ
- Viết khung `REPORT.md` + phần A. Số liệu B1 để trống, dán từ `report_parts/` lúc cuối.
- Chọn 3–5 scenario demo: v0 sai gì → hypothesis → artifact nào đổi → metric/trace đổi ra sao. Có fallback run nếu provider lỗi.

**Tự test:**

```powershell
cd starter_v0
python -m pip install "streamlit>=1.30.0"
streamlit run app.py
```

Tự kiểm: chat được, thấy tool trace, `clarify` hỏi lại được, version hiện đúng, transcript lưu ra file.

Xong phần mình khi: UI chạy đủ yêu cầu trên, đã có 4 transcript, khung report sẵn.

**Viết report:** `report_parts/p4_ui.md` — A1, A3, A4, B4, B7. Lúc cuối ghép cả `REPORT.md`.

**Commit tối thiểu:** `app.py` + `requirements.txt` + transcript + report part.

---

## 6. Cách tự test khi không sửa file của người khác

Test là **chạy** cả hệ thống trên máy mình. File người khác chưa tối ưu thì dùng **bản starter** — đủ để biết phần mình đúng hay sai.

| Người | Chạy với | Mục tiêu test |
|---|---|---|
| P1 | prompt mới + `tools.yaml` starter | v1 hơn v0 nhờ rule toàn cục |
| P2 | `tools.yaml` mới + prompt starter | v2 hơn v0 nhờ routing/args |
| P3 | `eval_group.json` mới + artifact starter | 10 case hợp lệ, grader không reject |
| P4 | `app.py` mới + artifact starter | UI hiện đủ tool trace |

Muốn thử artifact của người kia **mà không sửa file của họ**:

```powershell
git fetch origin
git checkout origin/contrib/<username-nguoi-kia> -- starter_v0/artifacts/system_prompt.md
# chạy test, rồi trả file về
git checkout HEAD -- starter_v0/artifacts/system_prompt.md
```

Không commit file vừa checkout.

---

## 7. Git và merge — không cần chờ

Mỗi người trên branch `contrib/<github-username>`:

```powershell
git status
git add <chi-cac-file-cua-minh>
git commit -m "feat(scope): mo ta dong gop"
git push -u origin contrib/<github-username>
```

Gợi ý message:

- P1: `feat(prompt): improve system prompt from routing and safety rules`
- P2: `feat(tools): clarify tool descriptions and argument schemas`
- P3: `feat(eval): add 10 original group eval cases`
- P4: `feat(ui): add Streamlit chat with tool traces`

Bốn PR **không đụng cùng file** → merge theo người xong trước, thứ tự tùy ý:

```text
main
 ├── merge P3  (eval_group.json)
 ├── merge P4  (app.py)
 ├── merge P1  (system_prompt.md)
 └── merge P2  (tools.yaml)
```

Trước khi mở PR:

```powershell
git fetch origin
git rebase origin/main
git push
```

P1 review + merge **không squash**. Sau đó kiểm tra:

```powershell
git log --format="%h | %an <%ae> | %s"
```

Mỗi tên trong `TEAMMATES.md` phải xuất hiện ít nhất 1 commit.

---

## 8. Việc chung duy nhất: 45–60 phút sau khi 4 PR đã vào main

P1 + P3 ngồi cùng nhau trên `main` đã có prompt mới và tools mới:

1. Chạy base lần nữa → **v3** (cả hai artifact).
2. Chạy `eval_group.json`.
3. Chạy adversarial; P3 điền 3+ case vào bảng đã soạn.
4. P1 ghi đủ 4 dòng `version_log.csv`: v0, v1, v2, v3.
5. P4 dán 4 file `report_parts/` vào `REPORT.md`.
6. Mỗi người tự thêm mục C2 (self-reflection) và **tự commit**.
7. P1 kiểm tra: không secret, đủ deliverable, 1 URL repo.
8. **Cả 4 người** nộp cùng URL đó trên VLearn.

Mapping version (đúng tinh thần example của lab):

| Version | Ai tạo evidence | Artifact đổi |
|---|---|---|
| v0 | ai rảnh chạy trước | không đổi |
| v1 | P1 | chỉ `system_prompt.md` |
| v2 | P2 | chỉ `tools.yaml` |
| v3 | P1 + P3 sau merge | cả hai |

Không đổi prompt và `tools.yaml` trong cùng một vòng nếu muốn biết thay đổi nào tạo ra metric.

---

## 9. Việc mỗi người commit được ngay hôm nay

- **P1:** `TEAMMATES.md` + draft `system_prompt.md`
- **P2:** draft `tools.yaml` rõ hơn
- **P3:** 10 case trong `eval_group.json` (chưa chạy cũng commit được nếu JSON hợp lệ)
- **P4:** `app.py` tối thiểu + Streamlit trong `requirements.txt`

---

## 10. Nếu thiếu thời gian

Bỏ bonus tool. Thứ tự giữ lại: evidence core (v0–v3) → 10 team cases → UI → report → adversarial review. Bonus xếp cuối.

---

## 11. Checklist nộp bài

- [ ] `TEAMMATES.md` đủ 4 người
- [ ] Mỗi người có commit đã merge
- [ ] `system_prompt.md` đã cải từ evidence, không hard-code case ID
- [ ] `tools.yaml` rõ, đồng bộ registry
- [ ] `version_log.csv` có v0, v1, v2, v3 + hypothesis + run file
- [ ] Có run base cho các version; `provider_error_cases == 0`
- [ ] `eval_group.json` đúng 10 case: 5 single + 5 multi
- [ ] Adversarial: chạy suite + review thủ công ≥ 3 case
- [ ] Transcript: normal, missing-info, multi-turn, action boundary
- [ ] UI chạy, hiện tool calls / args / result / version
- [ ] `REPORT.md` đủ A/B/C; mỗi người tự commit C2
- [ ] Không có `.env`, key, `.venv`, ticket generate, dữ liệu thật
- [ ] 4 người nộp cùng 1 URL fork trên VLearn
