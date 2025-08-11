import requests
import json

def test_ai_service():
    """Test AI service với câu hỏi về cửa hàng"""
    print("=== Testing AI Service ===")
    
    try:
        # Test với câu hỏi về cửa hàng
        response = requests.post('http://localhost:8000/chat', 
            json={'user_id': '123', 'message': 'Có những cửa hàng nào'})
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, ensure_ascii=False, indent=2)}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

def test_backend_api():
    """Test backend API trực tiếp"""
    print("\n=== Testing Backend API Direct ===")
    
    try:
        # Test shops endpoint
        response = requests.get('https://brightpa.me/api/shops')
        print(f"Shops API - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Shops count: {len(data.get('data', []))}")
            
        # Test products endpoint  
        response = requests.get('https://brightpa.me/api/products')
        print(f"Products API - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Products count: {len(data.get('data', []))}")
            
    except Exception as e:
        print(f"Backend API Exception: {e}")

def test_ai_shops_endpoint():
    """Test AI service shops endpoint"""
    print("\n=== Testing AI Service Shops Endpoint ===")
    
    try:
        response = requests.get('http://localhost:8000/shops')
        print(f"AI Shops - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"AI Shops response: {json.dumps(data, ensure_ascii=False, indent=2)}")
        else:
            print(f"AI Shops Error: {response.text}")
            
    except Exception as e:
        print(f"AI Shops Exception: {e}")

if __name__ == "__main__":
    test_backend_api()
    test_ai_shops_endpoint()
    test_ai_service()
