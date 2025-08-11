import requests
import json

print('=== Checking Backend APIs ===')

# Test shops
print('Shops API:')
try:
    response = requests.get('https://brightpa.me/api/shops')
    print(f'Status: {response.status_code}')
    data = response.json()
    print(f'Response: {json.dumps(data, ensure_ascii=False, indent=2)}')
except Exception as e:
    print(f'Error: {e}')

print()
print('=' * 50)

# Test products  
print('Products API:')
try:
    response = requests.get('https://brightpa.me/api/products')
    print(f'Status: {response.status_code}')
    data = response.json()
    print(f'Response type: {type(data)}')
    if isinstance(data, dict):
        print(f'Keys: {list(data.keys())}')
        if 'data' in data:
            products = data['data']
            print(f'Products count: {len(products)}')
            if products:
                print(f'First product: {json.dumps(products[0], ensure_ascii=False, indent=2)}')
    elif isinstance(data, list):
        print(f'Products count: {len(data)}')
        if data:
            print(f'First product: {json.dumps(data[0], ensure_ascii=False, indent=2)}')
except Exception as e:
    print(f'Error: {e}')
