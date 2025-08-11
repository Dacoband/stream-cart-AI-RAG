# Redis Integration & Backend API Design

## 🔥 Kiến trúc Redis cho Chat History

### Khi AI service đã dùng Redis:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   AI Service     │    │   Backend API   │
│                 │    │   (Python)       │    │   (.NET C#)     │
│   - Chat UI     │───►│   - Redis Chat   │───►│   - Redis User  │
│   - Auth        │    │   - Session Mgmt │    │   - Business    │
│                 │    │   - Context      │    │   - Products    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Redis Cache   │    │   SQL Database  │
                       │   - Chat Msgs   │    │   - User Data   │
                       │   - Sessions    │    │   - Orders      │
                       │   - Context     │    │   - Products    │
                       └─────────────────┘    └─────────────────┘
```

## 🚀 Câu trả lời cho câu hỏi:

### **Backend C# CÓ CẦN Redis cho lịch sử chat?**

**Câu trả lời: KHÔNG cần thiết, nhưng NÊN CÓ để tối ưu hiệu suất**

### Lý do:

#### ✅ **Không cần thiết vì:**
1. AI service đã quản lý chat history trong Redis
2. Backend có thể gọi API từ AI service để lấy lịch sử
3. Tránh duplicate data giữa 2 hệ thống

#### ✅ **Nên có để:**
1. **Caching**: Cache lịch sử chat cho truy cập nhanh
2. **Analytics**: Phân tích dữ liệu chat để cải thiện business
3. **Backup**: Backup lịch sử chat quan trọng
4. **Integration**: Dễ tích hợp với các service khác

## 🏗️ Thiết kế Backend C# API

### 1. **Redis Structure cho Backend**

```csharp
// Key patterns
"chat_history:{userId}:{sessionId}" -> List<ChatMessage>
"user_sessions:{userId}" -> Set<sessionId>
"chat_analytics:{date}" -> Hash<metric, value>
"user_preferences:{userId}" -> Hash<key, value>
```

### 2. **Models & DTOs**

```csharp
// Models/ChatModels.cs
public class ChatMessage
{
    public string MessageId { get; set; } = Guid.NewGuid().ToString();
    public string UserId { get; set; }
    public string SessionId { get; set; }
    public string UserMessage { get; set; }
    public string AiResponse { get; set; }
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
    public Dictionary<string, object> Metadata { get; set; } = new();
}

public class ChatSession
{
    public string SessionId { get; set; }
    public string UserId { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime LastActivity { get; set; }
    public int MessageCount { get; set; }
    public string Status { get; set; } // active, closed, archived
}

public class ChatHistoryRequest
{
    public int Page { get; set; } = 1;
    public int PageSize { get; set; } = 20;
    public DateTime? FromDate { get; set; }
    public DateTime? ToDate { get; set; }
    public string SessionId { get; set; }
}

public class ChatHistoryResponse
{
    public List<ChatMessage> Messages { get; set; }
    public int TotalCount { get; set; }
    public int CurrentPage { get; set; }
    public int TotalPages { get; set; }
    public ChatSession SessionInfo { get; set; }
}
```

### 3. **Redis Service**

```csharp
// Services/RedisChatService.cs
public interface IRedisChatService
{
    Task SaveChatMessageAsync(ChatMessage message);
    Task<ChatHistoryResponse> GetChatHistoryAsync(string userId, ChatHistoryRequest request);
    Task<List<ChatSession>> GetUserSessionsAsync(string userId);
    Task<ChatSession> GetSessionInfoAsync(string sessionId);
    Task ArchiveSessionAsync(string sessionId);
    Task DeleteChatHistoryAsync(string userId, string sessionId);
}

public class RedisChatService : IRedisChatService
{
    private readonly IDatabase _redis;
    private readonly ILogger<RedisChatService> _logger;
    
    public RedisChatService(IConnectionMultiplexer redis, ILogger<RedisChatService> logger)
    {
        _redis = redis.GetDatabase();
        _logger = logger;
    }

    public async Task SaveChatMessageAsync(ChatMessage message)
    {
        try
        {
            var key = $"chat_history:{message.UserId}:{message.SessionId}";
            var messageJson = JsonSerializer.Serialize(message);
            
            // Lưu message vào list
            await _redis.ListLeftPushAsync(key, messageJson);
            
            // Set TTL (30 days)
            await _redis.KeyExpireAsync(key, TimeSpan.FromDays(30));
            
            // Thêm session vào user sessions
            var userSessionsKey = $"user_sessions:{message.UserId}";
            await _redis.SetAddAsync(userSessionsKey, message.SessionId);
            
            // Update session info
            await UpdateSessionInfoAsync(message);
            
            _logger.LogInformation($"Saved chat message for user {message.UserId}, session {message.SessionId}");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, $"Error saving chat message for user {message.UserId}");
            throw;
        }
    }

    public async Task<ChatHistoryResponse> GetChatHistoryAsync(string userId, ChatHistoryRequest request)
    {
        try
        {
            var key = $"chat_history:{userId}:{request.SessionId}";
            
            // Get total count
            var totalCount = await _redis.ListLengthAsync(key);
            
            // Calculate pagination
            var skip = (request.Page - 1) * request.PageSize;
            var take = request.PageSize;
            
            // Get messages (Redis lists are LIFO, so we need to reverse)
            var messages = new List<ChatMessage>();
            var messageValues = await _redis.ListRangeAsync(key, skip, skip + take - 1);
            
            foreach (var messageValue in messageValues.Reverse())
            {
                var message = JsonSerializer.Deserialize<ChatMessage>(messageValue);
                
                // Apply date filters
                if (request.FromDate.HasValue && message.Timestamp < request.FromDate.Value)
                    continue;
                if (request.ToDate.HasValue && message.Timestamp > request.ToDate.Value)
                    continue;
                    
                messages.Add(message);
            }
            
            // Get session info
            var sessionInfo = await GetSessionInfoAsync(request.SessionId);
            
            return new ChatHistoryResponse
            {
                Messages = messages,
                TotalCount = (int)totalCount,
                CurrentPage = request.Page,
                TotalPages = (int)Math.Ceiling((double)totalCount / request.PageSize),
                SessionInfo = sessionInfo
            };
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, $"Error getting chat history for user {userId}");
            throw;
        }
    }

    public async Task<List<ChatSession>> GetUserSessionsAsync(string userId)
    {
        try
        {
            var userSessionsKey = $"user_sessions:{userId}";
            var sessionIds = await _redis.SetMembersAsync(userSessionsKey);
            
            var sessions = new List<ChatSession>();
            
            foreach (var sessionId in sessionIds)
            {
                var session = await GetSessionInfoAsync(sessionId);
                if (session != null)
                    sessions.Add(session);
            }
            
            return sessions.OrderByDescending(s => s.LastActivity).ToList();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, $"Error getting user sessions for {userId}");
            throw;
        }
    }

    public async Task<ChatSession> GetSessionInfoAsync(string sessionId)
    {
        try
        {
            var key = $"session_info:{sessionId}";
            var sessionData = await _redis.HashGetAllAsync(key);
            
            if (!sessionData.Any())
                return null;
                
            var sessionDict = sessionData.ToDictionary(x => x.Name, x => x.Value);
            
            return new ChatSession
            {
                SessionId = sessionId,
                UserId = sessionDict.GetValueOrDefault("userId"),
                CreatedAt = DateTime.Parse(sessionDict.GetValueOrDefault("createdAt")),
                LastActivity = DateTime.Parse(sessionDict.GetValueOrDefault("lastActivity")),
                MessageCount = int.Parse(sessionDict.GetValueOrDefault("messageCount", "0")),
                Status = sessionDict.GetValueOrDefault("status", "active")
            };
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, $"Error getting session info for {sessionId}");
            return null;
        }
    }

    private async Task UpdateSessionInfoAsync(ChatMessage message)
    {
        var key = $"session_info:{message.SessionId}";
        var now = DateTime.UtcNow.ToString("O");
        
        var sessionExists = await _redis.KeyExistsAsync(key);
        
        if (!sessionExists)
        {
            // Create new session
            await _redis.HashSetAsync(key, new HashEntry[]
            {
                new("sessionId", message.SessionId),
                new("userId", message.UserId),
                new("createdAt", now),
                new("lastActivity", now),
                new("messageCount", 1),
                new("status", "active")
            });
        }
        else
        {
            // Update existing session
            await _redis.HashSetAsync(key, new HashEntry[]
            {
                new("lastActivity", now)
            });
            await _redis.HashIncrementAsync(key, "messageCount");
        }
        
        // Set TTL
        await _redis.KeyExpireAsync(key, TimeSpan.FromDays(30));
    }

    public async Task ArchiveSessionAsync(string sessionId)
    {
        var key = $"session_info:{sessionId}";
        await _redis.HashSetAsync(key, "status", "archived");
    }

    public async Task DeleteChatHistoryAsync(string userId, string sessionId)
    {
        var chatKey = $"chat_history:{userId}:{sessionId}";
        var sessionKey = $"session_info:{sessionId}";
        var userSessionsKey = $"user_sessions:{userId}";
        
        await _redis.KeyDeleteAsync(chatKey);
        await _redis.KeyDeleteAsync(sessionKey);
        await _redis.SetRemoveAsync(userSessionsKey, sessionId);
    }
}
```

### 4. **API Controllers**

```csharp
// Controllers/ChatHistoryController.cs
[ApiController]
[Route("api/[controller]")]
[Authorize] // Require authentication
public class ChatHistoryController : ControllerBase
{
    private readonly IRedisChatService _chatService;
    private readonly ILogger<ChatHistoryController> _logger;

