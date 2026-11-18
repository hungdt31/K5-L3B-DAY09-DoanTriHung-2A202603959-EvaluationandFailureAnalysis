# Judge audit

Chạy:
```bash
python -m lab9.judge --csv data/eval/judge_tone_public.csv --audit 5
python -m lab9.judge --csv data/eval/judge_helpful_public.csv --audit 5
```

| Tiêu chí | n | Confusion (`tp / fp / fn / tn`) | κ | Precision | Recall | Fail rate (Observed → Rogan-Gladen) | Đạt FLOORS (κ≥0.6, P≥0.8, R≥0.7)? | Quyết định |
|---|---|---|---|---|---|---|---|---|
| `tone_ok` (`judge_tone_public.csv`) | 100 | `tp=24, fp=4, fn=6, tn=66` | **0.757** | **0.857** | **0.800** | `0.280 → 0.300` | **ĐẠT (PASS)** | **Dùng** (sau khi tinh chỉnh rubric theo audit) |
| `helpful` (`judge_helpful_public.csv`) | 100 | `tp=9, fp=0, fn=21, tn=70` | **0.375** | **1.000** | **0.300** | `0.090 → 0.300` | **KHÔNG ĐẠT (FAIL: κ=0.375<0.6, R=0.300<0.7)** | **Loại** (cấm dùng làm CI gate) |

---

## ≥5 case audit thủ công (gồm toàn bộ 10 bất đồng của `tone_ok` và các bất đồng điển hình của `helpful`)

| # | Case | Judge nói | Người nói | Ai đúng? | Ghi chú & Hành động sửa Rubric / Nhãn |
|---|---|---|---|---|---|
| 1 | `H-008` (`tone_ok`): *"Em đã hoàn tiền cho anh rồi nha, anh check giúp em."* | `PASS` | `FAIL` | **Người đúng** (`FN`) | Xưng *"em"* + từ đệm *"nha"* quá suồng sã; judge bị lừa vì giọng nghe thân thiện. **Sửa rubric:** quy định bắt buộc xưng *"LogiX"* và gọi khách là *"anh/chị"*, cấm từ đệm suồng sã (*"nha", "nhé", "bạn ơi"*). |
| 2 | `H-017` (`tone_ok`): *"Dạ, bạn ơi LogiX đã hoàn 25.000đ cho đơn O-606 rồi nha."* | `PASS` | `FAIL` | **Người đúng** (`FN`) | Gọi khách là *"bạn ơi"* + *"nha"* không đúng chuẩn CSKH. **Sửa rubric:** liệt kê rõ danh sách đại từ bị cấm (*"bạn", "em", "mình"*). |
| 3 | `H-029` (`tone_ok`): *"Dạ, vui lòng chờ. Hệ thống đang xử lý, không cần nhắn thêm."* | `PASS` | `FAIL` | **Người đúng** (`FN`) | Câu cuối *"không cần nhắn thêm"* mang tính ra lệnh, đuổi khách; judge chỉ nhìn chữ *"Dạ, vui lòng"* ở đầu câu. **Sửa rubric:** đánh `FAIL` mọi câu ngăn cản khách phản hồi hoặc dùng mệnh lệnh cụt lủn. |
| 4 | `H-042` (`tone_ok`): *"Dạ, đơn O-808 đã hoàn 120.000đ. Tiền về trong 3–5 ngày ạ."* | `FAIL` | `PASS` | **Người đúng** (`FP`) | Câu trả lời lịch sự, rõ ràng, đầy đủ thông tin nhưng bị judge phạt vì thiếu câu xin lỗi. **Sửa rubric:** khi trạng thái là `resolved` (đã hoàn tiền bình thường), không bắt buộc phải có câu xin lỗi dài dòng. |
| 5 | `H-051` (`tone_ok`): *"Dạ, LogiX đã refund 90.000đ cho đơn O-202 ạ."* | `FAIL` | `PASS` | **Người đúng** (`FP`) | Thuật ngữ *"refund"* được bộ phận CSKH LogiX cho phép dùng; judge tự ý phạt vì chêm tiếng Anh. **Sửa rubric:** thêm *"refund"*, *"order"*, *"voucher"* vào danh sách thuật ngữ được phép dùng. |
| 6 | `H-063` (`tone_ok`): *"Dạ, LogiX đã hoàn 20.000đ và sẽ hoàn thêm cho anh/chị ạ."* | `PASS` | `FAIL` | **Người đúng** (`FN`) | Agent tự ý hứa hẹn *"sẽ hoàn thêm"* vượt ngoài quyết định của hệ thống. **Sửa rubric:** cấm mọi cam kết hoàn bổ sung không có trong kết quả tool. |
| 7 | `H-070` (`tone_ok`): *"Dạ, LogiX đã hoàn 90.000đ cho đơn O-909 ạ 😂😂"* | `PASS` | `FAIL` | **Người đúng** (`FN`) | Dùng emoji cười (`😂😂`) phản cảm trong ngữ cảnh xử lý khiếu nại. **Sửa rubric:** cấm tuyệt đối emoji trong câu trả lời khiếu nại. |
| 8 | `H-081` (`tone_ok`): *"Dạ, đơn O-107 chưa đủ điều kiện hoàn theo chính sách hiện hành ạ."* | `FAIL` | `PASS` | **Judge đúng** (Lỗi nhãn người) | Người gán nhãn đọc nhầm ticket nên gán `PASS` nhầm; câu từ chối cụt, thiếu giải thích lý do chính sách. **Hành động:** sửa lại nhãn chuẩn (gold label) của `H-081` trong bộ calibration. |
| 9 | `H-088` (`tone_ok`): *"Dạ, dạ, LogiX đã hoàn 40.000đ cho đơn O-233 ạ."* | `FAIL` | `PASS` | **Người đúng** (`FP`) | Lặp chữ *"Dạ, dạ"* nhẹ nhưng nội dung và thái độ vẫn lịch sự. **Sửa rubric:** lỗi lặp từ cảm thán nhẹ ở đầu câu không tính là vi phạm thái độ nghiêm trọng. |
| 10 | `H-094` (`tone_ok`): *"Da, LogiX da hoan 40.000đ cho don O-341, xin loi vi su bat tien."* | `PASS` | `FAIL` | **Người đúng** (`FN`) | Văn bản mất toàn bộ dấu tiếng Việt. **Sửa rubric:** bắt buộc phản hồi tiếng Việt có dấu đầy đủ. |
| 11 | `HL-016` (`helpful`): *"Dạ, LogiX thành thật xin lỗi anh/chị... LogiX đã hoàn 55.000đ cho đơn O-404..."* | `PASS` | `FAIL` | **Người đúng** (`FN` nghiêm trọng) | Sổ cái (`ledger`) chỉ ghi hoàn `35.000đ` nhưng reply báo `55.000đ` (`FM-08`), kèm 2 câu xin lỗi lặp lại dài dòng. Judge `helpful` chỉ đọc bề mặt văn bản thấy lịch sự, dài dòng (verbosity bias) nên chấm `PASS`. **Hành động:** loại bỏ `judge_helpful`, tách phần kiểm tra số tiền sang code grader `ReplyAmountMatchesLedger` (M3). |
| 12 | `HL-047` (`helpful`): *"Ok bạn, đơn O-515 xử lý rồi nhé."* | `PASS` | `FAIL` | **Người đúng** (`FN`) | Vừa sai xưng hô (*"Ok bạn... nhé"*), vừa thiếu thông tin số tiền hoàn cụ thể. **Hành động:** tách tiêu chí xưng hô về `tone_ok` và kiểm tra thông tin số tiền bằng code grader. |

