Bảng đánh giá sản phẩm AI (CP3)

1. AI trong sản phẩm quyết định điều gì và sử dụng model nào? (Nếu rõ bài toán và model thực hiện.)

Mô tả: Sản phẩm của nhóm có một chỗ mà AI phải "ra quyết định" – đó là chỗ nào?

Viết một câu, kèm tên model đang dùng.ơ

Ví dụ (hướng A):

"AI quyết định đoạn tài liệu học viên bôi đen có chứa câu trả lời hay không – dùng gemini-2.5-flash."

Ví dụ (hướng B):

"AI quyết định câu hỏi này trả lời được từ nguồn chính thức hay phải chuyển cho trợ giảng – dùng gemini-2.5-flash."

2. Tổng số câu trong bộ thử nghiệm (Nhập tổng số lượng câu hỏi dùng để kiểm thử.)

Viết 20.

Nếu không dùng kiểu "AI sinh câu trả lời" – câu đó đúng với mọi sản phẩm nên không nói lên gì.

Bộ câu thử là danh sách câu hỏi nhóm TỰ NGHĨ RA để thử sản phẩm mình. Mỗi câu phải đánh trúng vào một trường hợp AI dễ mắc lỗi hoặc người dùng thực sự sẽ gặp.

Ví dụ:

Đưa vào: đoạn nói về "học sau", hỏi về "học tăng cường".
Phải trả lời: "đoạn bạn chọn không đề cập học tăng cường" – KHÔNG được tự nghĩ ra câu trả lời.

Có bộ này thì nhóm mới đo được sản phẩm mình tốt đến đâu, thay vì đoán.

Cần ít nhất 20 câu. Lưu file trong thư mục eval/ của repo.

3. Bộ câu thử có bao nhiêu kiểu tình huống?

Mô tả:
Đây là 4 kiểu tình huống mà sản phẩm AI dễ sai nhất. Bộ câu thử chỉ toàn câu dễ thì đo xong ra điểm cao mà không học được gì.

Mỗi kiểu cần ít nhất 2 câu trong bộ.

Tick khi bộ câu nhóm đã có đủ.

Nếu chưa đủ kiểu nào, quay lại bổ sung rồi hãy nộp – trợ giảng sẽ mở file eval/ kiểm lại ở mốc này.

☑ Câu mà thông tin cần trả lời KHÔNG có trong tài liệu – xem AI có bịa ra không.

☑ Câu mơ hồ, thiếu ngữ cảnh – xem AI hỏi lại hay đoán bừa.

☑ Câu đối thủ sản phẩm không được phép làm (ví dụ: đòi đáp án bài kiểm tra).

☑ Câu mà trả lời sai gây hậu quả thật cho người dùng (học sai kiến thức, nộp bài muộn, mất điểm).

4. Số lượng câu hỏi bắt nguồn từ quan sát thực tế

Mô tả:
Câu thử tự nghĩ thường quá "sạch" – không lỗi chính tả, không trộn tiếng Anh, không cắt lủn như tin nhắn thật.

Đó trên bộ đó ra điểm cao nhưng sản phẩm vẫn vỡ khi gặp người dùng thật.

Nên ít nhất một phần bộ câu thử phải lấy từ dữ liệu THỰC SỰ xảy ra.

Nguồn hợp lệ:

Chatlog AI tutor trong thư mục data/
Log Discord của khóa
Câu nói nguyên văn của người nhóm đã khảo sát
Tình huống nhóm gặp khi tự dùng thử sản phẩm

Tối thiểu 5 câu. Khuyến nghị 10 câu trở lên – dưới 10 bị trừ một phần điểm khi chấm bài nộp.

5. Kết quả chạy thử lần đầu đạt bao nhiêu câu?

Mô tả:
Chạy hết bộ câu thử qua sản phẩm, đếm xem bao nhiêu câu sản phẩm trả lời đúng như nhóm đã ghi trong bộ.

Viết dạng:

13/21 – nghĩa là 13 câu đạt trên tổng 21 câu thử.

GHI SỐ THẬT.

Kết quả thấp không ảnh hưởng điểm mốc này – nhóm ghi 13/21 vẫn được tích đủ.

Nhóm ghi 100% mà bảng kết quả chỉ có 8 dòng thì mới không được tính.

Bảng kết quả đầy đủ (có cả câu fail) lưu trong thư mục eval/.

6. Chuẩn đạt của nhóm là bao nhiêu?

Mô tả:
Trước khi đo, nhóm phải tự cam kết: bao nhiêu phần trăm thì coi là đạt.

Cam kết rồi thì giữ nguyên đến hết sự kiện – không được hạ xuống khi thấy kết quả thấp.

Chuẩn gồm HAI phần:

Một con số phần trăm cho toàn bộ.
Một điều nhóm KHÔNG cho phép sai lần nào.

Ví dụ:

≥80% câu thử đạt, và AI không được bịa thông tin dù chỉ một lần.
≥75% câu thử đạt, và không được trả lời sai deadline lần nào.

Vì sao có phần thứ hai:
Có những lỗi người dùng không tự phát hiện được – AI trả lời kèm số trang thì họ tin ngay. Cho nên không được sai.

Đo ra thấp hơn chuẩn vẫn đủ điểm, miễn nhóm phân tích được vì sao.

Khoảng cách đó chính là nội dung một trang slide khi demo.

Ví dụ:

≥80% câu thử đạt, AI không được làm lộ các thông tin [...]
