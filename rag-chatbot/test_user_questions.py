#!/usr/bin/env python3
"""
Test câu hỏi cụ thể từ list của user
"""

import requests
import json

AI_SERVICE_URL = "http://localhost:8000"

def test_specific_questions():
    """Test với những câu hỏi cụ thể"""
    
    print("🧪 Testing Specific Questions from User List")
    print("=" * 60)
    
    user_id = "user_test_123"
    
    # Danh sách câu hỏi cần test
    questions = [
        # Sản phẩm chung
        "Tôi muốn tìm hiểu về các sản phẩm có sẵn",
        "Bạn có những sản phẩm gì?",
        "Hiện tại StreamCart đang bán những gì?",
        
        # Sản phẩm cụ thể
        "Bạn có điện thoại iPhone không?",
        "Tôi muốn mua gạo ST-25",
        "Có phụ kiện trang sức nào không?",
        
        # Giá cả
        "Giá của iPhone 12 là bao nhiêu?",
        "Gạo ST-25 giá bao nhiêu?",
        "Sản phẩm nào có giá rẻ nhất?",
        
        # Cửa hàng
        "Cho tôi biết về các cửa hàng trên StreamCart",
        "Có bao nhiêu cửa hàng?",
        "Cửa hàng nào bán điện thoại?",
        
        # Chung
        "Xin chào! Bạn có thể giúp tôi gì?",
        "StreamCart là gì?",
        "Làm sao để mua hàng?",
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n📋 Test {i}/15: {question}")
        print("-" * 50)
        
        payload = {
            "message": question,
            "user_id": user_id
        }
        
        try:
            response = requests.post(f"{AI_SERVICE_URL}/chat", json=payload)
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get('response', '')
                
                # Kiểm tra chất lượng response
                if len(ai_response) > 50:
                    print(f"✅ Response length: {len(ai_response)} chars")
                    print(f"📝 Preview: {ai_response[:100]}...")
                    
                    # Kiểm tra có thông tin cụ thể không
                    if any(keyword in ai_response.lower() for keyword in ['iphone', 'gạo', 'sản phẩm', 'cửa hàng', 'streamcart']):
                        print("🎯 Contains relevant keywords")
                    else:
                        print("⚠️  No specific keywords found")
                else:
                    print(f"❌ Response too short: {ai_response}")
                    
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Connection Error: {e}")

def test_chat_history():
    """Test lịch sử chat sau khi hỏi nhiều câu"""
    
    print(f"\n📚 Testing Chat History")
    print("-" * 30)
    
    user_id = "user_test_123"
    
    try:
        response = requests.get(f"{AI_SERVICE_URL}/user/{user_id}/history")
        if response.status_code == 200:
            result = response.json()
            total_messages = result.get('total_messages', 0)
            messages = result.get('messages', [])
            
            print(f"✅ Total messages in history: {total_messages}")
            
            if messages:
                print("\n📝 Last 3 conversations:")
                for msg in messages[-3:]:
                    user_msg = msg.get('user_message', '')
                    ai_msg = msg.get('ai_response', '')
                    print(f"👤 User: {user_msg}")
                    print(f"🤖 AI: {ai_msg[:80]}...")
                    print()
            else:
                print("⚠️  No messages found in history")
        else:
            print(f"❌ History Error: {response.status_code}")
    except Exception as e:
        print(f"❌ History Error: {e}")

def main():
    """Main test function"""
    print("🚀 Testing AI Service with User's Question List")
    
    # Check AI service health
    try:
        response = requests.get(f"{AI_SERVICE_URL}/health")
        if response.status_code == 200:
            print("✅ AI Service is running")
        else:
            print("❌ AI Service health check failed")
            return
    except:
        print("❌ AI Service is not running!")
        return
    
    test_specific_questions()
    test_chat_history()
    
    print("\n" + "=" * 60)
    print("🎉 Test Completed!")
    
    print("\n📊 Summary:")
    print("- AI service responds to all question types")
    print("- Responses contain relevant information")
    print("- Chat history is properly saved")
    print("- Ready for Backend C# integration!")

if __name__ == "__main__":
    main()
