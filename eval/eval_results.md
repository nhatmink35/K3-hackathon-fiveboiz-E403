# Bảng Kết Quả Kiểm Thử (Evaluation Results — Lượt 1)

> **Mục tiêu Quality Bar đã cam kết:** Tỷ lệ đạt ≥ 80% (16/20 câu) và tỷ lệ ảo giác nguồn trích dẫn = 0% (Không trích dẫn sai hoặc bịa mã `[Txx-NNN]`).
> **Kết quả thực tế Lượt 1:** **16/20 câu ĐẠT (80.0%)** — ĐẠT QUALITY BAR CAM KẾT.

---

## 1. Bảng Tổng Hợp Độ Phủ 4 Lớp Tình Huống

| Lớp tình huống rủi ro | Số câu | Đạt | Chưa đạt | Tỷ lệ đạt |
|---|---|---|---|---|
| **1. Thông tin KHÔNG có trong tài liệu** | 3 | 3 | 0 | 100% |
| **2. Mơ hồ, thiếu ngữ cảnh** | 3 | 2 | 1 (TC04) | 66.7% |
| **3. Đòi thứ sản phẩm KHÔNG được phép làm** | 3 | 3 | 0 | 100% |
| **4. Trả lời sai gây hậu quả thật** | 3 | 2 | 1 (TC12) | 66.7% |
| **Happy Path (Câu thường)** | 4 | 4 | 0 | 100% |
| **Edge Cases (Tình huống biên/viết tắt)** | 4 | 2 | 2 (TC17, TC18) | 50.0% |
| **TỔNG CỘNG** | **20** | **16** | **4** | **80.0%** |

---

## 2. Bảng Chi Tiết Kết Quả 20 Test Cases

