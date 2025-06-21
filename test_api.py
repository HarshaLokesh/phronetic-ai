#!/usr/bin/env python3
"""
Simple test script for the Personal Finance API
Run this after starting the API server
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_register():
    """Test user registration"""
    print("Testing user registration...")
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }
    
    response = requests.post(f"{API_BASE}/auth/register", json=user_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        print("User registered successfully!")
        return user_data
    else:
        print(f"Error: {response.json()}")
        return None

def test_login(user_data):
    """Test user login"""
    print("Testing user login...")
    login_data = {
        "username": user_data["username"],
        "password": user_data["password"]
    }
    
    response = requests.post(f"{API_BASE}/auth/login", data=login_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        token_data = response.json()
        print("Login successful!")
        return token_data["access_token"]
    else:
        print(f"Error: {response.json()}")
        return None

def test_create_transaction(token):
    """Test transaction creation"""
    print("Testing transaction creation...")
    headers = {"Authorization": f"Bearer {token}"}
    
    transaction_data = {
        "amount": 50.00,
        "description": "Test grocery purchase",
        "category": "Food",
        "transaction_type": "expense"
    }
    
    response = requests.post(f"{API_BASE}/transactions/", json=transaction_data, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        print("Transaction created successfully!")
        return response.json()["id"]
    else:
        print(f"Error: {response.json()}")
        return None

def test_get_transactions(token):
    """Test getting transactions"""
    print("Testing get transactions...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{API_BASE}/transactions/", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        transactions = response.json()
        print(f"Found {len(transactions)} transactions")
        return transactions
    else:
        print(f"Error: {response.json()}")
        return None

def test_currency_conversion(token):
    """Test currency conversion"""
    print("Testing currency conversion...")
    headers = {"Authorization": f"Bearer {token}"}
    
    params = {
        "amount": 100,
        "from_currency": "USD",
        "to_currency": "EUR"
    }
    
    response = requests.get(f"{API_BASE}/analytics/currency/convert", params=params, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Currency conversion: {result['original_amount']} {result['original_currency']} = {result['converted_amount']} {result['target_currency']}")
    else:
        print(f"Error: {response.json()}")

def test_data_transformation(token):
    """Test data transformation"""
    print("Testing data transformation...")
    headers = {"Authorization": f"Bearer {token}"}
    
    test_data = {
        "transactions": [
            {"amount": 100, "type": "income", "category": "Salary"},
            {"amount": 50, "type": "expense", "category": "Food"},
            {"amount": 30, "type": "expense", "category": "Transportation"}
        ]
    }
    
    params = {"transformation_type": "summarize"}
    
    response = requests.post(f"{API_BASE}/analytics/data/transform", json=test_data, params=params, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Data transformation result: {result['result']}")
    else:
        print(f"Error: {response.json()}")

def main():
    """Run all tests"""
    print("Starting API tests...")
    print("=" * 50)
    
    # Test health endpoint
    test_health()
    
    # Test registration
    user_data = test_register()
    if not user_data:
        print("Registration failed, skipping remaining tests")
        return
    
    # Test login
    token = test_login(user_data)
    if not token:
        print("Login failed, skipping remaining tests")
        return
    
    # Test transaction creation
    transaction_id = test_create_transaction(token)
    
    # Test getting transactions
    test_get_transactions(token)
    
    # Test currency conversion
    test_currency_conversion(token)
    
    # Test data transformation
    test_data_transformation(token)
    
    print("=" * 50)
    print("All tests completed!")

if __name__ == "__main__":
    main() 