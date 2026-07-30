# D305 · Nhóm B4 — Mini Hackathon AI Batch 03 (Khoá 3)

> **Lát cắt MỘT CÂU** *(1 user · 1 việc · 1 quyết định AI · 1 kết quả)*
>
> **Một học viên**, trước khi nộp `/daily`, cần **soạn ba trường hôm-qua / hôm-nay / blocker**; hệ thống đọc tin nhắn 24h qua của chính người đó và quyết định **mỗi trường có đủ căn cứ hay không**; trả về **bản nháp ba trường, mỗi câu kèm mã tin nhắn nguồn, trường không đủ căn cứ để trống kèm lý do** — người dùng duyệt rồi copy sang `/daily`.

**Hướng:** ☑ B · Trợ lý Học viên (Discord)
**Loại:** ☑ Tính năng mới
**Mức prototype khai báo:** ☑ Mock — flow bấm được, AI thật ở lõi *(khai sai mức so với thực tế là mất điểm R5)*
**Quality bar đã chốt:** "Đạt khi **≥80%** case golden set đạt cả 3 chiều, **VÀ 0 case bịa căn cứ**" — chi tiết `spec.md` §7. Chốt từ lúc commit spec, **không đổi** sau đó.

---

## Thành viên

| # | Mã HV | Tên | Vai chính |
|---|---|---|---|
| 1 | 2A202601725 | Nguyễn Đức Trung | `TODO` |
| 2 | 2A202602039 | Nguyễn Tuấn Nam | `TODO` |
| 3 | 2A202601049 | Nguyễn Quang Vinh | Project manager · spec & báo cáo |
| 4 | 2A202601913 | Lại Duy Đông | `TODO` |
| 5 | 2A202601347 | Đinh Quang Minh | `TODO` |


## Phân công có tên — theo từng artifact được chấm

Rubric R7 đòi **README phân công có tên người cho từng phần**. Mỗi ô là một người chịu trách nhiệm chính, không để trống, không ghi "cả nhóm".

| Artifact | Mục rubric | Điểm | Người chịu trách nhiệm | Trạng thái |
|---|---|---:|---|---|
| Evidence — khảo sát ≥20 người / mining có phương pháp đếm | R1 | 6 | `TODO` | ☐ |
| Pain + bảng impact ≥3 ứng viên + ứng viên đã loại | R1 | 9 | `TODO` | ☐ |
| `spec.md` §4 — lát cắt · non-goals · automation · ≥4 nguyên tắc HAX/PAIR | R2 | 15 | `TODO` | ☐ |
| `spec.md` §5-§6 — 4 lớp chỗ khó · ≥8 kịch bản · 4 đường đi trải nghiệm | R3 | 11 | `TODO` | ☐ |
| `eval/` — golden set ≥20 case + các lượt chạy | R4 | 15 | `TODO` | ☐ |
| `codebase/` — prototype + ≥1 lời gọi AI thật, có log/trace | R5 | 8 | `TODO` | ☐ |
| `validation/` — feedback log ≥5 người + changelog | R6 | 8 | `TODO` | ☐ |
| Cấu trúc repo + README | R7 | 3 | Nguyễn Quang Vinh | ☐ |
| `demo-slides.pdf` — 6 trang theo guide §5.1 | *(vòng demo)* | — | `TODO` | ☐ |

**Ai nói phần nào ở demo** *(CP6 đòi mỗi thành viên nói ≥1 phần)*:

| Slide | Nội dung | Thời lượng | Người nói |
|---|---|---|---|
| 1 | User & Job | 45" | `TODO` |
| 2 | Vì sao chọn tính năng này | 45" | `TODO` |
| 3 | Giải pháp & demo live (1 case chuẩn + 1 case chỗ khó) | 2' | `TODO` |
| 4 | Kết quả đo vs quality bar | 45" | `TODO` |
| 5 | User thật nói gì | 45" | `TODO` |
| 6 | Nếu có thêm 1 tuần | 30" | `TODO` |

> **Vibe-coding rule:** dùng AI để build thoải mái, nhưng **không giải thích được phần có tên mình thì phần đó 0 điểm**. Kiểm ngẫu nhiên tại CP5, và giám khảo có thể hỏi lại tại CP6.

## Willing users (≥3 người ngoài nhóm, có tên — khai từ CP1)

| # | Tên / vai | Đã đồng ý thử | Đã test thật (CP5) |
|---|---|---|---|
| 1 | `TODO` | ☐ | ☐ |
| 2 | `TODO` | ☐ | ☐ |
| 3 | `TODO` | ☐ | ☐ |

---

## Cấu trúc repo

