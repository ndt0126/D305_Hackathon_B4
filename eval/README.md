# eval/ — Golden set + kết quả các lượt chạy

Chấm ở **R4 · Kiểm thử (15 điểm)** — khối điểm to nhất cùng với R1 và R2.

## Cần có trước CP3 (16:00 N1)

- [ ] `golden-set.md` (hoặc `.csv`) — **≥20 case nhóm tự xây**, cơ cấu bắt buộc:
  - ≥2 case cho **mỗi** lớp chỗ khó ①②③④ (8 case)
  - 8-10 case thường
  - 2-4 case hiếm
  - trong đó **≥10 case lấy hoặc phát triển từ chat thật** (ghi mã đoạn, **không dán nguyên văn dài** — quy định bảo mật data)
- [ ] `run-01.md` — bảng kết quả chạy **trọn bộ**, đủ **mọi** case kể cả case fail, có **%**, đối chiếu quality bar.

## Nhịp lặp (guide §4.1)

`chạy trọn bộ → bảng % → chọn MỘT failure đau nhất → sửa → chạy lại TRỌN BỘ`

Mỗi lượt một file `run-NN.md`. Sửa prompt chỗ này thường làm vỡ chỗ kia — nên bắt buộc chạy lại trọn bộ.

## Ba cái mất điểm oan

1. Golden set toàn case dễ → TA kiểm tra độ phủ 4 lớp.
2. Chấm "đạt" theo cảm tính giữa chừng → quay lại định nghĩa trong `spec.md` §7; nếu định nghĩa mơ hồ thì sửa **định nghĩa** và ghi vào Changelog §9.
3. **Hạ quality bar khi thấy kết quả thấp** → bar đã chốt lúc 23:59 N1. Không đạt mà phân tích được nguyên nhân thì **vẫn đủ điểm**; sửa số thì **mất trắng**.

## Định nghĩa "đạt" phải kiểm chứng được

Hai thành viên chấm độc lập cùng 5 output → lệch nhau = định nghĩa mơ hồ, viết lại. Trong nhóm còn chấm khác nhau thì người ngoài nhóm chấm chắc chắn khác.
