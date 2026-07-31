# AI SPEC — VLearn Adaptive Tutor · Nhóm Fiveboiz E403

Hướng: [x] A — VLearn
Loại: [x] Tối ưu tính năng có sẵn
Trạng thái: **CP4 quality bar đã khóa; cập nhật đường demo và audit hiện tại ngày 2026-07-31.**

## §1. User & Job

- **Job executor:** Học viên đang tự học lại bài từ slide trên VLearn.
- **Core JTBD:** Khi đọc lại bài giảng và gặp một khái niệm chưa hiểu, học viên muốn được giải thích đúng với tài liệu và nhận bước học tiếp theo vừa sức để có thể tự kiểm tra mức hiểu của mình.
- **Current alternative:** Học viên tự nghĩ câu tiếp theo, tua lại slide, hỏi bạn/TA hoặc dừng sau câu trả lời đầu. Cách này vẫn được dùng vì sẵn có, nhưng không tạo signal kiểm tra hiểu bài và không hướng dẫn bước tiếp theo.
- **Problem statement (không chữ AI):** Học viên đang ôn lại slide nhận được một câu trả lời nhưng không có bước học tiếp theo vừa sức và gần như không được kiểm tra hiểu bài, nên họ không biết nên đào sâu, ôn lại hay chuyển chủ đề.
- **Evidence chuẩn B — mining có thể chạy lại:**
  - Phạm vi: 2.522 message, 1.261 turn hoàn chỉnh, 369 user ẩn danh, 585 hội thoại.
  - **1.261/1.261 (100%)** tutor message có `follow_ups=[]`.
  - Chỉ **3/1.261 (0,2%)** tutor message có `asked_check_question=True`.
  - **1.261/1.261 (100%)** có `misconceptions=[]`.
  - **582/1.261 (46,2%)** không có citation.
  - Rating quan sát được: 37 down và 33 up; rating null không được suy diễn thành hài lòng/không hài lòng.
  - Phương pháp, code đếm và 5 ví dụ có mã turn: `evidence/mine_chatlog.py` và `evidence/mining-report.md`.
  - Năm turn minh họa: `T0769`, `T0408`, `T1258`, `T0776`, `T0519`; đều có rating down, citation rỗng và follow-up rỗng.

## §2. Impact & quyết định chọn

Mẫu số cho ba ứng viên là 1.261 tutor turn trong data pack.

| Ứng viên | Bao nhiêu người/lượt gặp | Tần suất | Tổn thất quan sát được mỗi lần | Khả thi trong hackathon | Quyết định |
|---|---:|---:|---|---|---|
| A. Citation/groundedness | 582/1.261 lượt (46,2%) | Gần 1/2 lượt | 1 câu trả lời không có điểm kiểm chứng; 5/5 ví dụ down được chọn cũng citation rỗng | Cao: đã có query-aware transcript retrieval; citation allowlist còn backlog | Giữ làm điều kiện an toàn, không chọn làm lát cắt chính |
| B. Câu hỏi tiếp theo thích ứng + quiz | 1.261/1.261 lượt (100%) không follow-up; 1.258/1.261 lượt (99,8%) không hỏi kiểm tra | Mỗi turn | Mất 1 cơ hội đưa bước học tiếp theo và 1 signal kiểm tra hiểu bài | Cao: sinh 5 suggestion khi chọn mức và quiz một câu trong cùng flow | **Chọn** |
| C. Phát hiện misconception dài hạn | 1.261/1.261 lượt (100%) không ghi misconception | Mỗi turn | Không có misconception signal để theo dõi lỗ hổng qua thời gian | Thấp hơn: cần nhiều câu trả lời, hồ sơ dài hạn và tiêu chí chấm domain | Loại khỏi MVP, đưa backlog |

**Lý do chọn B:** độ phủ lớn nhất trong data (100%), xuất hiện đúng tại mỗi turn,
có thể demo end-to-end trong 5 phút và đo bằng số suggestion, độ phù hợp mức cùng
khả năng xử lý case không nguồn. A vẫn được giữ như hard constraint vì một
follow-up thích ứng nhưng không có căn cứ có thể làm học viên học sai. C bị loại
vì prototype theo phiên ngắn chưa đủ bằng chứng để kết luận misconception dài hạn.

## §3. Giải pháp tương tự đã nghiên cứu

