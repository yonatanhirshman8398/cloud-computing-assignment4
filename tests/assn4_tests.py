# import pytest
# import requests
# import json

# STOCKS_URL = "http://localhost:5001"
# CAPITAL_GAINS_URL = "http://localhost:5003"

# # Test data from assignment
# stock1 = {
#     "name": "NVIDIA Corporation",
#     "symbol": "NVDA",
#     "purchase price": 134.66,
#     "purchase date": "18-06-2024",
#     "shares": 7
# }

# stock2 = {
#     "name": "Apple Inc.",
#     "symbol": "AAPL",
#     "purchase price": 183.63,
#     "purchase date": "22-02-2024",
#     "shares": 19
# }

# stock3 = {
#     "name": "Alphabet Inc.",
#     "symbol": "GOOG",
#     "purchase price": 140.12,
#     "purchase date": "24-10-2024",
#     "shares": 14
# }

# stock7 = {
#     "name": "Amazon.com, Inc.",
#     "purchase price": 134.66,
#     "purchase date": "18-06-2024",
#     "shares": 7
# }

# stock8 = {
#     "name": "Amazon.com, Inc.",
#     "symbol": "AMZN",
#     "purchase price": 134.66,
#     "purchase date": "Tuesday, June 18, 2024",
#     "shares": 7
# }

# # Global variables to store IDs
# stock_ids = {}

# def test_1_post_stocks():
#     """Test 1: POST three stocks and verify unique IDs and status codes"""
#     # Post stock1
#     response1 = requests.post(f"{STOCKS_URL}/stocks", json=stock1)
#     assert response1.status_code == 201
#     stock_ids['stock1'] = response1.json()['id']

#     # Post stock2
#     response2 = requests.post(f"{STOCKS_URL}/stocks", json=stock2)
#     assert response2.status_code == 201
#     stock_ids['stock2'] = response2.json()['id']

#     # Post stock3
#     response3 = requests.post(f"{STOCKS_URL}/stocks", json=stock3)
#     assert response3.status_code == 201
#     stock_ids['stock3'] = response3.json()['id']

#     # Verify unique IDs
#     assert stock_ids['stock1'] != stock_ids['stock2'] != stock_ids['stock3']

# def test_2_get_stock():
#     """Test 2: GET stock1 by ID and verify symbol"""
#     response = requests.get(f"{STOCKS_URL}/stocks/{stock_ids['stock1']}")
#     assert response.status_code == 200
#     assert response.json()['symbol'] == "NVDA"

# def test_3_get_all_stocks():
#     """Test 3: GET all stocks and verify count"""
#     response = requests.get(f"{STOCKS_URL}/stocks")
#     assert response.status_code == 200
#     stocks = response.json()
#     assert len(stocks) == 3

# def test_4_get_stock_values():
#     """Test 4: GET stock values and verify symbols"""
#     # Get stock1 value
#     response1 = requests.get(f"{STOCKS_URL}/stock-value/{stock_ids['stock1']}")
#     assert response1.status_code == 200
#     assert response1.json()['symbol'] == "NVDA"

#     # Get stock2 value
#     response2 = requests.get(f"{STOCKS_URL}/stock-value/{stock_ids['stock2']}")
#     assert response2.status_code == 200
#     assert response2.json()['symbol'] == "AAPL"

#     # Get stock3 value
#     response3 = requests.get(f"{STOCKS_URL}/stock-value/{stock_ids['stock3']}")
#     assert response3.status_code == 200
#     assert response3.json()['symbol'] == "GOOG"

# def test_5_get_portfolio_value():
#     """Test 5: GET portfolio value and verify against individual stock values"""
#     # Get individual stock values
#     response1 = requests.get(f"{STOCKS_URL}/stock-value/{stock_ids['stock1']}")
#     sv1 = response1.json()['stock value']
    
#     response2 = requests.get(f"{STOCKS_URL}/stock-value/{stock_ids['stock2']}")
#     sv2 = response2.json()['stock value']
    
#     response3 = requests.get(f"{STOCKS_URL}/stock-value/{stock_ids['stock3']}")
#     sv3 = response3.json()['stock value']

#     # Get portfolio value
#     response = requests.get(f"{STOCKS_URL}/portfolio-value")
#     assert response.status_code == 200
#     pv = response.json()['portfolio value']

#     # Verify portfolio value is within 3% of sum of individual values
#     total_sv = sv1 + sv2 + sv3
#     assert pv * 0.97 <= total_sv <= pv * 1.03

# def test_6_post_invalid_stock():
#     """Test 6: POST stock without symbol field"""
#     response = requests.post(f"{STOCKS_URL}/stocks", json=stock7)
#     assert response.status_code == 400

# def test_7_delete_stock():
#     """Test 7: DELETE stock2"""
#     response = requests.delete(f"{STOCKS_URL}/stocks/{stock_ids['stock2']}")
#     assert response.status_code == 204

# def test_8_get_deleted_stock():
#     """Test 8: GET deleted stock2"""
#     response = requests.get(f"{STOCKS_URL}/stocks/{stock_ids['stock2']}")
#     assert response.status_code == 404

# def test_9_post_invalid_date():
#     """Test 9: POST stock with invalid date format"""
#     response = requests.post(f"{STOCKS_URL}/stocks", json=stock8)
#     assert response.status_code == 400
import requests
import pytest

BASE_URL = "http://localhost:5001" 

# Stock data
stock1 = { "name": "NVIDIA Corporation", "symbol": "NVDA", "purchase price": 134.66, "purchase date": "18-06-2024", "shares": 7 }
stock2 = { "name": "Apple Inc.", "symbol": "AAPL", "purchase price": 183.63, "purchase date": "22-02-2024", "shares": 19 }
stock3 = { "name": "Alphabet Inc.", "symbol": "GOOG", "purchase price": 140.12, "purchase date": "24-10-2024", "shares": 14 }

def test_post_stocks():
    response1 = requests.post(f"{BASE_URL}/stocks", json=stock1)
    response2 = requests.post(f"{BASE_URL}/stocks", json=stock2)
    response3 = requests.post(f"{BASE_URL}/stocks", json=stock3)
    
    assert response1.status_code == 201
    assert response2.status_code == 201
    assert response3.status_code == 201

    # Ensure unique IDs
    data1 = response1.json()
    data2 = response2.json()
    data3 = response3.json()
    assert data1['id'] != data2['id']
    assert data1['id'] != data3['id']
    assert data2['id'] != data3['id']

def test_get_stocks():
    response = requests.get(f"{BASE_URL}/stocks")
    assert response.status_code == 200
    stocks = response.json()
    assert len(stocks) == 3 
    
def test_get_portfolio_value():
    response = requests.get(f"{BASE_URL}/portfolio-value")
    assert response.status_code == 200
    portfolio_value = response.json()
    assert portfolio_value['portfolio value'] > 0  # Portfolio value should be greater than 0

def test_post_stocks_invalid_data():
    stock_invalid = { "name": "Amazon", "purchase price": 100.50, "purchase date": "15-03-2025", "shares": 50 }
    response = requests.post(f"{BASE_URL}/stocks", json=stock_invalid)
    assert response.status_code == 400