| Đường dẫn | Nội dung | Chấm ở |
|---|---|---|
| `README.md` | File này — thành viên + phân công có tên | R7 |
| `spec.md` | AI Spec §1-§9 theo template. **Hạn cứng 23:59 N1** | R1-R4 (56đ) |
| `demo-slides.pdf` | Slide 6 trang. *Chưa có — nộp trước CP6* | vòng demo |
| `codebase/` | Prototype Discord bot (discord.js). Ghi rõ phần nào mock | R5 |
| `eval/` | Golden set ≥20 case + bảng kết quả các lượt chạy | R4 |
| `validation/` | Feedback log từ vòng user test ≥5 người | R6 |
| `reflection/` | Mỗi người 1 file, chấm riêng | *(cá nhân)* |
| `evidence/` | Log khảo sát n=49 + kế hoạch đo bù | R1 |
| `artifacts/` | Đề bài · guide · template · rubric · tham khảo — bản gốc từ BTC, giữ để tra | — |
| `data/` | Data pack VLearn (chatlog + 6 transcript) — **kế thừa từ upstream** | — |

## Trạng thái checkpoint

| Mốc | Giờ (K3) | Cần show | Trạng thái |
|---|---|---|---|
| CP1 · Canvas | 10:00 N1 | Canvas 7 dòng | ✅ đã qua |
| CP2 · Bấm được | 12:00 N1 | Flow chính bấm hết được + commit đầu | ☐ |
| CP3 · AI thật + đo lượt đầu | 16:00 N1 | ≥1 AI call thật ở quyết định trung tâm + golden set ≥20 + bảng % lượt 1 | ☐ |
| CP4 · Chốt tiến độ | 17:30 N1 | Spec gần cuối · **spec.md commit hạn cứng 23:59 N1** | ☐ |
| CP5 · Xác minh + validation + dry run | 09:00 N2 | Feedback log ≥5 có tên · changelog · slide final · dry run bấm giờ | ☐ |
| CP6 · Demo | 10:00 N2 | 5' trình bày + 5' Q&A · thẻ giám khảo · mỗi người nói ≥1 phần | ☐ |

**Mỗi checkpoint nộp đúng hạn = 5 điểm, nộp muộn = 0.** Mỗi thành viên nộp riêng, cả nhóm dùng chung link repo này.

---

## `codebase/` — phần nào thật, phần nào mock

Rubric R5 đòi khai rõ. Cập nhật bảng này trước CP3.

| Thành phần | File | Thật / Mock | Ghi chú |
|---|---|---|---|
| Nhận lệnh slash `/daily` | `codebase/Handling_discord_cmd_slash.js` | `TODO` | Hiện đang `editReply` trả lại nguyên input — chưa có AI call |
| Nhận lệnh text prefix `!!` | `codebase/Handling_discord_cmd_texts.js` | `TODO` | Có embed + button edit (`!!demo`, `!!edit_yesterday`) |
| Extract lịch sử chat | `TODO` | `TODO` | |
| **Lời gọi AI ở quyết định trung tâm** | `TODO` | **phải THẬT** | Bắt buộc ≥1 call thật, log/trace giữ trong repo |
| Render report | `TODO` | `TODO` | |

> ⚠️ **Hai việc kỹ thuật cần xử trước CP2** — `codebase/` hiện chưa chạy được:
> 1. `Handling_discord_cmd_slash.js` import `./config.js`, `./Handling_Schwab_bridge.js`; `Handling_discord_cmd_texts.js` import `./glob.js`, `./T.js` — **cả 4 file đều không có trong repo**. Thiếu `package.json` và entrypoint.
> 2. `Handling_Schwab_bridge.js` và application ID hardcode `945931546966245426` là **rác từ project khác** — xoá trước khi nộp, người chấm sẽ đọc file này.

## Luật an toàn — soát trước mỗi lần push

- [ ] **Không commit token/API key.** `codebase/config.js` chứa `BOT_TOKEN_A/B/C` → đã đưa vào `.gitignore`. Kiểm tra `git log -p` xem có bị lọt ở commit trước không; đã lọt thì **reset token ở Dev Portal**, đừng chỉ xoá file.
- [ ] **Data pack:** `data/` kế thừa từ fork upstream. Quy định BTC ghi *"không commit data pack vào repo nộp bài"* → **hỏi TA xem repo fork có được miễn không**, và **giữ repo ở chế độ private** cho tới khi có xác nhận.
- [ ] Golden set trong `eval/` ghi **mã đoạn / mã hội thoại**, không dán nguyên văn dài.
- [ ] Không dùng dữ liệu thật của người thật ngoài data pack. Chat Discord dùng để mining lấy số → khi đưa vào `eval/` phải viết lại đã ẩn danh.
- [ ] Không đưa data lên công cụ free tier có thể dùng dữ liệu để train (guide §3.4).

## Backup demo

- [ ] Screenshot / video ngắn của flow chính, phòng live hỏng — chuẩn bị **trước** CP5, không phải lúc lên demo.
- [ ] Cả nhóm trả lời được 3 câu: *"Augment hay automate — vì sao?"* · *"Failure nguy hiểm nhất?"* · *"Phần bạn làm là gì?"*
