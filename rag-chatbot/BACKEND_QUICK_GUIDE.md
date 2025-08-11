# Backend C# - AI Integration Quick Guide (Super Simple)

## 🎯 Tóm tắt cho Backend Developer

### Những gì bạn cần làm:

1. **Get user_id từ JWT claims** (sau khi user đăng nhập)
2. **Call AI Service** với HTTP POST
3. **Return response** 


## 🚀 Super Quick Implementation

### 1. Models
```csharp
public class ChatRequest { public string Message { get; set; } }
public class ChatResponse { public string Response { get; set; } public string Status { get; set; } }
```

### 2. Controller
```csharp
[HttpPost("api/chat")]
public async Task<ChatResponse> Chat([FromBody] ChatRequest request)
{
    var userId = User.FindFirst("sub")?.Value; // Từ JWT
    
    using var client = new HttpClient();
    var aiRequest = new { message = request.Message, user_id = userId };
    var response = await client.PostAsync("http://localhost:8000/chat", 
        new StringContent(JsonSerializer.Serialize(aiRequest), Encoding.UTF8, "application/json"));
    
    return await response.Content.ReadFromJsonAsync<ChatResponse>();
}

[HttpGet("api/chat/history")]
public async Task<IActionResult> GetHistory()
{
    var userId = User.FindFirst("sub")?.Value;
    
    using var client = new HttpClient();
    var response = await client.GetAsync($"http://localhost:8000/user/{userId}/history");
    var content = await response.Content.ReadAsStringAsync();
    
    return Ok(JObject.Parse(content));
}
```

### 3. Frontend call
```javascript
// Chat
fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token },
    body: JSON.stringify({ message: 'Hello AI!' })
})

// History  
fetch('/api/chat/history', {
    headers: { 'Authorization': 'Bearer ' + token }
})
```

## ✅ Done!

- AI Service URL: `http://localhost:8000`
- Chat: `POST /chat` với `{ message, user_id }`
- History: `GET /user/{user_id}/history`
- **No session_id needed!**

Xem file `BACKEND_SIMPLE_INTEGRATION.md` để có code đầy đủ!
