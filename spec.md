# AI SPEC — VLearn Adaptive Tutor · Nhóm Fiveboiz E403

Hướng: [x] A — VLearn
Loại: [x] Tối ưu tính năng có sẵn
Trạng thái: Mốc 1 — đã chốt phạm vi MVP; evidence và kết quả đo sẽ được bổ sung ở các mốc sau.

## §1. User & Job

- **Job executor:** Học viên đang tự học lại bài từ slide trên VLearn.
- **Core JTBD:** Khi đọc lại bài giảng và gặp một khái niệm chưa hiểu, học viên muốn được giải thích đúng với tài liệu và nhận bước học tiếp theo vừa sức để có thể tự kiểm tra mức hiểu của mình.
- **Problem statement:** Học viên có thể nhận được câu trả lời nhưng chưa biết nên hỏi gì tiếp theo, câu trả lời có bám sát bài học hay không, và nội dung tiếp theo có phù hợp với mức hiểu hiện tại hay không.
- **Evidence:** Chưa chốt ở mốc 1. Sẽ mining `data/vlearn-pack/chatlog/` ở mốc đánh giá; không commit lại data pack vào repo nộp bài.

## §2. Impact & quyết định chọn

Chưa chốt ở mốc 1. Cần mining để so sánh ít nhất ba pain: câu trả lời thiếu căn cứ, không biết hỏi gì tiếp theo, và câu trả lời lệch trình độ.

## §3. Giải pháp tương tự đã nghiên cứu

Chưa thực hiện ở mốc 1.

## §4. Thiết kế

### Lát cắt MVP — một câu

> Một học viên đang ôn lại một bài học hỏi về nội dung slide; tutor quyết định câu trả lời có đủ căn cứ và mức câu hỏi tiếp theo phù hợp với năng lực hiện tại, để học viên hiểu đúng và biết nên học gì tiếp.

### Phạm vi chức năng

1. Học viên hỏi tự do trong khung chat.
2. Tutor chỉ dùng nội dung của hai bộ slide được cung cấp làm nguồn sự thật cho MVP.
3. Câu trả lời có trích dẫn trang slide và cho phép mở đúng trang liên quan.
4. Sau mỗi câu trả lời, tutor gợi ý 2–3 câu hỏi tiếp theo ở mức phù hợp.
5. Tutor duy trì mức kiến thức theo phiên và cập nhật từ kết quả quiz ngắn:
   - **Cơ bản:** nhận biết, nhắc lại định nghĩa, thuật ngữ và ví dụ trực tiếp.
   - **Thông thạo:** giải thích quan hệ, so sánh, áp dụng vào tình huống gần với slide.
   - **Nâng cao:** phân tích điều kiện, giới hạn, đánh đổi hoặc tình huống mới có thể suy luận từ nguồn.
6. Học viên luôn có thể tự đổi mức và có thể bỏ qua câu hỏi gợi ý.

### Quy tắc cập nhật mức kiến thức

- Mức tự chọn ban đầu chỉ là giả thuyết, không phải kết luận năng lực.
- Một câu đúng không đủ để tăng mức.
- Tăng một mức khi học viên trả lời đúng ít nhất 2 câu liên tiếp ở mức hiện tại và mỗi câu kiểm tra một mục tiêu kiến thức khác nhau.
- Giữ mức khi bằng chứng chưa đủ hoặc kết quả lẫn lộn.
- Giảm một mức sau 2 câu sai liên tiếp; đồng thời gợi ý trang cần đọc lại.
- Không thay đổi quá một mức sau mỗi lượt đánh giá.
- Mỗi lần đổi mức phải hiển thị lý do ngắn và cho phép học viên hoàn tác.

### Non-goals

- Không trả lời kiến thức ngoài hai bộ slide trong MVP.
- Không chấm điểm chính thức hoặc thay thế giảng viên/TA.
- Không xây hồ sơ năng lực dài hạn giữa nhiều thiết bị hoặc nhiều khoá học.
- Không tự động tạo lộ trình học toàn khoá.
- Không dùng chatlog để huấn luyện mô hình hoặc hiển thị nội dung hội thoại thật trong sản phẩm.

