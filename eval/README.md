# Evaluation — Discord Learning Assistant

`golden-set.csv` co 25 case: 18 case `/ask` va 7 case Daily Schedule.

## Cach cham

- Moi case: `pass` hoac `fail`; khong cham theo cam tinh.
- Case QA-01..QA-18: chay command, copy output va doi chieu cot `pass_criteria`.
- Case SCH-01..SCH-07: ghi timestamp, channel, noi dung message va log cua bot.
- Bat buoc: QA-01..QA-05, QA-08..QA-10, QA-14, QA-17 va SCH-01..SCH-05 phai pass.

## Quality bar de dua vao spec

> Dat khi >=85% tong 25 case pass, 100% case deadline/link co citation dung, va 100% case thieu nguon/ambiguity khong bịa thong tin.

## Bang ket qua luot chay

Tao `run-01.csv` truoc khi demo voi cot: `case_id, run_at, actual_output_or_message_link, result, evaluator, failure_note`.
