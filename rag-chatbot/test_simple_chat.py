#!/usr/bin/env python3
"""
Simple Test - No Session ID, Only User ID
Test chat flow với chỉ user_id, không cần session_id
"""

import requests
import json

# URLs
BACKEND_URL = "http://localhost:5000"  # Backend C# API  
AI_SERVICE_URL = "http://localhost:8000"  # AI Service

def test_simple_chat_flow():
    """Test chat flow đơn giản - chỉ user_id"""
    
    print("🧪 Testing Simple Chat Flow - No Session ID")
    print("=" * 60)
    
    # Mock user từ JWT
    user_id = "user_123"
    print(f"👤 Testing với User ID: {user_id}")
    
    # Test direct với AI Service
    print("\n📋 Test 1: Direct AI Service Call")
    print("-" * 40)
    
    messages = [
        "Xin chào! Tôi muốn hỏi về sản phẩm",
        "Có iPhone nào không?",
        "Giá iPhone 15 bao nhiêu?"
    ]
    
    for i, message in enumerate(messages, 1):
        print(f"\n💬 Message {i}: {message}")
        
        payload = {
            "message": message,
            "user_id": user_id
            # Không có session_id
        }
        
        try:
            response = requests.post(f"{AI_SERVICE_URL}/chat", json=payload)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ AI Response: {result.get('response', '')[:80]}...")
                print(f"👤 User ID: {result.get('user_id')}")
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Connection Error: {e}")
    
    # Test lấy lịch sử
    print(f"\n📋 Test 2: Get Chat History")
    print("-" * 40)
    
    try:
        response = requests.get(f"{AI_SERVICE_URL}/user/{user_id}/history")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Found {result.get('total_messages', 0)} messages")
            messages = result.get('messages', [])
            for msg in messages[-2:]:  # Show last 2
                print(f"  👤 User: {msg.get('user_message', '')}")
                print(f"  🤖 AI: {msg.get('ai_response', '')[:50]}...")
        else:
            print(f"❌ History Error: {response.status_code}")
    except Exception as e:
        print(f"❌ History Error: {e}")

def test_backend_api_simulation():
    """Mô phỏng Backend C# call AI service"""
    
    print("\n🔧 Backend C# API Simulation")
    print("=" * 40)
    
    # Mock JWT token
    mock_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyXzEyMyJ9.mock"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {mock_token}"
    }
    
    print("📤 Simulating Backend C# API calls:")
    
    # Simulate Backend logic
    user_id = "user_123"  # From JWT claims
    messages = [
        "Hello, tôi muốn mua iPhone",
        "Có model nào mới nhất không?"
    ]
    
    for message in messages:
        print(f"\n💻 Backend C# → AI Service")
        print(f"   User ID: {user_id} (from JWT)")
        print(f"   Message: {message}")
        
        # Backend C# gọi AI service
        payload = {
            "message": message,
            "user_id": user_id
        }
        
        try:
            response = requests.post(f"{AI_SERVICE_URL}/chat", json=payload)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ AI Response: {result.get('response', '')[:60]}...")
                
                # Backend C# trả về Frontend
                backend_response = {
                    "response": result.get('response'),
                    "status": result.get('status'),
                    "userId": result.get('user_id')
                }
                print(f"📱 Backend C# → Frontend: {backend_response}")
            else:
                print(f"❌ AI Service Error: {response.status_code}")
        except Exception as e:
            print(f"❌ Connection Error: {e}")

def test_chat_history_apis():
    """Test chat history endpoints"""
    
    print("\n📚 Testing Chat History APIs")
    print("=" * 40)
    
    user_id = "user_123"
    
    # Test get history
    print(f"📖 GET /user/{user_id}/history")
    try:
        response = requests.get(f"{AI_SERVICE_URL}/user/{user_id}/history?page=1&pageSize=5")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Total messages: {result.get('total_messages', 0)}")
            print(f"   Page: {result.get('page', 1)}/{result.get('total_pages', 1)}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test clear history
    print(f"\n🗑️  DELETE /user/{user_id}/history")
    try:
        response = requests.delete(f"{AI_SERVICE_URL}/user/{user_id}/history")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {result.get('message', 'History cleared')}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main test function"""
    print("🚀 Simple Chat Test - User ID Only")
    print("No Session ID needed! AI Service auto-manages sessions.")
    
    print("\n🔧 Requirements:")
    print("- AI Service running at http://localhost:8000")
    print("- No Backend C# required for this test")
    
    # Check AI service
    try:
        response = requests.get(f"{AI_SERVICE_URL}/health")
        if response.status_code == 200:
            print("✅ AI Service is running")
        else:
            print("❌ AI Service health check failed")
    except:
        print("❌ AI Service is not running!")
        print("Start with: python main.py")
        return
    
    # Run tests
    test_simple_chat_flow()
    test_backend_api_simulation()
    test_chat_history_apis()
    
    print("\n" + "=" * 60)
    print("🎉 Test Completed!")
    
    print("\n📝 Summary for Backend C# Developer:")
    print("✅ Chat: POST /chat with { message, user_id }")
    print("✅ History: GET /user/{user_id}/history")
    print("✅ Clear: DELETE /user/{user_id}/history")
    print("✅ No session_id needed!")
    
    print("\n🔧 Backend C# Implementation:")
    print("1. Get user_id from JWT claims")
    print("2. Call AI service with message + user_id")
    print("3. Return AI response to frontend")
    print("4. Use history endpoints if needed")

if __name__ == "__main__":
    main()
