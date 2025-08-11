#!/usr/bin/env python3
"""
Demo script cho Backend-managed Sessions
Minh họa việc backend tự động xử lý user_id và session_id
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def print_separator(title):
    """In ra separator với title"""
    print("\n" + "="*60)
    print(f"🤖 {title}")
    print("="*60)

def chat_with_auth(message, auth_token=None, description=""):
    """Chat với authentication token"""
    print(f"\n👤 User: {message}")
    if description:
        print(f"📝 {description}")
    
    headers = {"Content-Type": "application/json"}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
        print(f"🔑 Auth Token: {auth_token}")
    else:
        print("🔑 No Auth Token (Anonymous)")
    
    payload = {"message": message}
    
    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"\n🤖 AI: {result['response']}")
            print(f"🆔 Backend assigned User ID: {result.get('user_id', 'N/A')}")
            print(f"💬 Backend assigned Session ID: {result.get('session_id', 'N/A')}")
            return result.get('session_id'), result.get('user_id')
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return None, None
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return None, None

def get_session_history(session_id):
    """Lấy lịch sử session"""
    try:
        response = requests.get(f"{BASE_URL}/session/{session_id}")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error getting session: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def get_user_sessions(user_id):
    """Lấy tất cả sessions của user"""
    try:
        response = requests.get(f"{BASE_URL}/user/{user_id}/sessions")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error getting user sessions: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    """Main demo function"""
    print("🚀 StreamCart AI Chatbot - Backend Session Management Demo")
    print("Backend tự động xử lý user_id và session_id")
    
    # Check if server is running
    try:
        health = requests.get(f"{BASE_URL}/health")
        if health.status_code == 200:
            health_data = health.json()
            print("✅ Server đang hoạt động!")
            print(f"📊 Active sessions: {health_data.get('active_sessions', 0)}")
        else:
            print("❌ Server không phản hồi")
            return
    except:
        print("❌ Không thể kết nối đến server. Vui lòng khởi chạy server trước.")
        return

    print_separator("DEMO 1: Anonymous User (Không có auth token)")
    session_id_1, user_id_1 = chat_with_auth(
        "Xin chào! Tôi muốn tìm hiểu về sản phẩm",
        description="Backend sẽ tạo anonymous user"
    )
    time.sleep(1)
    
    session_id_2, user_id_2 = chat_with_auth(
        "Có điện thoại iPhone nào không?",
        description="Tiếp tục chat với cùng anonymous user (session mới)"
    )
    time.sleep(1)

    print_separator("DEMO 2: Authenticated User 1")
    session_id_3, user_id_3 = chat_with_auth(
        "Tôi là user đã đăng nhập, muốn xem sản phẩm",
        auth_token="demo_token_123",
        description="User với authentication token"
    )
    time.sleep(1)
    
    session_id_4, user_id_4 = chat_with_auth(
        "Giá gạo ST-25 bao nhiêu?",
        auth_token="demo_token_123",
        description="Cùng user nhưng session mới"
    )
    time.sleep(1)

    print_separator("DEMO 3: Authenticated User 2")
    session_id_5, user_id_5 = chat_with_auth(
        "Xin chào, tôi là user khác",
        auth_token="demo_token_456",
        description="User khác với token khác"
    )
    time.sleep(1)

    print_separator("DEMO 4: Xem lịch sử Session")
    if session_id_3:
        print(f"📋 Lịch sử Session: {session_id_3}")
        history = get_session_history(session_id_3)
        if history:
            print(f"👤 User ID: {history['user_id']}")
            print(f"💬 Session ID: {history['session_id']}")
            print(f"📝 Số tin nhắn: {history['message_count']}")
            print("📜 Messages:")
            for i, msg in enumerate(history['messages'], 1):
                print(f"  {i}. User: {msg['user_message'][:50]}...")
                print(f"     AI: {msg['ai_response'][:50]}...")

    print_separator("DEMO 5: Xem tất cả Sessions của User")
    if user_id_3:
        print(f"👤 Tất cả sessions của User: {user_id_3}")
        user_sessions = get_user_sessions(user_id_3)
        if user_sessions:
            print(f"📊 Tổng số sessions: {user_sessions['total_sessions']}")
            for session in user_sessions['sessions']:
                print(f"  💬 Session: {session['session_id'][:16]}... ({session['message_count']} messages)")

    print_separator("DEMO HOÀN THÀNH")
    print("🎉 Demo Backend Session Management hoàn thành!")
    print("\n" + "="*60)
    print("📋 TÓM TẮT BACKEND SESSION MANAGEMENT:")
    print("="*60)
    print("✅ Backend tự động xử lý user_id từ Authorization header")
    print("✅ Backend tự động tạo session_id cho mỗi request")
    print("✅ Lưu trữ lịch sử chat trong memory (có thể chuyển sang database)")
    print("✅ API để xem session history và user sessions")
    print("✅ Frontend chỉ cần gửi message và auth token")
    print("\n🔧 Cách sử dụng:")
    print("1. Frontend gửi Authorization header với token")
    print("2. Backend tự động extract user_id từ token")
    print("3. Backend tự động tạo session_id mới")
    print("4. Backend trả về cả user_id và session_id cho frontend")
    print("5. Frontend có thể dùng session_id để xem lịch sử")

if __name__ == "__main__":
    main()
