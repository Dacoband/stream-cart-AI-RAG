import requests
import json

# Test client cho StreamCart AI Chatbot API

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test health check endpoint"""
    print("=== Testing Health Check ===")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_chat_about_products():
    """Test chatbot với câu hỏi về sản phẩm"""
    print("\n=== Testing Chat About Products ===")
    try:
        payload = {
            "message": "Tôi muốn tìm hiểu về các sản phẩm có sẵn",
            "user_id": "test_user_001"
        }
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {result['response']}")
            print(f"Status: {result['status']}")
        else:
            print(f"Error: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_chat_about_shops():
    """Test chatbot với câu hỏi về cửa hàng"""
    print("\n=== Testing Chat About Shops ===")
    try:
        payload = {
            "message": "Bạn có thể cho tôi biết về các cửa hàng không?",
            "user_id": "test_user_001"
        }
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {result['response']}")
            print(f"Status: {result['status']}")
        else:
            print(f"Error: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_general_chat():
    """Test chatbot với câu hỏi chung"""
    print("\n=== Testing General Chat ===")
    try:
        payload = {
            "message": "Xin chào! Bạn có thể giúp tôi gì?",
            "user_id": "test_user_001"
        }
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {result['response']}")
            print(f"Status: {result['status']}")
        else:
            print(f"Error: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_products_endpoint():
    """Test products endpoint"""
    print("\n=== Testing Products Endpoint ===")
    try:
        response = requests.get(f"{BASE_URL}/products")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Found {result['count']} products")
            if result['products']:
                print(f"Sample product: {json.dumps(result['products'][0], indent=2)}")
        else:
            print(f"Error: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_shops_endpoint():
    """Test shops endpoint"""
    print("\n=== Testing Shops Endpoint ===")
    try:
        response = requests.get(f"{BASE_URL}/shops")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Found {result['count']} shops")
            if result['shops']:
                print(f"Sample shop: {json.dumps(result['shops'][0], indent=2)}")
        else:
            print(f"Error: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 StreamCart AI Chatbot API Test Suite")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health_check),
        ("Products Endpoint", test_products_endpoint),
        ("Shops Endpoint", test_shops_endpoint),
        ("General Chat", test_general_chat),
        ("Chat About Products", test_chat_about_products),
        ("Chat About Shops", test_chat_about_shops),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        try:
            success = test_func()
            results.append((test_name, success))
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"Result: {status}")
        except Exception as e:
            print(f"❌ FAIL - Exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:<25} {status}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The chatbot API is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()
