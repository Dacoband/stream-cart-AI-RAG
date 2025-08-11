# Backend C# Simple Integration Guide

## 🎯 Solution đơn giản cho Backend C#

### Kiến trúc đơn giản:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend C#     │    │   AI Service    │
│                 │    │                  │    │   (Python)      │
│   - Send Message│───►│   - Get user_id  │───►│   - Process AI  │
│   - Show Response│   │   - Gen session  │    │   - Return Resp │
│                 │◄───│   - Call AI API  │◄───│                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📦 Những gì Backend C# cần:

### 1. **Models (đơn giản)**

```csharp
// Models/ChatModels.cs
public class ChatRequest
{
    public string Message { get; set; }
}

public class ChatResponse
{
    public string Response { get; set; }
    public string Status { get; set; }
    public string UserId { get; set; }
    public string SessionId { get; set; }
    public string Error { get; set; }
}

public class AIChatRequest
{
    public string Message { get; set; }
    public string UserId { get; set; }
    // Bỏ SessionId - chỉ dùng UserId
}

public class AIChatResponse
{
    public string Response { get; set; }
    public string Status { get; set; }
    public string UserId { get; set; }
    // Bỏ SessionId - không cần thiết
    public string Error { get; set; }
}
```

### 2. **AI Service Client**

```csharp
// Services/AIChatService.cs
public interface IAIChatService
{
    Task<ChatResponse> SendMessageAsync(string message, string userId);
}

public class AIChatService : IAIChatService
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<AIChatService> _logger;
    private readonly string _aiServiceUrl;

    public AIChatService(HttpClient httpClient, IConfiguration config, ILogger<AIChatService> logger)
    {
        _httpClient = httpClient;
        _logger = logger;
        _aiServiceUrl = config["AIService:BaseUrl"]; // http://localhost:8000
    }

    public async Task<ChatResponse> SendMessageAsync(string message, string userId)
    {
        try
        {
            var request = new AIChatRequest
            {
                Message = message,
                UserId = userId
                // Không cần SessionId nữa
            };

            var json = JsonSerializer.Serialize(request);
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            var response = await _httpClient.PostAsync($"{_aiServiceUrl}/chat", content);
            
            if (response.IsSuccessStatusCode)
            {
                var responseContent = await response.Content.ReadAsStringAsync();
                var aiResponse = JsonSerializer.Deserialize<AIChatResponse>(responseContent, new JsonSerializerOptions
                {
                    PropertyNameCaseInsensitive = true
                });

                return new ChatResponse
                {
                    Response = aiResponse.Response,
                    Status = aiResponse.Status,
                    UserId = aiResponse.UserId,
                    // Bỏ SessionId
                    Error = aiResponse.Error
                };
            }
            else
            {
                _logger.LogError($"AI Service returned {response.StatusCode}: {await response.Content.ReadAsStringAsync()}");
                return new ChatResponse
                {
                    Response = "Xin lỗi, có lỗi xảy ra với AI service.",
                    Status = "error",
                    Error = $"AI Service Error: {response.StatusCode}"
                };
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error calling AI service");
            return new ChatResponse
            {
                Response = "Xin lỗi, không thể kết nối với AI service.",
                Status = "error",
                Error = ex.Message
            };
        }
    }
}
```

### 3. **Session Manager (đơn giản)**

```csharp
// Services/SessionManager.cs
public interface ISessionManager
{
    string GetUserIdFromClaims(ClaimsPrincipal user);
    // Bỏ GenerateSessionId - không cần nữa
}

public class SessionManager : ISessionManager
{
    public string GetUserIdFromClaims(ClaimsPrincipal user)
    {
        // Lấy user ID từ JWT claims sau khi đăng nhập
        var userId = user.FindFirst("sub")?.Value 
                  ?? user.FindFirst("user_id")?.Value 
                  ?? user.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        
        if (string.IsNullOrEmpty(userId))
        {
            // Fallback cho anonymous user
            return $"anonymous_{Guid.NewGuid().ToString()[..8]}";
        }
        
        return userId;
    }
}
```

### 4. **Controller (đơn giản) - Updated với Chat History**

