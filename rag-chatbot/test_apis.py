import asyncio
import requests
import json

# Test script to verify API endpoints and functionality

async def test_backend_api():
    """Test the backend API endpoints"""
    base_url = "https://brightpa.me"
    
    print("Testing backend API endpoints...")
    
    # Test products endpoint
    try:
        response = requests.get(f"{base_url}/api/products", timeout=10)
        print(f"Products API Status: {response.status_code}")
        if response.status_code == 200:
            products = response.json()
            print(f"Found {len(products)} products")
            if products:
                print("Sample product:", json.dumps(products[0], indent=2))
    except Exception as e:
        print(f"Error testing products API: {e}")
    
    # Test shops endpoint
    try:
        response = requests.get(f"{base_url}/api/shops", timeout=10)
        print(f"Shops API Status: {response.status_code}")
        if response.status_code == 200:
            shops = response.json()
            print(f"Found {len(shops)} shops")
            if shops:
                print("Sample shop:", json.dumps(shops[0], indent=2))
    except Exception as e:
        print(f"Error testing shops API: {e}")

def test_gemini_connection():
    """Test Gemini API connection"""
    try:
        import google.generativeai as genai
        
        # Configure the API key
        api_key = "AIzaSyCNX-OKoJkIICawnJCYoQoppbuxWcGAVjQ"
        genai.configure(api_key=api_key)
        
        # Create model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Test a simple query
        response = model.generate_content("Hello, please respond in Vietnamese: Xin chào!")
        print("Gemini API test successful!")
        print("Response:", response.text)
        
    except Exception as e:
        print(f"Error testing Gemini API: {e}")

if __name__ == "__main__":
    print("=== Testing Backend API ===")
    asyncio.run(test_backend_api())
    
    print("\n=== Testing Gemini API ===")
    test_gemini_connection()