    public ChatHistoryController(IRedisChatService chatService, ILogger<ChatHistoryController> logger)
    {
        _chatService = chatService;
        _logger = logger;
    }

    /// <summary>
    /// Lấy lịch sử chat của user theo session
    /// </summary>
    [HttpGet("{userId}/sessions/{sessionId}")]
    public async Task<ActionResult<ChatHistoryResponse>> GetChatHistory(
        string userId, 
        string sessionId,
        [FromQuery] ChatHistoryRequest request)
    {
        try
        {
            // Verify user has access to this session
            if (!await VerifyUserAccess(userId, sessionId))
                return Forbid("Access denied to this chat session");

            request.SessionId = sessionId;
            var result = await _chatService.GetChatHistoryAsync(userId, request);
            
            if (result == null || !result.Messages.Any())
                return NotFound("Chat history not found");

            return Ok(result);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, $"Error getting chat history for user {userId}, session {sessionId}");
            return StatusCode(500, "Internal server error");
        }
    }

    /// <summary>
    /// Lấy tất cả sessions của user
    /// </summary>
    [HttpGet("{userId}/sessions")]
    public async Task<ActionResult<List<ChatSession>>> GetUserSessions(string userId)
    {
        try
        {
            // Verify current user can access this data
            if (!await VerifyCurrentUserAccess(userId))
                return Forbid("Access denied");

            var sessions = await _chatService.GetUserSessionsAsync(userId);
            return Ok(sessions);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, $"Error getting sessions for user {userId}");
            return StatusCode(500, "Internal server error");
        }
    }

    /// <summary>
    /// Lấy thông tin chi tiết của một session
    /// </summary>
    [HttpGet("sessions/{sessionId}")]
    public async Task<ActionResult<ChatSession>> GetSessionInfo(string sessionId)
    {
        try
        {
            var session = await _chatService.GetSessionInfoAsync(sessionId);
            
            if (session == null)
                return NotFound("Session not found");

            // Verify user has access
            if (!await VerifyUserAccess(session.UserId, sessionId))
                return Forbid("Access denied to this session");

            return Ok(session);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, $"Error getting session info for {sessionId}");
            return StatusCode(500, "Internal server error");
        }
    }

    /// <summary>
    /// Archive một chat session
    /// </summary>
    [HttpPatch("sessions/{sessionId}/archive")]
    public async Task<ActionResult> ArchiveSession(string sessionId)
    {
        try
        {
            var session = await _chatService.GetSessionInfoAsync(sessionId);
            if (session == null)
                return NotFound("Session not found");

            if (!await VerifyUserAccess(session.UserId, sessionId))
                return Forbid("Access denied");

            await _chatService.ArchiveSessionAsync(sessionId);
            return Ok(new { message = "Session archived successfully" });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, $"Error archiving session {sessionId}");
            return StatusCode(500, "Internal server error");
        }
    }

    /// <summary>
    /// Xóa chat history (GDPR compliance)
    /// </summary>
    [HttpDelete("{userId}/sessions/{sessionId}")]
    public async Task<ActionResult> DeleteChatHistory(string userId, string sessionId)
    {
        try
        {
            if (!await VerifyUserAccess(userId, sessionId))
                return Forbid("Access denied");

            await _chatService.DeleteChatHistoryAsync(userId, sessionId);
            return Ok(new { message = "Chat history deleted successfully" });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, $"Error deleting chat history for user {userId}, session {sessionId}");
            return StatusCode(500, "Internal server error");
        }
    }

    /// <summary>
    /// Sync chat message from AI service (webhook)
    /// </summary>
    [HttpPost("sync")]
    public async Task<ActionResult> SyncChatMessage([FromBody] ChatMessage message)
    {
        try
        {
            // Validate message
            if (string.IsNullOrEmpty(message.UserId) || string.IsNullOrEmpty(message.SessionId))
                return BadRequest("UserId and SessionId are required");

            await _chatService.SaveChatMessageAsync(message);
            return Ok(new { message = "Chat message synced successfully" });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error syncing chat message");
            return StatusCode(500, "Internal server error");
        }
    }

    private async Task<bool> VerifyUserAccess(string userId, string sessionId)
    {
        // Implement your access verification logic
        // Check if current authenticated user can access this data
        var currentUserId = User.FindFirst("userId")?.Value;
        return currentUserId == userId || User.IsInRole("Admin");
    }

    private async Task<bool> VerifyCurrentUserAccess(string userId)
    {
        var currentUserId = User.FindFirst("userId")?.Value;
        return currentUserId == userId || User.IsInRole("Admin");
    }
}
```

### 5. **Dependency Injection Setup**

```csharp
// Program.cs hoặc Startup.cs
public void ConfigureServices(IServiceCollection services)
{
    // Redis Configuration
    services.AddSingleton<IConnectionMultiplexer>(provider =>
    {
        var configuration = provider.GetService<IConfiguration>();
        var connectionString = configuration.GetConnectionString("Redis");
        return ConnectionMultiplexer.Connect(connectionString);
    });

    // Register Redis Chat Service
    services.AddScoped<IRedisChatService, RedisChatService>();

    // Other services...
    services.AddControllers();
    services.AddAuthentication();
    services.AddAuthorization();
}
```

### 6. **Configuration**

```json
// appsettings.json
{
  "ConnectionStrings": {
    "Redis": "localhost:6379",
    "DefaultConnection": "Server=...;Database=...;"
  },
  "ChatSettings": {
    "MaxHistoryDays": 30,
    "PageSize": 20,
    "MaxSessionsPerUser": 100
  }
}
```

## 🔄 Integration Flow

### 1. **AI Service → Backend Sync**

```csharp
// AI service gọi webhook sau mỗi chat
POST /api/chathistory/sync
{
    "messageId": "uuid",
    "userId": "user123",
    "sessionId": "session456",
    "userMessage": "Hello",
    "aiResponse": "Hi there!",
    "timestamp": "2024-01-01T10:00:00Z",
    "metadata": {
        "aiModel": "gemini-1.5-flash",
        "responseTime": 1.2,
        "confidence": 0.95
    }
}
```

### 2. **Frontend → Backend API**

```javascript
// Lấy lịch sử chat
const getChatHistory = async (userId, sessionId, page = 1) => {
    const response = await fetch(`/api/chathistory/${userId}/sessions/${sessionId}?page=${page}`);
    return response.json();
};