```csharp
// Controllers/ChatController.cs
[ApiController]
[Route("api/[controller]")]
public class ChatController : ControllerBase
{
    private readonly IAIChatService _aiChatService;
    private readonly ISessionManager _sessionManager;
    private readonly ILogger<ChatController> _logger;

    public ChatController(
        IAIChatService aiChatService, 
        ISessionManager sessionManager,
        ILogger<ChatController> logger)
    {
        _aiChatService = aiChatService;
        _sessionManager = sessionManager;
        _logger = logger;
    }

    /// <summary>
    /// Chat với AI - Chỉ dùng USER_ID để track lịch sử
    /// </summary>
    [HttpPost]
    public async Task<ActionResult<ChatResponse>> Chat([FromBody] ChatRequest request)
    {
        try
        {
            // 1. Validate request
            if (string.IsNullOrWhiteSpace(request.Message))
            {
                return BadRequest(new ChatResponse
                {
                    Status = "error",
                    Error = "Message cannot be empty"
                });
            }

            // 2. Get user ID từ authentication claims
            var userId = _sessionManager.GetUserIdFromClaims(User);

            _logger.LogInformation($"Processing chat for user {userId}");

            // 3. Call AI Service - chỉ cần userId
            var response = await _aiChatService.SendMessageAsync(request.Message, userId);

            _logger.LogInformation($"AI response status: {response.Status}");

            return Ok(response);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing chat request");
            return StatusCode(500, new ChatResponse
            {
                Status = "error",
                Error = "Internal server error"
            });
        }
    }

    /// <summary>
    /// Lấy lịch sử chat của user hiện tại
    /// </summary>
    [HttpGet("history")]
    public async Task<ActionResult> GetChatHistory([FromQuery] int page = 1, [FromQuery] int pageSize = 20)
    {
        try
        {
            var userId = _sessionManager.GetUserIdFromClaims(User);
            
            _logger.LogInformation($"Getting chat history for user {userId}");

            // Call AI service để lấy lịch sử theo user_id
            using var client = new HttpClient();
            var response = await client.GetAsync($"http://localhost:8000/user/{userId}/history?page={page}&pageSize={pageSize}");
            
            if (response.IsSuccessStatusCode)
            {
                var content = await response.Content.ReadAsStringAsync();
                return Ok(JObject.Parse(content));
            }
            else
            {
                return Ok(new { messages = new List<object>(), message = "No chat history found" });
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting chat history");
            return StatusCode(500, new { error = "Internal server error" });
        }
    }

    /// <summary>
    /// Xóa lịch sử chat của user hiện tại
    /// </summary>
    [HttpDelete("history")]
    public async Task<ActionResult> ClearChatHistory()
    {
        try
        {
            var userId = _sessionManager.GetUserIdFromClaims(User);
            
            _logger.LogInformation($"Clearing chat history for user {userId}");

            // Call AI service để xóa lịch sử theo user_id
            using var client = new HttpClient();
            var response = await client.DeleteAsync($"http://localhost:8000/user/{userId}/history");
            
            if (response.IsSuccessStatusCode)
            {
                return Ok(new { message = "Chat history cleared successfully" });
            }
            else
            {
                return Ok(new { message = "No chat history to clear" });
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error clearing chat history");
            return StatusCode(500, new { error = "Internal server error" });
        }
    }

    /// <summary>
    /// Health check cho AI service
    /// </summary>
    [HttpGet("health")]
    public async Task<ActionResult> HealthCheck()
    {
        try
        {
            using var client = new HttpClient();
            var response = await client.GetAsync("http://localhost:8000/health");
            
            if (response.IsSuccessStatusCode)
            {
                var content = await response.Content.ReadAsStringAsync();
                return Ok(new { 
                    status = "healthy", 
                    aiService = "connected",
                    aiServiceResponse = content 
                });
            }
            else
            {
                return Ok(new { 
                    status = "warning", 
                    aiService = "disconnected",
                    message = "AI Service not responding" 
                });
            }
        }
        catch (Exception ex)
        {
            return Ok(new { 
                status = "error", 
                aiService = "error",
                message = ex.Message 
            });
        }
    }
}
```

### 5. **Dependency Injection Setup**

