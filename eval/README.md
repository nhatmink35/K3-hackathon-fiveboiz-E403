# CP3 evaluation

## Golden set

`golden_set.json` có 20 case:

- 10 case phát triển từ chatlog thật, giữ `turn_id` để phúc khảo.
- 6 case thường lấy từ nội dung slide.
- 4 case khó: nguồn không tồn tại, logistics ngoài phạm vi, câu mơ hồ và khẳng
  định sai đặc thù domain.

Không dán nguyên hội thoại chatlog vào golden set.

## Chạy lượt đo

Lệnh dưới đây gửi câu hỏi và tối đa 4 slide chunks liên quan tới Gemini:

```powershell
python eval/run_eval.py
```

Smoke test hai case:

```powershell
python eval/run_eval.py --limit 2
```

Mỗi lượt luôn ghi đủ tất cả case đã chạy vào:

- `eval/results/run-<UTC>.csv`: input, output, citation, pass/fail, lỗi, latency
  và token usage của từng case.
- `eval/results/run-<UTC>-summary.json`: tỷ lệ đạt và so sánh quality bar 85%.

Case sai vẫn được ghi nguyên trạng. Runner không sửa quality bar dựa trên kết
quả.

Trước khi push, chạy `python scripts/sanitize_eval_results.py`. Script giữ bản
đầy đủ tại `eval/private-results/` (Git ignore) và loại nội dung câu trả lời khỏi
CSV được commit; metadata đánh giá vẫn được giữ nguyên.
