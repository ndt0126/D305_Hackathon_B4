# Mock evaluation log — Run 01

> **Trang thai:** Mo phong tu golden set va hanh vi MVP ky vong; khong phai ket qua chay Discord that. Thay toan bo file nay bang `run-01.csv` co timestamp/message link that truoc khi nop bai.

## Tong ket

- Tong case: 25
- Pass: 22
- Fail: 3
- Ty le: 88.0%
- Quality bar: >=85% tong case pass; 100% case deadline/link co citation dung; 100% case thieu nguon/mo ho khong bia thong tin.
- Ket luan mock: dat nguong %; cac hard constraint deu pass trong mo phong.

## Failure can sua truoc demo

| Case | Failure | Sua de xuat |
|---|---|---|
| QA-07 | Khong nhan typo `assigment`. | Them normalisation/fuzzy matching va test lai toan bo golden set. |
| SCH-04 | Bot khoi dong muon khong co quy tac catch-up/log. | Chot: gui bu mot lan neu tre <=15 phut, neu khong bo qua va ghi log. |
| SCH-07 | Sai channel ID chua co structured error. | Validate channel khi startup, log `channel_not_found` va gui canh bao admin. |

## Cach bien thanh log that

1. Chay tung QA case bang slash command va dan output that vao cot `actual_output_or_message_link`.
2. Chay SCH case tren server test, luu message link va timestamp Discord.
3. Doi `evaluator` thanh ten nguoi cham; ghi `pass`/`fail` theo `pass_criteria` trong `golden-set.csv`.
4. Tinh lai tong pass; giu ca fail va viet phan tich nguyen nhan trong spec/slide.