### Mức prototype và automation

- **Mức nhắm tới:** Working prototype.
- **Phần thật:** truy xuất nội dung slide, lời gọi AI trả lời, trích dẫn, sinh gợi ý và quyết định mức tiếp theo.
- **Phần đơn giản hoá:** trạng thái năng lực lưu theo phiên trình duyệt; chưa có tài khoản hoặc cơ sở dữ liệu người dùng.
- **Automation:** Conditional.
- **Lý do theo cost-of-error:** Tutor được tự trả lời khi có căn cứ rõ trong slide. Khi không tìm thấy nguồn, nguồn mâu thuẫn, hoặc câu hỏi thiếu ngữ cảnh, tutor không đoán mà phải báo giới hạn hay hỏi lại. Một câu trả lời sai có thể khiến học viên học sai và mất niềm tin; việc hỏi lại tốn ít hơn việc sửa hiểu nhầm.

### Kiến trúc MVP

`index.html` → `POST /api/chat` → truy xuất top slide chunks → AI có kiểm soát
nguồn (mốc 4) → câu trả lời + citation + suggestions. Trạng thái năng lực được
lưu theo `session_id` trong RAM; không ghi hội thoại người dùng xuống đĩa.

API mốc 3 gồm health check, tạo/đọc/đổi mức phiên, tìm kiếm slide và chat. Chat
hiện trả context với trạng thái `retrieval_ready`; trường sinh câu trả lời được
để trống có chủ ý cho lời gọi AI thật ở mốc 4.

### Nguyên tắc HAX/PAIR áp dụng

| Nguyên tắc | Áp cụ thể vào prototype |
|---|---|
| G1 — Làm rõ hệ thống làm được gì | Lời chào nêu rõ tutor chỉ trả lời từ hai bộ slide và có thể gợi ý câu hỏi theo mức kiến thức. |
| G2 — Làm rõ nó làm tốt đến đâu | Mỗi câu trả lời hiển thị căn cứ trang; câu suy luận phải được gắn nhãn “Suy luận từ nguồn”. |
| G10 — Thu hẹp phạm vi khi nghi ngờ | Câu hỏi mơ hồ được hỏi lại một câu; không có đoạn nguồn đủ liên quan thì tutor nói không tìm thấy căn cứ. |
| G11 — Giải thích vì sao | Khi gợi ý đọc lại hoặc đổi mức, tutor nói rõ kết quả nào dẫn đến quyết định và liên kết đến trang liên quan. |
| G9 — Sửa dễ dàng | Học viên có thể hỏi lại, tự đổi mức hoặc hoàn tác thay đổi mức ngay trong chat. |
| PAIR — Feedback + Control | Gợi ý là tuỳ chọn; chat tự do và nút đổi mức luôn còn khả dụng. |
| PAIR — Errors + Graceful Failure | Phân biệt “không có trong tài liệu”, “câu hỏi chưa rõ” và “dịch vụ AI lỗi”; mỗi trường hợp có đường tiếp tục riêng. |

## §5. Kiểu lỗi — 4 lớp chỗ khó

