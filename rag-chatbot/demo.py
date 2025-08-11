#!/usr/bin/env python3
"""
Demo script cho StreamCart AI Chatbot API
Minh họa các tính năng chính của chatbot
"""

import requests
import json
import time
import uuid  # Thêm để tạo session_id

BASE_URL = "http://localhost:8000"

def print_separator(title):
    """In ra separator với title"""
    print("\n" + "="*60)
    print(f"🤖 {title}")
    print("="*60)

def chat_demo(message, description="", user_id=None, session_id=None):
    """Demo chat function với user_id và session_id"""
    print(f"\n👤 User: {message}")
    if description:
        print(f"📝 {description}")
    
    # Tạo payload với hoặc không có user_id và session_id
    payload = {"message": message}
    
    if user_id:
        payload["user_id"] = user_id
        print(f"🆔 User ID: {user_id}")
    
    if session_id:
        payload["session_id"] = session_id
        print(f"💬 Session ID: {session_id}")
    
    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        if response.status_code == 200:
            result = response.json()
            print(f"\n🤖 AI: {result['response']}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")
    
    time.sleep(1)  # Pause between requests

def chat_demo_simple(message, description=""):
    """Demo chat function đơn giản - chỉ có message"""
    print(f"\n👤 User: {message}")
    if description:
        print(f"📝 {description}")
    
    try:
        response = requests.post(f"{BASE_URL}/chat", json={"message": message})
        if response.status_code == 200:
            result = response.json()
            print(f"\n🤖 AI: {result['response']}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")
    
    time.sleep(1)  # Pause between requests

def main():
    """Main demo function"""
    print("🚀 StreamCart AI Chatbot Demo")
    print("Đảm bảo server đang chạy tại http://localhost:8000")
    print("Để khởi chạy server: python main.py")
    
    # Check if server is running
    try:
        health = requests.get(f"{BASE_URL}/health")
        if health.status_code == 200:
            print("✅ Server đang hoạt động!")
        else:
            print("❌ Server không phản hồi")
            return
    except:
        print("❌ Không thể kết nối đến server. Vui lòng khởi chạy server trước.")
        return

    # Tạo user_id và session_id mẫu
    user_id = "user_12345"  # Giả sử lấy từ backend API
    session_id = str(uuid.uuid4())  # Tạo session mới cho cuộc chat
    
    print(f"\n📋 Demo với User ID: {user_id}")
    print(f"📋 Demo với Session ID: {session_id}")

    print_separator("DEMO 1: Chat đơn giản (chỉ message)")
    chat_demo_simple(
        "Xin chào! Bạn có thể giúp tôi gì?",
        "Test basic chat without user info"
    )

    print_separator("DEMO 2: Chat với User ID")
    chat_demo(
        "Tôi muốn tìm hiểu về các sản phẩm có sẵn",
        "Test chat with user identification",
        user_id=user_id
    )

    print_separator("DEMO 3: Chat với User ID + Session ID (Cuộc trò chuyện liên tục)")
    chat_demo(
        "Bạn có điện thoại iPhone nào không?",
        "Test chat with full session tracking",
        user_id=user_id,
        session_id=session_id
    )
    
    chat_demo(
        "Giá iPhone đó bao nhiêu?",
        "Continuing the conversation in same session",
        user_id=user_id,
        session_id=session_id
    )

    print_separator("DEMO 4: Chat session mới (Session ID khác)")
    new_session_id = str(uuid.uuid4())
    chat_demo(
        "Tôi muốn hỏi về gạo ST-25",
        "New conversation session",
        user_id=user_id,
        session_id=new_session_id
    )

    print_separator("DEMO 5: Mô phỏng user khác")
    another_user_id = "user_67890"
    another_session_id = str(uuid.uuid4())
    
    chat_demo(
        "Xin chào, tôi là người dùng mới",
        "Different user starting new conversation",
        user_id=another_user_id,
        session_id=another_session_id
    )

    print_separator("DEMO HOÀN THÀNH")
    print("🎉 Demo đã hoàn thành!")
    print("💡 Bạn có thể thử các câu hỏi khác bằng cách gọi trực tiếp API")
    print(f"📚 API Documentation: {BASE_URL}/docs")
    
    print("\n" + "="*60)
    print("📋 TỔNG KẾT VỀ USER_ID VÀ SESSION_ID:")
    print("="*60)
    print("👤 user_id: Nhận biết người dùng cụ thể")
    print("   - Từ backend API authentication")
    print("   - Để cá nhân hóa trải nghiệm")
    print("   - Theo dõi lịch sử chat của user")
    print()
    print("💬 session_id: Quản lý phiên chat")
    print("   - Tạo mới mỗi khi bắt đầu cuộc trò chuyện")
    print("   - UUID ngẫu nhiên: str(uuid.uuid4())")
    print("   - Giúp phân biệt các cuộc chat khác nhau")
    print("   - Hỗ trợ context trong conversation")

if __name__ == "__main__":
    main()
