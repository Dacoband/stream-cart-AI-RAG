#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify policies integration
"""

from policies import search_policy, get_purchase_policy, get_sales_policy

def test_policies():
    print("=== Testing Policy System ===\n")
    
    print("1. Testing search for 'chính sách mua hàng':")
    result1 = search_policy('chính sách mua hàng')
    print(result1[:300] + "...\n")
    
    print("2. Testing search for 'đổi trả':")
    result2 = search_policy('đổi trả')
    print(result2[:300] + "...\n")
    
    print("3. Testing search for 'mở shop':")
    result3 = search_policy('mở shop')
    print(result3[:300] + "...\n")
    
    print("✅ Policy integration test completed successfully!")

if __name__ == "__main__":
    test_policies()