| ID | Tình huống cụ thể | Lớp | Hành vi mong muốn | Nguyên tắc |
|---|---|---|---|---|
| R1 | Hỏi một khái niệm không xuất hiện trong hai bộ slide | ① Nguồn sự thật | Nói không tìm thấy căn cứ; không bịa; gợi ý câu hỏi gần nhất có trong bài | G2, G10 |
| R2 | Đoạn truy xuất có từ khoá giống câu hỏi nhưng không đủ để kết luận | ① Nguồn sự thật | Không biến mức liên quan thấp thành câu trả lời chắc chắn; báo giới hạn hoặc hỏi lại | G2, G10 |
| R3 | Học viên hỏi “cái này hoạt động thế nào?” nhưng không nêu “cái này” | ② Mơ hồ | Hỏi lại đang nói đến khái niệm hoặc trang nào | G10 |
| R4 | Một thuật ngữ xuất hiện ở nhiều ngữ cảnh trong hai bài | ② Mơ hồ | Nêu hai cách hiểu ngắn và yêu cầu chọn ngữ cảnh | G10, G9 |
| R5 | Học viên yêu cầu làm hộ bài tập hoặc đưa đáp án chấm điểm chính thức | ③ Ngoài phạm vi | Từ chối làm thay/chấm chính thức; chuyển sang gợi ý từng bước dựa trên slide | G1, PAIR Control |
| R6 | Học viên hỏi deadline, link nộp bài hoặc chính sách khoá học | ③ Ngoài phạm vi | Nói rõ slide học thuật không phải nguồn chính thức; hướng dẫn kiểm tra kênh khoá học/TA | G1, G10 |
| R7 | Tutor nhầm “Cơ bản” thành “Nâng cao” chỉ vì một câu đúng | ④ Đặc thù domain | Áp quy tắc tối thiểu 2 bằng chứng khác nhau; không nhảy quá một mức | G11, G13/G14 |
| R8 | Câu gợi ý mức nâng cao đòi kiến thức không thể suy ra từ slide | ④ Đặc thù domain | Loại câu không truy vết được về nguồn; hạ độ khó hoặc gắn rõ câu mở rộng ngoài phạm vi | G2, G10 |
| R9 | Hai trang slide diễn đạt khác nhau hoặc có vẻ mâu thuẫn | ① Nguồn sự thật | Trình bày cả hai trích dẫn và nói rõ chưa thể kết luận thay vì tự hoà giải | G2, G11 |
| R10 | API AI hoặc truy xuất tài liệu bị lỗi | Failure | Giữ nguyên câu hỏi, báo lỗi kỹ thuật, cho phép thử lại; không hiển thị câu trả lời hardcode như kết quả AI | PAIR Graceful Failure |

## §6. Bốn đường đi của trải nghiệm

- **Happy path:** Học viên hỏi rõ → tìm được đoạn nguồn → trả lời ngắn đúng mức kèm trang → gợi ý 2–3 câu tiếp → quiz → cập nhật hoặc giữ mức có lý do.
- **Low-confidence:** Có nguồn gần đúng nhưng chưa đủ → tutor nói điều đã xác định được và hỏi một câu làm rõ; chưa cập nhật mức.
- **Failure/không căn cứ:** Không có nguồn hoặc dịch vụ lỗi → tutor nêu đúng loại lỗi, không tạo kiến thức thay thế, cho phép thử lại hoặc chọn chủ đề có trong bài.
- **Correction:** Học viên nói câu trả lời/mức chưa phù hợp → tutor giữ lịch sử, hỏi phần cần sửa, trả lời lại và cho phép hoàn tác mức.
- **Ngoài phạm vi:** Tutor từ chối ngắn, giải thích phạm vi nguồn và chỉ tới kênh phù hợp.
- **Case domain:** Không suy ra năng lực từ một lượt; không dùng độ dài/cách viết câu hỏi làm bằng chứng duy nhất về trình độ.

## §7. Kiểm thử

### Chiều chất lượng

| Chiều | Định nghĩa pass có thể kiểm chứng |
|---|---|
| Groundedness | Mọi mệnh đề kiến thức trong câu trả lời được hỗ trợ trực tiếp bởi trang trích dẫn; suy luận được gắn nhãn và không vượt quá thông tin nguồn. |
| Citation accuracy | Bộ slide và số trang tồn tại, mở đúng trang, và trang đó chứa căn cứ cho câu trả lời. |
| Scope safety | Case không có căn cứ/ngoài phạm vi không tạo ra câu trả lời chắc chắn hay nguồn giả. |
| Level fit | Câu trả lời và gợi ý tuân thủ định nghĩa Cơ bản/Thông thạo/Nâng cao; không đòi kiến thức ngoài nguồn. |
| Adaptation | Mức chỉ đổi khi thoả đúng quy tắc bằng chứng, không nhảy quá một mức, có lý do và có hoàn tác. |
| UX recovery | Mọi case mơ hồ, không nguồn và lỗi kỹ thuật đều có ít nhất một hành động tiếp theo dùng được. |

