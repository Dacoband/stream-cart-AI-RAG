# StreamCart Chatbot Policies Integration

## Tổng quan
Hệ thống chatbot đã được tích hợp chính sách mua hàng và bán hàng của nền tảng StreamCart. Khi người dùng hỏi về các chính sách, hệ thống sẽ tự động cung cấp thông tin chính xác và đầy đủ.

## Các tính năng mới

### 1. Tự động phát hiện câu hỏi về chính sách
Chatbot có thể nhận diện các từ khóa liên quan đến chính sách:
- `chính sách`, `quy định`, `điều khoản`
- `mua hàng`, `đặt hàng`, `thanh toán`
- `bán hàng`, `mở shop`, `đăng ký shop`
- `đổi trả`, `hoàn tiền`, `vận chuyển`
- `vi phạm`, `trách nhiệm`, `nghĩa vụ`

### 2. API endpoints mới
```
GET /policies - Lấy toàn bộ chính sách
GET /policies/purchase - Chỉ chính sách mua hàng
GET /policies/sales - Chỉ chính sách bán hàng
GET /policies/search?q={query} - Tìm kiếm chính sách theo từ khóa
```

### 3. Tích hợp vào hệ thống chat
- Khi người dùng hỏi về chính sách, chatbot sẽ tự động include thông tin từ `policies.py`
- Thông tin được format đẹp và dễ đọc
- Ưu tiên hiển thị phần chính sách liên quan nhất với câu hỏi

## Ví dụ sử dụng

### Câu hỏi của user:
- "Chính sách đổi trả như thế nào?"
- "Làm sao để mở shop?"
- "Quy định thanh toán ra sao?"
- "Tôi vi phạm thì bị xử lý thế nào?"

### Phản hồi của chatbot:
Chatbot sẽ trả lời với thông tin chính sách chi tiết, bao gồm:
- Điều kiện và quy trình
- Thời hạn và yêu cầu
- Quyền và nghĩa vụ của các bên
- Xử lý vi phạm (nếu áp dụng)

## Files được thêm/sửa đổi

### 1. `policies.py` (MỚI)
- Chứa toàn bộ nội dung chính sách
- Functions: `search_policy()`, `get_purchase_policy()`, `get_sales_policy()`
- Tự động mapping từ khóa với nội dung tương ứng

### 2. `main.py` (CẬP NHẬT)
- Import policy functions
- Cập nhật `get_additional_context()` để include chính sách
- Thêm 5 API endpoints mới cho policies

### 3. `test_policies.py` (MỚI)
- Script test để verify tích hợp chính sách
- Có thể chạy để kiểm tra hoạt động

## Cách chạy test
```bash
cd "d:\My Project\stream-cart-AI-RAG\rag-chatbot"
python test_policies.py
```

## Deployment
Code đã sẵn sàng deploy. Chỉ cần restart server:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Lưu ý
- Tất cả nội dung chính sách được lưu trong `policies.py` 
- Dễ dàng cập nhật/chỉnh sửa chính sách mà không cần động vào logic chính
- Hỗ trợ tìm kiếm thông minh theo từ khóa
- Tự động ưu tiên hiển thị phần liên quan nhất với câu hỏi