| Sản phẩm | Flow quan sát được | Đáng học | Đáng né | VLearn Tutor khác gì |
|---|---|---|---|---|
| [ChatGPT Study Mode](https://help.openai.com/en/articles/11780217-study-mode) | Hỏi mục tiêu/mức hiện tại → giải thích theo lớp → hỏi kiểu Socratic → quiz và feedback | Kiểm tra hiểu bài từng bước; cho người học yêu cầu đơn giản hơn hoặc khó hơn | Có thể vẫn đưa direct answer; nguồn upload có thể bị đọc thiếu và cần user chỉ rõ trang | Phạm vi cố định trên transcript khóa học; ba mức hiển thị rõ, có 5 suggestion và quiz; citation allowlist là backlog |
| [NotebookLM](https://support.google.com/notebooklm/answer/16179559) | Chọn nguồn → hỏi trong chat → trả lời có inline citation → bấm citation để xem ngữ cảnh | Grounded chat và citation điều hướng về đúng đoạn nguồn | Tập trung nghiên cứu nguồn hơn là cập nhật mức hiểu; không bảo đảm mọi source ngắn đều có citation riêng | Giữ source grounding nhưng thêm câu hỏi tiếp theo và quiz theo mức Cơ bản/Thông thạo/Nâng cao |

**Quyết định thiết kế rút ra:** học NotebookLM ở khả năng kiểm chứng nguồn và học
Study Mode ở flow hỏi–kiểm tra–điều chỉnh độ khó; không sao chép phạm vi mở của
hai sản phẩm, vì MVP chỉ có thẩm quyền trên 6 transcript bài giảng đã cung cấp.

## §4. Thiết kế

### Lát cắt MVP — một câu

> Một học viên đang ôn lại tài liệu đặt câu hỏi tự do; tutor truy xuất các đoạn transcript liên quan, trả lời theo mức học viên đã chọn, kèm mã căn cứ và cho phép làm một câu quiz kiểm tra nhanh.

### Phạm vi chức năng

1. Học viên hỏi tự do trong khung chat.
2. Tutor chỉ dùng 6 transcript bài giảng đã chuẩn hoá, gồm khoảng 700 đoạn có mã `Txx-NNN`, làm nguồn sự thật cho MVP.
3. Câu trả lời có mã trích dẫn `Txx-NNN`; giao diện cho phép điều hướng tới phần nội dung chứa mã tương ứng.
4. Khi học viên chọn mức, tutor sinh 5 câu hỏi gợi ý và một lối vào bài test; học viên vẫn có thể bỏ qua gợi ý và nhập câu hỏi riêng.
5. Giao diện giữ mức học viên tự chọn trong bộ nhớ trình duyệt và gửi mức đó theo từng request để điều chỉnh câu trả lời, suggestion và quiz:
   - **Cơ bản:** nhận biết, nhắc lại định nghĩa, thuật ngữ và ví dụ trực tiếp.
   - **Thông thạo:** giải thích quan hệ, so sánh, áp dụng vào tình huống gần với slide.
   - **Nâng cao:** phân tích điều kiện, giới hạn, đánh đổi hoặc tình huống mới có thể suy luận từ nguồn.
6. Tutor sinh một câu quiz trắc nghiệm theo mức; giao diện chấm đúng/sai ngay và hiển thị phản hồi ôn tập.
7. Học viên luôn có thể tự đổi mức và có thể bỏ qua câu hỏi gợi ý.

### Quy tắc mức kiến thức trong MVP

- Mức ban đầu do học viên tự chọn; sản phẩm không tuyên bố đây là kết luận năng lực chính thức.
- Tutor sinh câu trả lời, suggestion và quiz theo đúng mức đang chọn.
- Học viên có thể đổi mức bất kỳ lúc nào; mức hiện chỉ được giữ ở frontend, chưa có session backend.
- Quiz hiện là kiểm tra nhanh một câu theo mức và gợi ý trang ôn lại khi sai.
- **Không tự động tăng/giảm mức trong MVP** vì một câu quiz không đủ bằng chứng; tự động thích ứng từ nhiều signal là backlog sau validation.

### Non-goals

- Không trả lời kiến thức ngoài 6 transcript bài giảng trong MVP.
- Không chấm điểm chính thức hoặc thay thế giảng viên/TA.
- Không xây hồ sơ năng lực dài hạn giữa nhiều thiết bị hoặc nhiều khoá học.
- Không tự động tạo lộ trình học toàn khoá.
- Không dùng chatlog để huấn luyện mô hình hoặc hiển thị nội dung hội thoại thật trong sản phẩm.
- Không tự động kết luận hoặc thay đổi trình độ học viên từ một câu trả lời.

### Mức prototype và automation

- **Mức nhắm tới:** Working prototype.
- **Phần thật:** parse 6 transcript thành khoảng 700 chunk/98 phần, truy hồi theo câu hỏi trên toàn corpus, gọi Gemini để trả lời, sinh 5 gợi ý theo mức, sinh quiz và chuyển model dự phòng khi model chính lỗi/quota.
- **Phần đơn giản hoá:** mức do người dùng tự chọn và giữ ở frontend; quiz một câu/mức, logic chấm phía client là deterministic; chưa có session backend hay hồ sơ người dùng dài hạn.
- **Giới hạn đã biết:** citation hiện được yêu cầu trong prompt nhưng chưa có allowlist server-side để loại mã do model tạo sai; đây là hạng mục cần hoàn thiện trước khi tuyên bố 100% citation hợp lệ.
- **Automation:** Conditional.
- **Lý do theo cost-of-error:** Tutor được tự trả lời khi có căn cứ rõ trong slide. Khi không tìm thấy nguồn, nguồn mâu thuẫn, hoặc câu hỏi thiếu ngữ cảnh, tutor không đoán mà phải báo giới hạn hay hỏi lại. Một câu trả lời sai có thể khiến học viên học sai và mất niềm tin; việc hỏi lại tốn ít hơn việc sửa hiểu nhầm.

### Kiến trúc MVP

`index.html` → `POST /api/chat` → truy hồi top transcript chunks theo nội dung câu hỏi
trên toàn bộ corpus → Gemini → câu trả lời + mã citation. Frontend giữ `currentLevel`
trong RAM của trang và gửi `level` theo request; không có `session_id` và không ghi
hội thoại người dùng xuống đĩa.

API demo hiện gồm `GET /api/health`, `GET /api/slides`,
`POST /api/suggest-questions`, `POST /api/chat` và `POST /api/generate-quiz`.
Model chính là `gemini-3.5-flash`; khi quota/lỗi, agent thử
`gemini-3.5-flash-lite` và các model Gemini thay thế đã cấu hình.

### Nguyên tắc HAX/PAIR áp dụng

| Nguyên tắc | Áp cụ thể vào prototype |
|---|---|
| G1 — Làm rõ hệ thống làm được gì | Lời chào nêu rõ tutor trả lời từ transcript bài giảng, gợi ý câu hỏi theo mức và sinh quiz kiểm tra nhanh. |
| G2 — Làm rõ nó làm tốt đến đâu | Mỗi câu trả lời hiển thị mã căn cứ `Txx-NNN`; citation allowlist server-side vẫn là giới hạn chưa hoàn thiện. |
| G10 — Thu hẹp phạm vi khi nghi ngờ | Câu hỏi mơ hồ được hỏi lại một câu; không có đoạn nguồn đủ liên quan thì tutor nói không tìm thấy căn cứ. |
| G11 — Giải thích vì sao | Citation nêu mã đoạn transcript hỗ trợ câu trả lời; quiz sai hiển thị giải thích và phần cần ôn. |
| G9 — Sửa dễ dàng | Học viên có thể hỏi lại và tự đổi mức ngay trong chat. |
| PAIR — Feedback + Control | Gợi ý là tuỳ chọn; chat tự do và nút đổi mức luôn còn khả dụng. |
| PAIR — Errors + Graceful Failure | Phân biệt “không có trong tài liệu”, “câu hỏi chưa rõ” và “dịch vụ AI lỗi”; mỗi trường hợp có đường tiếp tục riêng. |

## §5. Kiểu lỗi — 4 lớp chỗ khó

| ID | Tình huống cụ thể | Lớp | Hành vi mong muốn | Nguyên tắc |
|---|---|---|---|---|
| R1 | Hỏi một khái niệm không xuất hiện trong 6 transcript | ① Nguồn sự thật | Nói không tìm thấy căn cứ; không bịa; gợi ý câu hỏi gần nhất có trong bài | G2, G10 |
| R2 | Đoạn truy xuất có từ khoá giống câu hỏi nhưng không đủ để kết luận | ① Nguồn sự thật | Không biến mức liên quan thấp thành câu trả lời chắc chắn; báo giới hạn hoặc hỏi lại | G2, G10 |
| R3 | Học viên hỏi “cái này hoạt động thế nào?” nhưng không nêu “cái này” | ② Mơ hồ | Hỏi lại đang nói đến khái niệm hoặc trang nào | G10 |
| R4 | Một thuật ngữ xuất hiện ở nhiều ngữ cảnh trong corpus | ② Mơ hồ | Nêu hai cách hiểu ngắn và yêu cầu chọn ngữ cảnh | G10, G9 |
| R5 | Học viên yêu cầu làm hộ bài tập hoặc đưa đáp án chấm điểm chính thức | ③ Ngoài phạm vi | Từ chối làm thay/chấm chính thức; chuyển sang gợi ý từng bước dựa trên slide | G1, PAIR Control |
| R6 | Học viên hỏi deadline, link nộp bài hoặc chính sách khoá học | ③ Ngoài phạm vi | Nói rõ slide học thuật không phải nguồn chính thức; hướng dẫn kiểm tra kênh khoá học/TA | G1, G10 |
| R7 | Tutor suy diễn trình độ từ một câu đúng | ④ Đặc thù domain | Không tự đổi mức trong MVP; mức chỉ đổi khi học viên chủ động chọn | G9, G17 |
| R8 | Câu gợi ý mức nâng cao đòi kiến thức không thể suy ra từ slide | ④ Đặc thù domain | Loại câu không truy vết được về nguồn; hạ độ khó hoặc gắn rõ câu mở rộng ngoài phạm vi | G2, G10 |
| R9 | Hai trang slide diễn đạt khác nhau hoặc có vẻ mâu thuẫn | ① Nguồn sự thật | Trình bày cả hai trích dẫn và nói rõ chưa thể kết luận thay vì tự hoà giải | G2, G11 |
| R10 | API AI hoặc truy xuất tài liệu bị lỗi | Failure | Giữ nguyên câu hỏi, báo lỗi kỹ thuật, cho phép thử lại; không hiển thị câu trả lời hardcode như kết quả AI | PAIR Graceful Failure |

## §6. Bốn đường đi của trải nghiệm

- **Happy path:** Học viên chọn mức → nhận 5 câu gợi ý và nút test → chọn gợi ý hoặc nhập câu hỏi riêng → truy hồi đoạn transcript liên quan → trả lời đúng mức kèm mã căn cứ → có thể đổi mức hoặc làm quiz.
- **Low-confidence:** Có nguồn gần đúng nhưng chưa đủ → tutor nói điều đã xác định được và hỏi một câu làm rõ; chưa cập nhật mức.
- **Failure/không căn cứ:** Không có nguồn hoặc dịch vụ lỗi → tutor nêu đúng loại lỗi, không tạo kiến thức thay thế, cho phép thử lại hoặc chọn chủ đề có trong bài.
- **Correction:** Học viên thấy mức chưa phù hợp → tự chọn mức khác và hỏi lại; biến mức ở frontend được cập nhật nhưng lịch sử hiển thị không bị xoá.
- **Ngoài phạm vi:** Tutor từ chối ngắn, giải thích phạm vi nguồn và chỉ tới kênh phù hợp.
- **Case domain:** Không suy ra năng lực từ một lượt; mức tự chọn được ghi rõ là lựa chọn trải nghiệm, không phải điểm đánh giá chính thức.

## §7. Kiểm thử

### Chiều chất lượng

| Chiều | Định nghĩa pass có thể kiểm chứng |
|---|---|
| Groundedness | Mọi mệnh đề kiến thức trong câu trả lời được hỗ trợ trực tiếp bởi chunk transcript được trích dẫn; suy luận không vượt quá thông tin nguồn. |
| Citation accuracy | Mã `Txx-NNN` tồn tại trong transcript, điều hướng đúng phần và đoạn đó chứa căn cứ cho câu trả lời. |
| Scope safety | Case không có căn cứ/ngoài phạm vi không tạo ra câu trả lời chắc chắn hay nguồn giả. |
| Level fit | Hai người chấm độc lập xác nhận answer/suggestion đúng taxonomy Cơ bản/Thông thạo/Nâng cao của mức đã chọn; không dùng kiến thức ngoài nguồn. |
| UX recovery | Mọi case mơ hồ, không nguồn và lỗi kỹ thuật đều có ít nhất một hành động tiếp theo dùng được. |

### Quality bar chính thức — khóa tại CP4

- Ít nhất **85% case đạt toàn bộ tiêu chí bắt buộc**.
- **100% citation phải trỏ tới trang tồn tại**.
- **0 câu bịa nguồn** trong nhóm case không có căn cứ.
- **100% answer/suggestion được sinh theo đúng mức người dùng đã chọn**.

### Kết quả eval và audit

| Run | Model | Case | Đạt | Pass rate | Quality bar | Kết luận |
|---|---|---:|---:|---:|---:|---|
| `20260730T081816Z` — backend PDF cũ | `gemini-3.5-flash` | 20 | 2 | 10% | 85% | Chưa đạt |
| `20260730T082211Z` — smoke backend PDF cũ | `gemini-3.5-flash` | 2 | 1 | 50% | 85% | Chưa đạt; case còn lại lỗi quota 429 |
| `20260731-current-api-audit` — backend transcript đang demo | `gemini-3.5-flash-lite` fallback | 20 | 15 theo ngữ nghĩa; 14 nếu bắt buộc đúng mã citation kỳ vọng | 75%; 70% strict | 85% | Chưa đạt |

Hai lượt ngày 2026-07-30 được giữ làm bằng chứng lịch sử của backend PDF cũ.
Phân tích khi đó cho thấy failure chủ yếu đến từ parser thinking-part,
quota/503/timeout; chi tiết tại `eval/results/first-run-analysis.md`. Live test
Labcoach trong `eval/results/labcoach-live-test.json` cũng thuộc backend cũ:
response có citation `[D1, trang 14]`, `[D1, trang 20]` và 3 suggestion. Không
dùng trace đó để mô tả response của backend transcript hiện tại.

Audit ngày 2026-07-31 gọi trực tiếp đủ 20 câu trong `eval/golden_set.json` qua
`POST /api/chat` của demo hiện tại. Năm case chưa đạt theo hành vi mong đợi:

- `TC01`: hỏi slide 37 nhưng bot chỉ hỏi lại chung chung, chưa nói nguồn không có.
- `TC09`: bot khẳng định có thể lấy slide trên LMS thay vì hướng tới TA.
- `TC11`: trả lời 80% do evaluation thay vì 70% do con người/vận hành.
- `TC18`: nêu hai nghĩa của “PM” nhưng chưa hỏi người dùng chọn nghĩa nào.
- `TC19`: chưa truy xuất được trực tiếp câu hỏi theo mã `T01-005`.

`TC10` đúng về nội dung nhưng dùng `T01-009/010/011` thay vì mã kỳ vọng
`T01-008`; vì vậy pass khi chấm ngữ nghĩa và fail khi chấm strict citation.

**Giới hạn tái lập hiện tại:** `eval/run_eval.py` vẫn đọc schema cũ
`{"cases": [...]}` với các trường `question`, `level`, `expected_citations`,
trong khi `eval/golden_set.json` hiện là array dùng `input`,
`expected_behavior`, `expected_keywords`. Runner dừng với `TypeError`; audit
20 case trên chưa được coi là lượt runner chính thức cho tới khi hai schema
được thống nhất.

### Artifact checkpoint 3

- Prototype phải nhận được câu hỏi lạ nhập trực tiếp tại chỗ; không giới hạn ở
  các nút/câu hardcode trong `index.html`.
- Quyết định trung tâm gọi AI thật qua Gemini; trace thể hiện model và token
  usage trong bảng kết quả.
- Golden set tại `eval/golden_set.json` có 20 case, gồm **11 case phát triển từ
  chatlog thật và 9 case synthetic**, phủ nguồn sự thật, mơ hồ, ngoài phạm vi,
  hậu quả cao và edge case.
- Runner chính thức cần được sửa schema trước khi có thể ghi lại một lượt mới
  vào `eval/results/`; các artifact cũ không đại diện cho backend đang demo.
- Báo cáo đối chiếu pass rate với quality bar 85%; kết quả thấp không bị xoá hoặc
  sửa sau khi chạy.

## §8. Phân công & kế hoạch

- Phương án automation đã chọn: conditional thay vì automate hoàn toàn, do cost-of-error của kiến thức sai cao.
- **Phân công có tên và tỷ lệ đóng góp:**

  | Thành viên | Mã học viên | Phần việc chịu trách nhiệm | Đóng góp |
  |---|---|---|---:|
  | Nguyễn Hữu Nhật Minh | 2A202601551 | Product, evidence, lát cắt, spec, quality bar và điều phối checkpoint | 20% |
  | Ngô Hữu Nghĩa | 2A202601924 | Backend chatbot, Gemini, prompt, fallback và xử lý lỗi API | 20% |
  | Bùi Văn Khởi | 2A202601723 | Chuẩn hóa transcript, retrieval, citation, golden set và báo cáo eval | 20% |
  | Lý Thành Đạt | 2A202601469 | Frontend chatbot, trình xem nội dung, responsive và kết nối frontend–backend | 20% |
  | Lê Văn Huy | 2A202601235 | Luồng quiz sinh theo mức, kiểm thử, validation và demo | 20% |
  | **Tổng** |  | **Mỗi người triển khai, kiểm tra và giải thích được phần có tên mình** | **100%** |

- **Willing users dự kiến (cần xác nhận trước CP5):**
  1. Vũ Minh Quang
  2. Bùi Văn Khởi
  3. Lý Thành Đạt

- **Kế hoạch CP5:**
  1. Thống nhất schema `eval/run_eval.py` với `eval/golden_set.json`, sau đó chạy lại đủ 20 case bằng cùng golden set/bar và lưu artifact mới; không ghi đè lượt lịch sử.
  2. Mời 5 người ngoài nhóm, mỗi người test 10 phút với một happy path và một task khó.
  3. Hỏi đúng ba câu trong guide; lưu tên/vai, quan sát và quote nguyên văn vào `validation/feedback-log.md`.
  4. Chọn 1–2 thay đổi dựa trên feedback và ghi §9; phần giữ nguyên phải có lý do.
  5. Dry run demo 10 phút có bấm giờ: 1 case chuẩn + 1 case không đủ nguồn + số đo so với bar.
- **Review chéo:** mỗi thành viên review ít nhất một phần ngoài nhiệm vụ chính; cả 5 người cùng tham gia dry run và mỗi người trình bày ít nhất một phần trong demo.

## §9. Changelog

| Thời điểm | Đổi gì | Vì sao |
|---|---|---|
| 2026-07-30 | Tạo bản spec mốc 1: lát cắt, phạm vi, ba mức kiến thức, conditional automation, 10 kịch bản rủi ro và quality bar dự kiến | Chuyển prototype hardcode hiện tại thành phạm vi build và đo được |
| 2026-07-30 | Phân công công việc cho các thành viên | Mỗi thành viên phụ trách một nhóm nhiệm vụ và đóng góp ~20% |
| 2026-07-30 | Chuẩn hóa 58 trang từ hai bộ slide thành JSONL có mã trang và citation ổn định | Tạo nguồn cho backend PDF cũ; đường chạy này được giữ làm artifact lịch sử |
| 2026-07-30 | Thêm backend HTTP API, BM25-like retrieval và session state trong RAM | Hoàn thành backend PDF cũ và tạo điểm nối AI thật |
| 2026-07-30 | Thêm Gemini 3.5 Flash grounded generation, citation allowlist và golden set 20 case cùng eval runner | Tạo lượt đo lịch sử `2/20`; runner/schema này chưa được đồng bộ với backend demo hiện tại |
| 2026-07-30 | Chốt CP4: evidence mining chuẩn B, bảng impact 3 ứng viên, nghiên cứu sản phẩm tương tự và cập nhật phạm vi MVP khớp bản build | Đáp ứng checklist §2.7 của guide; quality bar khóa từ commit này |
| 2026-07-30 | Thay danh sách text slide bằng PDF viewer Day 1/Day 2; citation và quiz mở đúng trang | Thay đổi thuộc backend/frontend PDF cũ, không phải đường demo `main.py` hiện tại |
| 2026-07-30 | Mở rộng ngân hàng quiz lên 12 câu | Artifact của nhánh cũ; demo hiện tại sinh một câu quiz bằng Gemini theo mỗi request |
| 2026-07-31 | Chốt đường demo `uvicorn main:app`: 6 transcript/~700 chunk/98 phần, truy hồi câu hỏi tự nhập, 5 suggestion và quiz sinh bởi Gemini | Loại nhập nhằng giữa hai backend và mô tả đúng code đang chạy |
| 2026-07-31 | Audit trực tiếp 20 case trên API hiện tại: 15/20 theo ngữ nghĩa, 14/20 strict citation; bar 85% chưa đạt | Cập nhật số đo trung thực và ghi rõ runner chính thức còn lệch schema |