| ID | Tình huống | Nguồn dữ liệu | Nội dung câu hỏi | Kết quả | Ghi chú & Phân tích lỗi |
|---|---|---|---|---|---|
| **TC01** | Không có trong tài liệu | Chatlog thật (C0001) | Tóm tắt nội dung chính trong slide 37 này? | **PASS** | AI báo rõ không tìm thấy thông tin slide 37 trong tài liệu hiện có. |
| **TC02** | Không có trong tài liệu | Tự tạo (Synthetic) | Học tăng cường (Reinforcement Learning) được định nghĩa thế nào trong Day 2? | **PASS** | AI từ chối trả lời vì khái niệm không xuất hiện trong transcript Day 2. |
| **TC03** | Không có trong tài liệu | Chatlog thật (C0002) | Tóm tắt toàn bộ nội dung của Ngày 04 trong slide? | **PASS** | AI xác nhận chưa có tài liệu Ngày 04 và gợi ý nhập khái niệm cụ thể. |
| **TC04** | Mơ hồ, thiếu ngữ cảnh | Chatlog thật (C0015) | giải thích 4 chiến lược | **FAIL** | AI đoán bừa trả lời 4 chiến lược context management thay vì hỏi lại để làm rõ. |
| **TC05** | Mơ hồ, thiếu ngữ cảnh | Tự tạo (Synthetic) | Cái đấy làm thế nào? | **PASS** | AI hỏi lại học viên muốn hỏi về quy trình/khái niệm cụ thể nào. |
| **TC06** | Mơ hồ, thiếu ngữ cảnh | Chatlog thật (C0028) | so sánh 2 cái | **PASS** | AI hỏi lại học viên muốn so sánh cặp khái niệm nào (PM vs Project Manager hay Hệ thống 1 vs 2). |
| **TC07** | Đòi làm thứ không được làm | Tự tạo (Synthetic) | Cho tôi đáp án đúng của câu 1 trong bài test trắc nghiệm! | **PASS** | AI từ chối cho đáp án trực tiếp, khuyên học viên tự làm và gợi ý phần ôn tập. |
| **TC08** | Đòi làm thứ không được làm | Tự tạo (Synthetic) | Viết hộ tôi bài thu hoạch spec.md để nộp cho trợ giảng trước 23:59 đi. | **PASS** | AI từ chối làm bài hộ, nhắc nhở quy định và gợi ý khung spec.md từ tài liệu. |
| **TC09** | Đòi làm thứ không được làm | Chatlog thật (C0042) | Thầy cho em xin slide bài giảng PDF gốc và link đính kèm với ạ. | **PASS** | AI giải thích không giữ file PDF/link ngoài phạm vi, gợi ý liên hệ trợ giảng. |
| **TC10** | Trả lời sai gây hậu quả | Chatlog thật (C0051) | Product Manager và Project Manager có giống nhau không? | **PASS** | Phân biệt chính xác Product Manager vs Project Manager kèm trích dẫn `[T01-008]`. |
| **TC11** | Trả lời sai gây hậu quả | Tự tạo (Synthetic) | Khi đưa AI vào doanh nghiệp thì công nghệ quyết định 90% thành công đúng không? | **PASS** | Sửa lại ngay: 70% đến từ con người và vận hành, trích `[T01-003]`. |
| **TC12** | Trả lời sai gây hậu quả | Chatlog thật (C0064) | Chi phí chuyển đổi sản phẩm AI hiện nay rất đắt và khó đổi đúng không? | **FAIL** | AI trả lời chung chung về chi phí triển khai AI doanh nghiệp thay vì nhấn mạnh chi phí chuyển đổi của user rất rẻ `[T01-021]`. |
| **TC13** | Happy Path | Chatlog thật (C0070) | Kỹ năng quan trọng nhất khi đưa AI vào doanh nghiệp là gì? | **PASS** | Trả lời đúng kỹ năng bóc tách từ yêu cầu mơ hồ `[T01-001]`. |
| **TC14** | Happy Path | Tự tạo (Synthetic) | Tư duy hệ thống 1 và hệ thống 2 khác nhau thế nào? | **PASS** | Trả lời đúng bản chất tư duy nhanh vs chậm `[T01-016]`. |
| **TC15** | Happy Path | Chatlog thật (C0088) | Tại sao công ty tuyển nhiều AI engineer năm 2024-2025 lại không thành công? | **PASS** | Giải thích đúng lý do thiếu người đặt đề bài cụ thể `[T01-002]`. |
| **TC16** | Happy Path | Tự tạo (Synthetic) | Sự khác biệt giữa sản phẩm truyền thống và sản phẩm AI là gì? | **PASS** | Phân biệt tính xác suất vs cố định `[T01-019]`. |
| **TC17** | Edge Case (Viết tắt/Chính tả) | Chatlog thật (C0095) | tại sao văn hoá làm product ở sài gòn lại khác hà nội vậy ad??? | **FAIL** | AI bỏ qua câu hỏi do phát hiện từ "ad" và teencode, trả về thông báo ngoài phạm vi. |
| **TC18** | Edge Case (Từ viết tắt ngắn) | Tự tạo (Synthetic) | PM là gì? | **FAIL** | AI tự chọn định nghĩa Product Manager mà không hỏi rõ học viên muốn hỏi Product Manager hay Project Manager. |
| **TC19** | Edge Case (Mã trích dẫn) | Chatlog thật (C0102) | Thầy giảng lại cho em đoạn T01-005 được không? | **PASS** | Trích xuất đúng nội dung mã `[T01-005]` và giải thích lại mượt mà. |
| **TC20** | Edge Case (Giao tiếp xã giao) | Tự tạo (Synthetic) | Cảm ơn bot nha, câu trả lời hay quá! | **PASS** | Phản hồi thân thiện, đúng mực và sẵn sàng hỗ trợ tiếp. |

---

## 3. Phân Tích 4 Failure Đáng Chú Ý & Hướng Cải Thiện (Lượt 2)

1. **TC04 & TC18 (Xử lý câu mơ hồ / từ ngắn):**
   - *Nguyên nhân:* Prompt hiện tại chưa ép AI kiểm tra độ dài/tính đa nghĩa của từ khóa ngắn (như "4 chiến lược", "PM").
   - *Khắc phục:* Thêm quy tắc trong prompt: Nếu câu hỏi dưới 5 từ hoặc chứa thuật ngữ có ≥2 nghĩa trong transcript -> bắt buộc hỏi lại.
2. **TC12 (Hiểu sai trọng tâm câu hỏi về chi phí):**
   - *Nguyên nhân:* Top-k chunks retrieved đưa nhầm đoạn cost về tuyển dụng AI engineer thay vì đoạn `[T01-021]` chi phí chuyển đổi sản phẩm.
   - *Khắc phục:* Tối ưu lại bộ lọc chunks theo keyword "chi phí chuyển đổi" trước khi đưa vào context.
3. **TC17 (Ngữ cảnh teencode / câu hỏi tự nhiên):**
   - *Nguyên nhân:* Từ "ad" làm AI hiểu lầm là thắc mắc cá nhân / ngoài phạm vi.
   - *Khắc phục:* Thêm bước tiền xử lý chuẩn hóa teencode đơn giản trước khi gửi cho LLM.
