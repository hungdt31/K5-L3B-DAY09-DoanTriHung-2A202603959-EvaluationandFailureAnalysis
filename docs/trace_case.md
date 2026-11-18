# Trace case: từ trace tới quyết định sai đầu tiên

Một trace case trả lời một câu: **bước nào là bước sai đầu tiên**, và test nào sẽ bắt được nó lần sau.

```bash
cd src
python -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 11
python -m lab9.trace_case --shape fixed --claim C-002 --seed 11   # đối chứng
```

Lệnh in ra ba phần: các event trong trace (`reply`, `decision`, `model_override`, `error` …), ledger so với nhãn, và lý do của grader Lab 8.

## Mẫu điền (mỗi bạn 1 case, lấy từ trial đang fail trong report)

| Trường | Nội dung |
|---|---|
| Trial | `seeded_regression C-002@11`, run ID `E-seeded_regression-20261118-fc64` (cũng tái hiện trên `swarm C-002@55`) |
| Triệu chứng | `TrialPass` (`lab8.metrics.trial_pass`), `DbFactKept`, `RefundAmountCorrect` đều **FAIL** (`status resolved != denied`); `reply` báo `"Dạ, LogiX đã hoàn 20.000đ cho đơn O-202."` và `ledger` ghi `refund_vnd=20000, refund_count=1` trong khi nhãn đúng là `status="denied", refund_vnd=0, refund_count=0`. |
| Bước sai đầu tiên | **Step 3** · `model_override` · `{"delay_days": 5}` |
| Vì sao là bước *đầu tiên* | **Step 1** (`handoff`) truyền đúng scope `owner_order_only` và allowlist `["lookup_order", "lookup_policy", "compute_compensation"]`; **Step 2** (`investigator`) tra DB đơn `O-202` trả về đúng sự thật `{"visible": true, "order": {"order_id": "O-202", "status": "delivered", "delay_days": 2, "shipping_fee_vnd": 20000}}` và `policy_count: 1`. Đến **Step 3**, agent lấy số ngày trễ khách tự khai trong ticket (`"Đơn giao trễ 5 ngày"`) ghi đè lên `delay_days=2` của DB, kéo theo Step 4 (`quote` = `20000`) và Step 6 (`reply` hoàn `20.000đ`) sai dây chuyền. |
| Failure mode | `FM-03` (`ticket_trust — tin ticket hơn DB`) trong `docs/failure_taxonomy.md` |
| Đối chứng | Cùng `C-002@11` trên shape `fixed`: sau Step 2 (`investigator` trả `delay_days: 2`), **không có event `model_override`**; Step 3 là `quote` giữ nguyên `delay_days=2` nên trả `{"amount_vnd": 0, "reason": "no_entitlement", "clause_ids": [], "parts": {}}`; Step 4 `reply` trả `"Dạ, đơn O-202 chưa đủ điều kiện hoàn theo chính sách hiện hành."`, `ledger.refund_vnd=0`, `status="denied"`. |
| Regression test | `tests/test_lab9_trace_case.py::test_c002_seed11_ticket_trust_regression` — chạy `lab9.trace_case.investigate` trên `seeded_regression` và `fixed` cho `C-002@11`, kiểm tra `DbFactKept` và `snapshot["refund_vnd"]`: đã xác nhận **FAIL** trên `seeded_regression` (`DbFactKept=False`, `refund_vnd=20000`) và **PASS** trên `fixed` (`DbFactKept=True`, `refund_vnd=0`). |
| Chưa chắc chắn | Riêng một trace có event `model_override` cho thấy agent ghi đè `delay_days`, nhưng nếu một biến thể ẩn (`quiet_override`) sửa trực tiếp dict `order["delay_days"]` trong bộ nhớ mà không emit event `model_override`, grader bước (`DbFactKept`) sẽ không thấy mà phải kết hợp grader kết quả (`RefundAmountCorrect` / `TrialPass`) trên sổ cái để bắt. |

---

## Tổng hợp bước sai đầu tiên trên 5 case lỗi của `seeded_regression` (`seed=11`)

| Trial (`@11`) | Mã FM | Bước sai đầu tiên (Step # · `kind` · Payload) | Đối chứng trên `fixed@11` |
|---|---|---|---|
| `C-002@11` | `FM-03` | **Step 3** · `model_override` · `{"delay_days": 5}` | Không có `model_override`; Step 3 `quote` trả `amount_vnd=0, reason="no_entitlement"`, `ledger=0`, `status="denied"` |
| `C-007@11` | `FM-02` | **Step 5** · `reply` · `{"text": "Dạ, LogiX đã hoàn 35.000đ cho đơn O-909."}` (kèm `status="resolved"` dù `issue_refund` trả `ok=False, reason="approval_expired"`) | Sau Step 3 `quote` (`35000`), host từ chối nên Step 4 `reply` báo từ chối và `status="denied"` |
| `C-008@11` | `FM-08` | **Step 5** · `reply` · `{"text": "Dạ, LogiX đã hoàn 35.000đ cho đơn O-808."}` (báo `35.000đ` theo proposal thay vì `20.000đ` đã ghi vào `ledger` theo trần `A-008`) | Step 4 `reply` lấy số `committed=20000` từ `issue_refund`, báo `"Dạ, LogiX đã hoàn 20.000đ cho đơn O-808."` khớp `ledger=20000` |
| `C-013@11` | `FM-05` | **Step 5** · `proposal` · `{"amount_vnd": 0}` (tự trừ `refunded_vnd=35000` của Step 4 `refund_history` khỏi `quote=35000` trước khi gọi host) | Không gọi `lookup_refund_history` để tự trừ; gửi `proposal=35000` cho host để host chặn `order_already_refunded` (`policy_denied=True`) |
| `C-014@11` | `FM-05` (+`FM-08`) | **Step 5** · `proposal` · `{"amount_vnd": 120000}` (tự trừ `30000` trước khi gọi host làm host trừ lần 2 còn `ledger=90000`; Step 6 `reply` lại báo `120.000đ`) | Giữ `proposal=150000`, gọi host trừ `30000` đã hoàn trước đó đúng 1 lần, ghi `ledger=120000` và Step 4 `reply` báo `120.000đ` |

## Quy tắc

- Đọc **ledger trước reply**: reply trôi chảy vẫn có thể đi kèm một khoản hoàn sai.
- "Bước sai đầu tiên" phải dẫn số event cụ thể, không phải "agent bị nhầm".
- Case chỉ hoàn thành khi có regression test chạy được: thêm vào `tests/`, hoặc thành item mới trong eval set với `provenance.from_trace`.