// Lấy tất cả sessions
const getUserSessions = async (userId) => {
    const response = await fetch(`/api/chathistory/${userId}/sessions`);
    return response.json();
};
```

## 📊 Monitoring & Analytics

```csharp
// Analytics Service
public class ChatAnalyticsService
{
    public async Task TrackChatMetrics(ChatMessage message)
    {
        var date = DateTime.UtcNow.ToString("yyyy-MM-dd");
        var key = $"chat_analytics:{date}";
        
        await _redis.HashIncrementAsync(key, "total_messages");
        await _redis.HashIncrementAsync(key, $"user_{message.UserId}_messages");
        await _redis.HashIncrementAsync(key, "ai_responses");
    }

    public async Task<Dictionary<string, int>> GetDailyStats(DateTime date)
    {
        var key = $"chat_analytics:{date:yyyy-MM-dd}";
        var stats = await _redis.HashGetAllAsync(key);
        return stats.ToDictionary(x => x.Name, x => (int)x.Value);
    }
}
```

## 🎯 Kết luận

### **Recommendation:**

1. **Backend C# NÊN dùng Redis** để:
   - Cache chat history cho performance
   - Analytics và monitoring
   - Backup và compliance (GDPR)

2. **Architecture pattern:**
   - AI Service: Primary chat storage + real-time processing
   - Backend C#: Secondary storage + business logic + analytics
   - Sync qua webhook hoặc message queue

3. **Benefits:**
   - Redundancy: Dữ liệu không bị mất
   - Performance: Fast access cho business features
   - Analytics: Business insights từ chat data
   - Compliance: GDPR deletion, data retention

Bạn có muốn tôi tạo thêm code examples cho phần nào không?