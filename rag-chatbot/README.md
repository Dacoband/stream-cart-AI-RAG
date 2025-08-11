# StreamCart AI Chatbot API

Một API chatbot thông minh sử dụng FastAPI và Google Gemini Pro để tương tác với thông tin sản phẩm và cửa hàng từ StreamCart platform.

## 🚀 Tính năng chính

- **FastAPI Framework**: API RESTful hiệu suất cao với tài liệu tự động
- **Google Gemini Pro Integration**: Sử dụng model AI tiên tiến để xử lý ngôn ngữ tự nhiên
- **Product & Shop Integration**: Tích hợp real-time với backend API của StreamCart
- **Smart Context Understanding**: Hiểu ngữ cảnh và trả lời phù hợp theo yêu cầu
- **Vietnamese Language Support**: Hỗ trợ đầy đủ tiếng Việt

## 📋 Yêu cầu hệ thống

- Python 3.10+
- Kết nối internet (để gọi Gemini API và backend API)
- Google API Key cho Gemini Pro

## 🛠️ Cài đặt

1. **Clone repository và navigate vào thư mục:**
```bash
cd rag-chatbot
```

2. **Cài đặt dependencies:**
```bash
pip install -r requirements.txt
```

3. **Cấu hình environment variables:**
Tạo file `.env` với nội dung:
```
GOOGLE_API_KEY=AIzaSyCNX-OKoJkIICawnJCYoQoppbuxWcGAVjQ
BACKEND_API_URL=https://brightpa.me
```

## 🏃‍♂️ Chạy ứng dụng

1. **Khởi chạy server:**
```bash
python main.py
```

2. **Server sẽ chạy tại:** `http://localhost:8000`

3. **Truy cập API Documentation:** `http://localhost:8000/docs`

## 📚 API Endpoints

### 1. Chat với AI
**POST** `/chat`

**Request Body:**
```json
{
  "message": "Tôi muốn tìm hiểu về các sản phẩm có sẵn",
  "user_id": "optional_user_id",
  "session_id": "optional_session_id"
}
```

**Response:**
```json
{
  "response": "Chào bạn! Hiện tại StreamCart đang có các sản phẩm...",
  "status": "success"
}
```

### 2. Lấy danh sách sản phẩm
**GET** `/products`

**Response:**
```json
{
  "products": [...],
  "count": 6
}
```

### 3. Lấy danh sách cửa hàng
**GET** `/shops`

**Response:**
```json
{
  "shops": [...],
  "count": 0
}
```

### 4. Lấy thông tin cửa hàng theo ID
**GET** `/shops/{shop_id}`

### 5. Health Check
**GET** `/health`

**Response:**
```json
{
  "status": "healthy",
  "gemini_configured": true,
  "backend_api_url": "https://brightpa.me"
}
```

## 🧪 Testing

Chạy test suite để kiểm tra tất cả chức năng:

```bash
python test_client.py
```

Test các API backend riêng lẻ:
```bash
python test_apis.py
```

## 💡 Cách sử dụng

### 1. Chat về sản phẩm:
```json
{
  "message": "Tôi muốn tìm điện thoại iPhone"
}
```

### 2. Chat về cửa hàng:
```json
{
  "message": "Cho tôi biết thông tin các cửa hàng"
}
```

### 3. Chat chung:
```json
{
  "message": "Xin chào! Bạn có thể giúp tôi gì?"
}
```

## 🏗️ Kiến trúc hệ thống

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend/     │    │   FastAPI        │    │   Backend API   │
│   Client App    │───►│   Chatbot API    │───►│   (Products &   │
│                 │    │                  │    │    Shops)       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Gemini Pro    │
                       │   AI Model      │
                       └─────────────────┘
```

### Các thành phần chính:

1. **APIService**: Xử lý gọi API backend để lấy thông tin sản phẩm và cửa hàng
2. **PromptTemplateService**: Tạo và format prompt cho Gemini AI
3. **ChatbotService**: Logic chính xử lý tin nhắn và tạo response
4. **FastAPI App**: RESTful API endpoints

## 🔧 Cấu hình

### Environment Variables:
- `GOOGLE_API_KEY`: API key cho Google Gemini Pro
- `BACKEND_API_URL`: URL của backend API StreamCart

### Tùy chỉnh prompt:
Bạn có thể chỉnh sửa prompt templates trong `PromptTemplateService` để thay đổi cách AI phản hồi.

## 📝 Logs

Ứng dụng sử dụng Python logging để ghi log các hoạt động:
- API calls
- Errors
- Request processing

## 🚨 Error Handling

API có xử lý lỗi toàn diện:
- Network timeouts
- Invalid API responses  
- Gemini API errors
- Missing environment variables

## 🤝 Đóng góp

1. Fork repository
2. Tạo feature branch
3. Commit changes
4. Push và tạo Pull Request

## 📄 License

Dự án này được phát hành dưới MIT License.

## 📞 Hỗ trợ

Nếu bạn gặp vấn đề hoặc có câu hỏi, vui lòng tạo issue trên GitHub repository.

---

**Phát triển bởi:** StreamCart Team  
**Phiên bản:** 1.0.0  
**Cập nhật lần cuối:** July 31, 2025