```csharp
// Program.cs
var builder = WebApplication.CreateBuilder(args);

// Add services
builder.Services.AddControllers();
builder.Services.AddHttpClient();

// Register custom services
builder.Services.AddScoped<IAIChatService, AIChatService>();
builder.Services.AddScoped<ISessionManager, SessionManager>();

// Authentication (nếu dùng JWT)
builder.Services.AddAuthentication("Bearer")
    .AddJwtBearer("Bearer", options =>
    {
        options.Authority = "https://your-auth-server.com";
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateAudience = false
        };
    });

var app = builder.Build();

// Configure pipeline
if (app.Environment.IsDevelopment())
{
    app.UseDeveloperExceptionPage();
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();

app.Run();
```

### 6. **Configuration**

```json
// appsettings.json
{
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft.AspNetCore": "Warning"
    }
  },
  "AIService": {
    "BaseUrl": "http://localhost:8000",
    "Timeout": "00:00:30"
  },
  "AllowedHosts": "*"
}
```

## 🔄 Frontend Integration Examples

### **JavaScript/React**

```javascript
// Frontend call backend API
const chatWithAI = async (message) => {
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({ message })
        });

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Chat error:', error);
        return { status: 'error', error: error.message };
    }
};

// Continue conversation
const continueChat = async (sessionId, message) => {
    try {
        const response = await fetch(`/api/chat/continue/${sessionId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({ message })
        });

        return await response.json();
    } catch (error) {
        console.error('Continue chat error:', error);
        return { status: 'error', error: error.message };
    }
};
```

### **C# Client Example**

```csharp
// Nếu có service khác cần call chat API
public class ChatApiClient
{
    private readonly HttpClient _httpClient;

    public ChatApiClient(HttpClient httpClient)
    {
        _httpClient = httpClient;
    }

    public async Task<ChatResponse> SendMessageAsync(string message, string authToken)
    {
        _httpClient.DefaultRequestHeaders.Authorization = 
            new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", authToken);

        var request = new ChatRequest { Message = message };
        var json = JsonSerializer.Serialize(request);
        var content = new StringContent(json, Encoding.UTF8, "application/json");

        var response = await _httpClient.PostAsync("api/chat", content);
        var responseContent = await response.Content.ReadAsStringAsync();

        return JsonSerializer.Deserialize<ChatResponse>(responseContent);
    }
}
```

## 🚀 Cách AI Service nhận request từ Backend

### **Update AI Service để nhận user_id và session_id**

```python
# Trong main.py của AI service, update ChatRequest
class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None      # Backend sẽ gửi
    session_id: Optional[str] = None   # Backend sẽ gửi

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, http_request: Request):
    try:
        # Dùng user_id và session_id từ backend thay vì tự tạo
        user_id = request.user_id or f"anonymous_{str(uuid.uuid4())[:8]}"
        session_id = request.session_id or str(uuid.uuid4())
        
        # Process message với AI
        response_text = await chatbot_service.process_message(
            request.message, 
            user_id, 
            session_id
        )
        
        # Save to session (nếu cần)
        user_session_manager.save_message(session_id, request.message, response_text)
        
        return ChatResponse(
            response=response_text,
            status="success",
            user_id=user_id,
            session_id=session_id
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return ChatResponse(
            response="Xin lỗi, có lỗi xảy ra. Vui lòng thử lại.",
            status="error",
            error=str(e)
        )
```

## 📝 Tóm tắt Solution

### **Ưu điểm:**
1. ✅ **Đơn giản**: Backend chỉ cần call AI API
2. ✅ **Secure**: user_id từ authentication claims
3. ✅ **Flexible**: Có thể dùng session_id để continue conversation
4. ✅ **No Redis needed**: AI service tự quản lý state
5. ✅ **Easy to maintain**: Ít dependencies

### **Flow hoạt động (Đơn giản hơn):**
1. User đăng nhập → Backend có user_id trong JWT
2. Frontend gửi message → Backend
3. Backend lấy user_id từ claims
4. Backend call AI Service với message + user_id (không cần session_id)
5. AI Service lưu chat history theo user_id
6. AI Service xử lý và trả response
7. Backend forward response về Frontend

### **Khi nào cần Redis:**
- Chỉ cần Redis nếu muốn analytics hoặc backup
- Không bắt buộc cho basic chat functionality

Đây là solution tối thiểu và hiệu quả nhất cho backend C# của bạn!