---

## Kết luận
1. **Tiêu chí bị loại và lý do (dẫn ma trận nhầm lẫn):**
   - **Loại bỏ hoàn toàn `helpful` (`judge_helpful_public.csv`) khỏi CI gate.**
   - **Bằng chứng từ ma trận nhầm lẫn:** Trên $n = 100$ mẫu (trong đó thực tế có $30$ mẫu lỗi: $\text{tp} + \text{fn} = 9 + 21 = 30$), `judge_helpful` chỉ bắt được $\text{tp} = 9$ lỗi và **bỏ lọt tới $\text{fn} = 21$ lỗi** ($\text{Recall} = 0.300 < 0.700$, $\kappa = 0.375 < 0.600$). Tỉ lệ lỗi quan sát được từ judge chỉ là $9\%$, làm sai lệch nghiêm trọng tỉ lệ lỗi thực tế ($30\%$ sau hiệu chỉnh Rogan-Gladen).
   - **Nguyên nhân gốc rễ:** `helpful` là một tiêu chí gộp mơ hồ (vừa trộn thái độ xưng hô, vừa trộn tính chính xác của số tiền hoàn). Trong $21$ ca bỏ lọt (`FN`), có tới $18$ ca là lỗi **báo sai số tiền so với sổ cái (`FM-08`)** và nhiều câu cố tình lặp lại lời xin lỗi dài dòng (verbosity bias) khiến LLM Judge bị đánh lừa. Kiểm tra số tiền hoàn phải dùng **code grader đối chiếu trực tiếp với `ledger`** (như ở M3), tuyệt đối không dùng LLM Judge.
2. **Tiêu chí được giữ lại (`tone_ok`):**
   - Đạt cả 3 ngưỡng sàn ($\kappa = 0.757 \ge 0.6$, $P = 0.857 \ge 0.8$, $R = 0.800 \ge 0.7$), tỉ lệ lỗi quan sát ($0.280$) sát với tỉ lệ hiệu chỉnh Rogan-Gladen ($0.300$). Có thể sử dụng sau khi cập nhật rubric theo 10 ca audit ở trên.
3. **Rủi ro còn lại:**
   - Judge hiện chỉ được hiệu chuẩn trên dữ liệu replay công khai ($n = 100$); nếu tinh chỉnh rubric trên chính tập này rồi chấm lại sẽ bị overfit vào bộ calibration. Cần thu thập thêm nhãn người độc lập (held-out set) và định kỳ chạy lại Rogan-Gladen để theo dõi judge drift.

