# Evaluation — Daily Draft Assistant

## AI decision

> AI quyet dinh thong tin nguoi dung nhap co du ro de dua vao `/yesterday`, `/today`, `/blocked` hay phai hoi lai/giu placeholder; AI khong duoc tu tao cong viec hoac che di blocker.

Ghi model dang dung trong prototype o day: `[TEN_MODEL_THAT]`.

## Golden set

- File: `daily-draft-golden-set.csv`
- So case: 20 (12 tao ban nhap, 8 scheduling)
- Bon lop cho kho: thieu thong tin (DD-04, DD-05); mo ho (DD-06, DD-11); ngoai pham vi/gia mao (DD-10, DD-12); hau qua cao (DD-08, DS-05, DS-06).

## Quality bar (chot truoc khi do)

> Dat khi >=85% tong 20 case pass; va 100% case khong du thong tin/mo ho khong tu bịa cong viec, 100% daily duoc gui dung kenh team rieng luc 07:00 Asia/Bangkok (+/- 1 phut) va khong gui trung.

## Mock Run 01 — KHONG PHAI KET QUA THAT

- File: `daily-draft-run-mock-01.csv`
- Ket qua mo phong: 16/20 = 80.0% (chua dat quality bar).
- Fail: DD-04 (tu dien blocked), DD-08 (giu task mo ho), DS-04 (khong xu ly offline/catch-up), DS-08 (mat `/blocked` khi dai).

## Viec can lam truoc khi nop

1. Chot chinh xac han Daily: `12:00` trua hay `00:00` dem; luu timezone `Asia/Bangkok` trong config.
2. Chay tung case tren Discord server test va tao `daily-draft-run-01.csv` theo dung schema cua file mock.
3. Dan message link/timestamp that, ten nguoi cham, ca case fail va nguyen nhan.
4. Sua mot failure uu tien, chay lai toan bo 20 case, luu `run-02`.

## Ve bang chung tu thuc te

5 case dau co nhan `user_workflow_description` chi dua tren mo ta hien tai cua ban; chung khong tu dong thanh 5 quan sat doc lap. Truoc khi nop, them it nhat 5 mau da duoc phep dung tu daily cua thanh vien/phan hoi survey (ma hoa, khong commit noi dung nhay cam) va doi `source_origin` thanh ma mau that.
