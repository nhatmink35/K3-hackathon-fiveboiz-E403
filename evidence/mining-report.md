# CP4 Evidence — Mining chatlog VLearn

## Nguồn và phạm vi

- File: `data/vlearn-pack/chatlog/chat_history_anonymized_for_hackathon.csv`
- Tổng số dòng: **2,522**
- Student messages: **1,261**
- Tutor messages/turn hoàn chỉnh: **1,261**
- Người dùng ẩn danh: **369**
- Hội thoại: **585**

## Phương pháp có thể kiểm lại

1. Đọc CSV bằng UTF-8 và tách dòng theo `role`.
2. Mẫu số của các tỷ lệ là toàn bộ tutor messages.
3. Field JSON được xem là rỗng khi giá trị trống hoặc parse thành `[]`.
4. Check question chỉ được tính khi `asked_check_question=True`.
5. Rating được đếm trực tiếp theo `up`/`down`; không suy diễn các dòng null.
6. Ví dụ định tính chọn từ các turn có `rating=down`, giữ mã turn để phúc khảo.

Chạy lại:

```powershell
python evidence/mine_chatlog.py
```

## Kết quả

| Pattern | Số lượt | Tỷ lệ trên 1.261 lượt tutor | Quy tắc đếm |
|---|---:|---:|---|
| Tutor không sinh câu hỏi gợi ý tiếp theo | 1,261 | 100.0% | `follow_ups` rỗng hoặc `[]` |
| Tutor không ghi nhận misconception | 1,261 | 100.0% | `misconceptions` rỗng hoặc `[]` |
| Tutor không có citation | 582 | 46.2% | `citations` rỗng hoặc `[]` |
| Tutor có hỏi kiểm tra hiểu bài | 3 | 0.2% | `asked_check_question=True` |
| Tutor nhận rating down | 37 | 2.9% | `rating=down` |
| Tutor nhận rating up | 33 | 2.6% | `rating=up` |

## Năm ví dụ có mã nguồn

> Các quote dưới đây lấy từ data pack đã ẩn danh. Không dùng để suy ngược danh tính.

| Turn ID | Câu hỏi học viên (trích ngắn nguyên văn) | Phản hồi tutor (trích ngắn nguyên văn) | Signal |
|---|---|---|---|
| T0769 | “(Trang 4, đoạn được chọn: "giải thích nghĩa chi tiết của trang 4") giải thích nghĩa chi tiết của tr…” | “Chào bạn, rất xin lỗi vì hiện tại hệ thống tìm kiếm không tìm thấy nội dung cụ thể cho trang 4 tron…” | rating=down; citations=[]; follow_ups=[] |
| T0408 | “(Trang 14, đoạn được chọn: "tóm tắt các chủ đề chính của slide day05-lecture-slides-batch03.pdf này…” | “Rất tiếc, tôi không thể tìm thấy tệp tin hoặc nội dung chi tiết của `day05-lecture-slides-batch03.p…” | rating=down; citations=[]; follow_ups=[] |
| T1258 | “(Trang 33, đoạn được chọn: "tóm tắt slide này") tóm tắt slide này” | “Rất tiếc là tôi đã tra cứu trong tài liệu nhưng chưa tìm thấy nội dung cụ thể của **Trang 33**. Kết…” | rating=down; citations=[]; follow_ups=[] |
| T0776 | “(Trang 27, đoạn được chọn: "giải thích và tóm tắt nội dung học hôm này") giải thích và tóm tắt nội …” | “Xin lỗi bạn, tôi không tìm thấy phần tóm tắt tổng quát trong nội dung bài giảng của ngày hôm nay. B…” | rating=down; citations=[]; follow_ups=[] |
| T0519 | “(Trang 46, đoạn được chọn: "Tóm tắt slide pdf day2 cho tôi") Tóm tắt slide pdf day2 cho tôi” | “Rất tiếc, tôi không thể truy cập trực tiếp vào tệp PDF của buổi học để tóm tắt cho bạn. Nếu bạn có …” | rating=down; citations=[]; follow_ups=[] |

## Kết luận evidence

- **1,261/1,261 (100.0%)** lượt tutor không có follow-up: pain “học viên không có bước học tiếp theo” tồn tại trên toàn bộ mẫu.
- Chỉ **3/1,261 (0.2%)** lượt tutor chủ động hỏi để kiểm tra hiểu bài: gần như không có signal để thích ứng độ khó.
- **582/1,261 (46.2%)** lượt không có citation: groundedness vẫn là rủi ro quan trọng, nhưng prototype chọn lát cắt follow-up thích ứng và giữ citation như điều kiện an toàn.
- Có **37** rating down; năm ví dụ cho thấy nhiều case người học yêu cầu giải thích/tóm tắt nhưng tutor không truy xuất được nguồn và không đưa ra bước phục hồi đủ hữu ích.

## Giới hạn

- Rating chỉ xuất hiện trên một phần nhỏ lượt chat, không dùng để ước lượng mức hài lòng toàn bộ người học.
- `follow_ups=[]` chứng minh feature chưa được sử dụng, không tự nó chứng minh mọi học viên đều muốn follow-up.
- Mining chứng minh pain tồn tại; validation CP5 phải kiểm tra người dùng có thấy gợi ý thích ứng hữu ích hay không.
