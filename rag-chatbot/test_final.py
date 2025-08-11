import requests
import json

def test_ai_with_shops():
    """Test AI service với câu hỏi về cửa hàng"""
    print("=== Test AI với câu hỏi về cửa hàng ===")
    try:
        response = requests.post('http://localhost:8000/chat', 
            json={'user_id': '123', 'message': 'Có những cửa hàng nào'})
        print(f'Status: {response.status_code}')
        if response.status_code == 200:
            result = response.json()
            print(f'AI Response: {result["response"]}')
        else:
            print(f'Error: {response.text}')
    except Exception as e:
        print(f'Error: {e}')

def test_ai_with_products():
    """Test AI service với câu hỏi về sản phẩm"""
    print("\n=== Test AI với câu hỏi về sản phẩm ===")
    try:
        response = requests.post('http://localhost:8000/chat', 
            json={'user_id': '123', 'message': 'Có những sản phẩm gì'})
        print(f'Status: {response.status_code}')
        if response.status_code == 200:
            result = response.json()
            print(f'AI Response: {result["response"]}')
        else:
            print(f'Error: {response.text}')
    except Exception as e:
        print(f'Error: {e}')

def test_ai_shops_endpoint():
    """Test AI service shops endpoint"""
    print("\n=== Test AI Service /shops endpoint ===")
    try:
        response = requests.get('http://localhost:8000/shops')
        print(f'Status: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'Shops count: {data.get("count", 0)}')
            print(f'First shop: {data.get("shops", [])[0] if data.get("shops") else "None"}')
        else:
            print(f'Error: {response.text}')
    except Exception as e:
        print(f'Error: {e}')

if __name__ == "__main__":
    test_ai_shops_endpoint()
    test_ai_with_shops()
    test_ai_with_products()