### Quality bar dự kiến

Quality bar chính thức chỉ được chốt sau khi golden set được tạo nhưng trước lượt đo đầu:

- Ít nhất **85% case đạt toàn bộ tiêu chí bắt buộc**.
- **100% citation phải trỏ tới trang tồn tại**.
- **0 câu bịa nguồn** trong nhóm case không có căn cứ.
- **100% quyết định đổi mức tuân thủ quy tắc cập nhật mức**.

### Kết quả lượt chạy CP3

| Run | Model | Case | Đạt | Pass rate | Quality bar | Kết luận |
|---|---|---:|---:|---:|---:|---|
| `20260730T081816Z` | `gemini-3.5-flash` | 20 | 2 | 10% | 85% | Chưa đạt |
| `20260730T082211Z` (smoke sau sửa parser) | `gemini-3.5-flash` | 2 | 1 | 50% | 85% | Chưa đạt; case còn lại lỗi quota 429 |

Lượt đầu được giữ nguyên. Phân tích cho thấy phần lớn failure đến từ parser
thinking-part và quota/timeout; chi tiết tại
`eval/results/first-run-analysis.md`. Sau khi sửa parser, một case lạ đã chạy
end-to-end với AI thật, citation hợp lệ và câu hỏi gợi ý.

Live test mô phỏng Labcoach nhập câu chưa hardcode đã PASS: backend trả lời bằng
`gemini-3.5-flash-lite` fallback, có citation `[D1, trang 14]`,
`[D1, trang 20]` và 3 câu hỏi gợi ý. Trace:
`eval/results/labcoach-live-test.json`.

### Artifact checkpoint 3

- Prototype phải nhận được câu hỏi lạ nhập trực tiếp tại chỗ; không giới hạn ở
  các nút/câu hardcode trong `index.html`.
- Quyết định trung tâm gọi AI thật qua Gemini; trace thể hiện model và token
  usage trong bảng kết quả.
- Golden set tại `eval/golden_set.json` có 20 case, gồm 10 case phát triển từ
  chatlog thật và các case khó phủ nguồn sự thật, mơ hồ, ngoài phạm vi, đặc thù
  domain.
- Mỗi lượt chạy ghi đủ mọi case vào `eval/results/`, kể cả case sai và API lỗi.
- Báo cáo đối chiếu pass rate với quality bar 85%; kết quả thấp không bị xoá hoặc
  sửa sau khi chạy.

## §8. Phân công & kế hoạch

- Tên thành viên/phân công và willing users: bỏ qua theo phạm vi build hiện tại.
- Phương án automation đã chọn: conditional thay vì automate hoàn toàn, do cost-of-error của kiến thức sai cao.

## §9. Changelog

| Thời điểm | Đổi gì | Vì sao |
|---|---|---|
| 2026-07-30 | Tạo bản spec mốc 1: lát cắt, phạm vi, ba mức kiến thức, conditional automation, 10 kịch bản rủi ro và quality bar dự kiến | Chuyển prototype hardcode hiện tại thành phạm vi build và đo được |
| 2026-07-30 | Bỏ qua tên/phân công thành viên và willing users trong phạm vi build | Theo yêu cầu của nhóm để chuyển sang xử lý dữ liệu slide |
| 2026-07-30 | Chuẩn hóa 58 trang từ hai bộ slide thành JSONL có mã trang và citation ổn định | Làm nguồn truy xuất cho backend ở mốc 3 |
| 2026-07-30 | Thêm backend HTTP API, BM25-like retrieval và session state trong RAM | Hoàn thành mốc 3 mà không cần tải dependency; chuẩn bị điểm nối AI thật |
| 2026-07-30 | Thêm Gemini 3.5 Flash grounded generation, citation allowlist và golden set 20 case cùng eval runner | Đáp ứng artifact CP3: AI thật + lượt đo đầu có đủ case |
