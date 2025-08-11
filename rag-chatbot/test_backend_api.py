#!/usr/bin/env python3
"""
Test API cho Backend C# - Simplified Session Management
Demo cách test API khi chỉ có 1 chat conversation per user
"""

import requests
import json

# Test URLs
BACKEND_URL = "http://localhost:5000"  # Backend C# API
AI_SERVICE_URL = "http://localhost:8000"  # AI Service

def test_chat_flow():
    """Test complete chat flow với session management"""
    
    print("🧪 Testing Chat Flow với Session Management")
    print("=" * 60)
    
    # Mock JWT token (trong thực tế sẽ có từ authentication)
    mock_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyXzEyMyIsIm5hbWUiOiJKb2huIERvZSJ9.mock"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {mock_token}"
    }
    
    print("📋 Test Case 1: First chat message")
    print("-" * 40)
    
    # Test 1: Gửi tin nhắn đầu tiên
    payload1 = {
        "message": "Xin chào! Tôi muốn tìm hiểu về sản phẩm iPhone"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/chat", json=payload1, headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Response: {result.get('response', '')[:100]}...")
            print(f"👤 User ID: {result.get('userId')}")
            print(f"🔗 Session ID: {result.get('sessionId')}")
            
            # Lưu session_id để test tiếp
            session_id = result.get('sessionId')
        else:
            print(f"❌ Error: {response.text}")
            return
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return
    
    print("\n📋 Test Case 2: Continue conversation")
    print("-" * 40)
    
    # Test 2: Tiếp tục cuộc trò chuyện
    payload2 = {
        "message": "Giá iPhone 15 Pro Max bao nhiêu?"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/chat", json=payload2, headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Response: {result.get('response', '')[:100]}...")
            print(f"🔗 Session ID: {result.get('sessionId')} (should be same as above)")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")
    
    print("\n📋 Test Case 3: Get chat history")
    print("-" * 40)
    
    # Test 3: Lấy lịch sử chat
    try:
        response = requests.get(f"{BACKEND_URL}/api/chat/history?page=1&pageSize=10", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            messages = result.get('messages', [])
            print(f"✅ Found {len(messages)} messages in history")
            for i, msg in enumerate(messages[-3:], 1):  # Show last 3 messages
                print(f"  {i}. User: {msg.get('user_message', '')}")
                print(f"     AI: {msg.get('ai_response', '')[:50]}...")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")

def test_direct_ai_service():
    """Test direct call to AI service để hiểu session management"""
    
    print("\n🔬 Testing Direct AI Service - Session Management")
    print("=" * 60)
    
    user_id = "user_123"
    session_id = f"user_{user_id}_main"  # Fixed session cho user
    
    print(f"👤 User ID: {user_id}")
    print(f"🔗 Session ID: {session_id} (fixed per user)")
    
    # Test messages
    messages = [
        "Xin chào! Tôi muốn hỏi về sản phẩm",
        "Có điện thoại iPhone nào không?",
        "Giá iPhone 15 bao nhiêu?"
    ]
    
    for i, message in enumerate(messages, 1):
        print(f"\n📨 Message {i}: {message}")
        
        payload = {
            "message": message,
            "user_id": user_id,
            "session_id": session_id  # Same session cho tất cả messages
        }
        
        try:
            response = requests.post(f"{AI_SERVICE_URL}/chat", json=payload)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ AI Response: {result.get('response', '')[:100]}...")
                print(f"🔗 Returned Session: {result.get('session_id')}")
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Connection Error: {e}")
    
    # Test lấy lịch sử từ AI service
    print(f"\n📋 Getting session history from AI service")
    try:
        response = requests.get(f"{AI_SERVICE_URL}/session/{session_id}")
        if response.status_code == 200:
            result = response.json()
            messages = result.get('messages', [])
            print(f"✅ Found {len(messages)} messages in AI service")
            for msg in messages[-2:]:  # Show last 2
                print(f"  - {msg.get('user_message', '')}")
                print(f"    → {msg.get('ai_response', '')[:50]}...")
        else:
            print(f"❌ History Error: {response.status_code}")
    except Exception as e:
        print(f"❌ History Connection Error: {e}")

def test_health_checks():
    """Test health của cả 2 services"""
    
    print("\n🏥 Health Checks")
    print("=" * 30)
    
    # Backend C# health
    try:
        response = requests.get(f"{BACKEND_URL}/api/chat/health")
        print(f"Backend C#: {response.status_code} - {response.json() if response.status_code == 200 else 'Error'}")
    except Exception as e:
        print(f"Backend C#: Connection Error - {e}")
    
    # AI Service health
    try:
        response = requests.get(f"{AI_SERVICE_URL}/health")
        print(f"AI Service: {response.status_code} - {response.json() if response.status_code == 200 else 'Error'}")
    except Exception as e:
        print(f"AI Service: Connection Error - {e}")

def main():
    """Main test function"""
    print("🚀 Backend C# API Test Suite")
    print("Test session management với 1 chat conversation per user")
    
    print("\n🔧 Setup Requirements:")
    print("1. Backend C# API running at http://localhost:5000")
    print("2. AI Service running at http://localhost:8000")
    print("3. Authentication configured (hoặc disable cho test)")
    
    test_health_checks()
    
    print("\n" + "="*60)
    print("💡 KEY CONCEPT - Session Management:")
    print("="*60)
    print("1. Mỗi USER chỉ có 1 CONVERSATION duy nhất")
    print("2. Session ID = 'user_{userId}_main'")
    print("3. Tất cả messages của user đều vào cùng 1 session")
    print("4. Lịch sử chat = lịch sử của session đó")
    print("5. Không cần track nhiều sessions")
    
    # Uncomment để test thực tế
    # test_direct_ai_service()
    # test_chat_flow()
    
    print("\n📋 API Endpoints for Testing:")
    print("-" * 40)
    print("POST /api/chat")
    print("  Body: { \"message\": \"Hello AI\" }")
    print("  Headers: Authorization: Bearer <token>")
    print()
    print("GET /api/chat/history?page=1&pageSize=10")
    print("  Headers: Authorization: Bearer <token>")
    print()
    print("DELETE /api/chat/history")
    print("  Headers: Authorization: Bearer <token>")
    print()
    print("GET /api/chat/health")

if __name__ == "__main__":
    main()
