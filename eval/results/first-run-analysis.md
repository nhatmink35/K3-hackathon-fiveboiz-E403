# CP3 — Phân tích lượt chạy đầu

## Kết quả

- Run ID: `20260730T081816Z`
- Model: `gemini-3.5-flash`
- Case đã chạy: 20/20
- Đạt: 2
- Chưa đạt: 18
- Pass rate: **10%**
- Quality bar đã chốt: **85%**
- Kết luận: **chưa đạt quality bar**

Không case nào bị xoá khỏi bảng kết quả. File gốc:
`run-20260730T081816Z.csv`.

## Phân loại nguyên nhân

| Nhóm nguyên nhân | Số case | Nhận định |
|---|---:|---|
| Parser chỉ đọc part đầu, trong khi Gemini trả thinking part trước JSON | 12 | Lỗi tích hợp của prototype, không phải kết luận chất lượng câu trả lời |
| Free-tier quota `429` | 3 | Lỗi hạ tầng/quota |
| Model quá tải `503` | 1 | Lỗi hạ tầng |
| Timeout | 1 | Lỗi hạ tầng |
| Case đạt | 2 | Có câu trả lời/citation theo tiêu chí |

Tổng nhóm có thể chồng lấn theo cách phân loại log; bảng CSV là nguồn sự thật cho
từng case.

## Thay đổi sau lượt 1

1. Parser bỏ qua Gemini thinking parts và đọc JSON part cuối.
2. Parser chấp nhận JSON code fence.
3. Client retry một lần cho `429`, `503` và timeout.
4. Eval runner thêm delay mặc định 5 giây giữa các case.
5. Không thay đổi golden set hoặc quality bar.

## Lượt xác minh sau sửa

Smoke run `20260730T082211Z` chạy hai case:

- GS-001: PASS — AI thật, citation `D1-P11-C01`, có 2 gợi ý.
- GS-002: FAIL — free-tier quota `429`.

Kết luận: lỗi parser đã được sửa và đường AI end-to-end hoạt động; quota của
Gemini free tier hiện chưa đủ ổn định để chạy liên tiếp toàn bộ golden set.

## Hướng xử lý tiếp

- Giữ nguyên lượt 1 để demo tính trung thực.
- Khi quota reset, chạy lại bằng cùng model/golden set với delay dài hơn; lưu
  thành run mới, không ghi đè.
- Nếu cần hoàn thành lượt đo trong thời gian ngắn, khai báo rõ việc chuyển sang
  model free có quota cao hơn và coi đó là một cấu hình eval mới.
