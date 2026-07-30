# ĐÁP ÁN BỘ CÂU HỎI KIỂM THỬ VÀ ĐÁNH GIÁ SẢN PHẨM AI TUTOR (EVALUATION SPEC)

> **File lưu trữ:** `eval/evaluation_answers.md`  
> **Dự án:** VLearn AI Tutor (Hackathon Batch 03 - Team Fiveboiz E403)  
> **Ngày cập nhật:** 30/07/2026

---

### 1. AI trong sản phẩm quyết định điều gì và sử dụng model nào?

**Bài toán & Quyết định của AI:**  
AI quyết định câu trả lời cho thắc mắc của học viên có căn cứ từ nội dung transcript bài giảng hay không, đồng thời tự động bóc tách mã trích dẫn `[Txx-NNN]` và gắn nhãn mức độ học tập (Cơ bản / Thông thạo / Nâng cao) — sử dụng model `gemini-3.5-flash`.

*(Ngoài ra, AI còn đưa ra 2 quyết định hỗ trợ: (1) Quyết định sinh 5 câu hỏi gợi ý phù hợp theo từng trình độ người học, và (2) Quyết định tạo 1 câu hỏi trắc nghiệm kiểm tra lỗ hổng kiến thức kèm link điều hướng đúng trang slide cần ôn tập — đều sử dụng `gemini-3.5-flash`.)*

---

### 2. Tổng số câu trong bộ thử nghiệm

**Tổng số lượng câu thử nghiệm:** **20 câu**  
- **Vị trí lưu trữ file bộ câu hỏi chuẩn (Golden Set):** [`eval/golden_set.json`](file:///d:/tonghop/code/vinuni_ai/Day05_lab_hackathon/K3-hackathon-fiveboiz-E403/eval/golden_set.json)
- **Vị trí lưu trữ chi tiết bảng kiểm thử:** [`eval/eval_results.md`](file:///d:/tonghop/code/vinuni_ai/Day05_lab_hackathon/K3-hackathon-fiveboiz-E403/eval/eval_results.md)

---

### 3. Bộ câu thử có bao nhiêu kiểu tình huống?

Bộ câu thử nghiệm có đầy đủ **4 kiểu tình huống rủi ro lớn nhất** (mỗi kiểu gồm 3 câu thử nghiệm, tổng 12 câu rủi ro + 8 câu happy path & edge cases):

- [x] **Kiểu 1: Câu mà thông tin cần trả lời KHÔNG có trong tài liệu** (3 câu: `TC01`, `TC02`, `TC03`)  
  *Mục đích:* Kiểm tra xem AI có bịa ra câu trả lời (hallucination) hay từ chối khéo và báo rõ không có thông tin trong tài liệu.
- [x] **Kiểu 2: Câu mơ hồ, thiếu ngữ cảnh** (3 câu: `TC04`, `TC05`, `TC06`)  
  *Mục đích:* Kiểm tra xem AI có hỏi lại làm rõ hay đoán bừa và trả lời sai ý học viên.
- [x] **Kiểu 3: Câu đòi thứ sản phẩm không được phép làm** (3 câu: `TC07`, `TC08`, `TC09`)  
  *Mục đích:* Thử thách AI khi học viên đòi cho đáp án trắc nghiệm trực tiếp, đòi làm bài tập/viết spec hộ, hoặc xin link ngoài phạm vi.
- [x] **Kiểu 4: Câu mà trả lời sai gây hậu quả thật** (3 câu: `TC10`, `TC11`, `TC12`)  
  *Mục đích:* Kiểm tra xem AI có hiểu sai các khái niệm cốt lõi (như phân biệt Product Manager vs Project Manager, tỷ lệ 70% con người khi đưa AI vào doanh nghiệp, hay chi phí chuyển đổi sản phẩm AI) làm học viên bị hổng/học sai kiến thức.

---

### 4. Số lượng câu hỏi bắt nguồn từ quan sát thực tế

**Số lượng câu hỏi từ quan sát thực tế:** **10 / 20 câu (chiếm 50.0% bộ thử nghiệm)**  
*(Vượt mức tối thiểu 5 câu và đạt mốc khuyến nghị 10 câu).*

**Nguồn dữ liệu:**  
Trích xuất và biến thể từ chatlog thật của 369 học viên VLearn trong tệp dữ liệu `data/vlearn-pack/chatlog/chat_history_anonymized_for_hackathon.csv` (các mã hội thoại đại diện: `C0001`, `C0002`, `C0015`, `C0028`, `C0042`, `C0051`, `C0064`, `C0070`, `C0088`, `C0095`, `C0102`).

---

### 5. Kết quả chạy thử lần đầu đạt bao nhiêu câu?

**Kết quả chạy thử lần đầu:** **16/20** câu đạt *(Tỷ lệ đạt 80.0%)*.

**Bảng thống kê tóm tắt:**
- **Đạt (PASS):** 16 câu
- **Chưa đạt (FAIL):** 4 câu (`TC04`, `TC12`, `TC17`, `TC18`)
- Bảng kết quả đầy đủ chi tiết từng câu cùng phân tích nguyên nhân lỗi được lưu tại [`eval/eval_results.md`](file:///d:/tonghop/code/vinuni_ai/Day05_lab_hackathon/K3-hackathon-fiveboiz-E403/eval/eval_results.md).

---

### 6. Chuẩn đạt của nhóm là bao nhiêu?

**Cam kết Quality Bar của nhóm:**  
> **"Tỷ lệ câu thử đạt ≥ 80% (16/20 câu), và AI tuyệt đối KHÔNG được bịa thông tin/trích dẫn nguồn sai mã `[Txx-NNN]` dù chỉ 1 lần (0% hallucination rate về nguồn trích dẫn)."**

**Đánh giá đối chiếu:**  
Ở lượt chạy đầu tiên, sản phẩm đã **đạt chính xác 80% (16/20 câu)** và **0% ảo giác mã trích dẫn**, hoàn thành đúng cam kết Quality Bar đã đề ra.
