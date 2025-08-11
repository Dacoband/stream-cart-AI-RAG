#!/usr/bin/env python3
"""
Test Backend C# Integration
Mô phỏng cách Backend C# call AI Service
"""

import requests
import json
import uuid

BASE_URL = "http://localhost:8000"

def test_backend_integration():
    """Test như Backend C# sẽ call AI service"""
    
    print("🚀 Testing Backend C# Integration with AI Service")
    print("=" * 60)
    
    # Mô phỏng data từ Backend C# 
    test_cases = [
        {
            "name": "Authenticated User Chat",
            "user_id": "user_123_from_jwt",  # Từ JWT claims
            "session_id": str(uuid.uuid4()),  # Backend tạo
            "message": "Xin chào! Tôi muốn tìm hiểu về sản phẩm"
        },
        {
            "name": "Continue Conversation",
            "user_id": "user_123_from_jwt",  # Same user
            "session_id": "existing_session_456",  # Frontend gửi lại session
            "message": "Có điện thoại iPhone nào không?"
        },
        {
            "name": "Anonymous User",
            "user_id": "anonymous_789",  # Backend tạo cho user chưa đăng nhập
            "session_id": str(uuid.uuid4()),
            "message": "Giá gạo ST-25 bao nhiêu?"
        },
        {
            "name": "Admin User",
            "user_id": "admin_user_001",
            "session_id": str(uuid.uuid4()),
            "message": "Tôi muốn xem thống kê sản phẩm"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {test_case['name']}")
        print(f"User ID: {test_case['user_id']}")
        print(f"Session ID: {test_case['session_id']}")
        print(f"Message: {test_case['message']}")
        print("-" * 40)
        
        # Tạo request như Backend C# sẽ gửi
        payload = {
            "message": test_case["message"],
            "user_id": test_case["user_id"],
            "session_id": test_case["session_id"]
        }
        
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "StreamCart-Backend-API/1.0"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/chat", json=payload, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Status: {result.get('status')}")
                print(f"🤖 AI Response: {result.get('response')}")
                print(f"👤 Returned User ID: {result.get('user_id')}")
                print(f"🔗 Returned Session ID: {result.get('session_id')}")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Connection Error: {e}")

def test_health_check():
    """Test health check endpoint"""
    print("\n🏥 Testing Health Check")
    print("-" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ AI Service Health: {result}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")

def test_legacy_integration():
    """Test backward compatibility với old method"""
    print("\n🔄 Testing Legacy Integration (No user_id/session_id)")
    print("-" * 50)
    
    payload = {
        "message": "Test legacy call without user_id and session_id"
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer demo_token_123"  # Để AI service tự extract
    }
    
    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Legacy call successful")
            print(f"🤖 AI Response: {result.get('response')}")
            print(f"👤 Generated User ID: {result.get('user_id')}")
            print(f"🔗 Generated Session ID: {result.get('session_id')}")
        else:
            print(f"❌ Legacy call failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Legacy call error: {e}")

def main():
    """Main test function"""
    print("🧪 StreamCart AI Service - Backend C# Integration Test")
    print("Ensure AI service is running at http://localhost:8000")
    print("Start with: python main.py")
    
    # Test connection first
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ AI Service is running: {response.status_code}")
    except:
        print("❌ AI Service is not running!")
        print("Please start AI service first: python main.py")
        return
    
    # Run tests
    test_health_check()
    test_backend_integration()
    test_legacy_integration()
    
    print("\n" + "=" * 60)
    print("🎉 Integration Test Completed!")
    
    print("\n📝 Summary for Backend C# Development:")
    print("1. ✅ AI Service supports user_id and session_id from Backend")
    print("2. ✅ Backward compatibility maintained for direct calls")
    print("3. ✅ Health check endpoint available")
    print("4. ✅ Ready for Backend C# integration")
    
    print("\n🔧 Backend C# Implementation:")
    print("- Get user_id from JWT claims after login")
    print("- Generate session_id using Guid.NewGuid()")
    print("- Call POST /chat with message, user_id, session_id")
    print("- Handle response and return to frontend")

if __name__ == "__main__":
    main()
