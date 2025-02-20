from flask import Flask, request, jsonify
import requests
from datetime import datetime
import uuid
import re
import os
from flask_pymongo import PyMongo

app = Flask(__name__)

# MongoDB Configuration - using local MongoDB container
app.config["MONGO_URI"] = "mongodb://mongodb:27017/stocks"
mongo = PyMongo(app)
stocks_collection = mongo.db.stocks  # Changed from stocks1/stocks2 to just stocks

API_KEY = 'uqvOjCmoGxE3Sf5GCDH/Ow==wXlU5zxyTCawpavs'

# All the helper functions and route handlers remain exactly the same
def get_stock_price(symbol):
    url = f"https://api.api-ninjas.com/v1/stockprice?ticker={symbol}"
    headers = {'X-Api-Key': API_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"API response code {response.status_code}")
    data = response.json()
    return round(float(data['price']), 2)

def validate_date_format(date_str):
    """
    Validate date string is in DD-MM-YYYY format and represents a valid date
    """
    if not isinstance(date_str, str):
        return False
        
    if date_str == 'NA':
        return True
        
    try:
        # Check format using regex
        if not re.match(r'^(0[1-9]|[12][0-9]|3[01])-(0[1-9]|1[0-2])-\d{4}$', date_str):
            return False
            
        # Validate it's a real date
        datetime.strptime(date_str, '%d-%m-%Y')
        return True
        
    except (ValueError, TypeError):
        return False

def validate_stock_data(data, require_id=False):
    """
    Validate stock data with strict type checking and value validation
    Returns False if any validation fails
    """
    try:
        # Validate ID if required
        if require_id:
            if 'id' not in data:
                return False
            if not isinstance(data['id'], str):
                return False
            if not data['id'].strip():  # Check if ID is not empty string
                return False
                
        # Validate symbol
        if 'symbol' not in data:
            return False
        if not isinstance(data['symbol'], str):
            return False
        if not data['symbol'].strip():  # Check if symbol is not empty string
            return False
            
        # Validate purchase price
        if 'purchase price' not in data:
            return False
        try:
            price = float(data['purchase price'])
            if price <= 0:  # Price must be positive
                return False
            # Check if it's not infinity or NaN
            if not isinstance(price, (int, float)) or not str(price).replace('.','').isdigit():
                return False
        except (TypeError, ValueError):
            return False
            
        # Validate shares
        if 'shares' not in data:
            return False
        try:
            shares = int(float(data['shares']))  # Convert through float to handle "100.0"
            if shares <= 0:  # Shares must be positive
                return False
            if shares != float(data['shares']):  # Must be whole number
                return False
        except (TypeError, ValueError):
            return False
            
        # Validate optional fields
        if 'purchase date' in data:
            if not isinstance(data['purchase date'], str):
                return False
            if not validate_date_format(data['purchase date']):
                return False
                
        if 'name' in data:
            if not isinstance(data['name'], str):
                return False
                
        return True
        
    except Exception:
        return False

def validate_stock_update(data, id):
    """
    Additional validation for stock updates
    """
    try:
        # Validate basic stock data first
        if not validate_stock_data(data, require_id=True):
            return False
            
        # Ensure ID matches
        if data['id'] != id:
            return False
            
        # Ensure all required fields are present for update
        required_fields = ['id', 'name', 'symbol', 'purchase price', 'purchase date', 'shares']
        if not all(field in data for field in required_fields):
            return False
            
        return True
        
    except Exception:
        return False

def filter_stocks(query_params):
    """Filter stocks based on query parameters"""
    filter_criteria = {}
    
    for field, value in query_params.items():
        if field in ['purchase price', 'shares']:
            try:
                value = float(value) if field == 'purchase price' else int(value)
                filter_criteria[field] = value
            except (ValueError, TypeError):
                continue
        elif field in ['id', 'name', 'symbol', 'purchase date']:
            filter_criteria[field] = {'$regex': f'^{value}$', '$options': 'i'}
            
    return list(stocks_collection.find(filter_criteria, {'_id': 0}))

@app.route('/stocks', methods=['POST'])
def create_stock():
    try:
        if not request.is_json:
            return jsonify({"error": "Expected application/json media type"}), 415
        
        try:
            data = request.get_json()
        except Exception:
            return jsonify({"error": "Malformed data"}), 400
            
        if not validate_stock_data(data, require_id=False):
            return jsonify({"error": "Malformed data"}), 400
            
        # Check for duplicate symbol
        if stocks_collection.find_one({'symbol': data['symbol'].upper()}):
            return jsonify({"error": "Malformed data"}), 400
            
        stock_id = str(uuid.uuid4())
        
        stock = {
            'id': stock_id,
            'name': data.get('name', 'NA'),
            'symbol': data['symbol'].upper(),
            'purchase price': round(float(data['purchase price']), 2),
            'purchase date': data.get('purchase date', 'NA'),
            'shares': int(float(data['shares']))
        }
        
        stocks_collection.insert_one(stock)
        return jsonify({'id': stock_id}), 201
        
    except Exception as e:
        return jsonify({"server error": str(e)}), 500

@app.route('/stocks', methods=['GET'])
def get_stocks():
    try:
        if request.args:
            filtered_results = filter_stocks(request.args)
            return jsonify(filtered_results), 200
            
        stocks = list(stocks_collection.find({}, {'_id': 0}))
        return jsonify(stocks), 200
    except Exception as e:
        return jsonify({"server error": str(e)}), 500

@app.route('/stocks/<string:id>', methods=['GET'])
def get_stock(id):
    try:
        stock = stocks_collection.find_one({'id': id}, {'_id': 0})
        if not stock:
            return jsonify({"error": "Not found"}), 404
            
        return jsonify(stock), 200
        
    except Exception as e:
        return jsonify({"server error": str(e)}), 500

@app.route('/stocks/<string:id>', methods=['PUT'])
def update_stock(id):
    try:
        if not stocks_collection.find_one({'id': id}):
            return jsonify({"error": "Not found"}), 404
            
        if not request.is_json:
            return jsonify({"error": "Expected application/json media type"}), 415
            
        try:
            data = request.get_json()
        except Exception:
            return jsonify({"error": "Malformed data"}), 400
            
        if not validate_stock_update(data, id):
            return jsonify({"error": "Malformed data"}), 400
            
        stock = {
            'id': id,
            'name': data['name'],
            'symbol': data['symbol'].upper(),
            'purchase price': round(float(data['purchase price']), 2),
            'purchase date': data['purchase date'],
            'shares': int(float(data['shares']))
        }
        
        stocks_collection.replace_one({'id': id}, stock)
        return jsonify({'id': id}), 200
        
    except Exception as e:
        return jsonify({"server error": str(e)}), 500

@app.route('/stocks/<string:id>', methods=['DELETE'])
def delete_stock(id):
    try:
        result = stocks_collection.delete_one({'id': id})
        if result.deleted_count == 0:
            return jsonify({"error": "Not found"}), 404
        
        return '', 204
        
    except Exception as e:
        return jsonify({"server error": str(e)}), 500

@app.route('/stock-value/<string:id>', methods=['GET'])
def get_stock_value(id):
    try:
        stock = stocks_collection.find_one({'id': id}, {'_id': 0})
        if not stock:
            return jsonify({"error": "Not found"}), 404
        
        current_price = get_stock_price(stock['symbol'])
        stock_value = round(current_price * stock['shares'], 2)
        
        return jsonify({
            'symbol': stock['symbol'],
            'ticker': current_price,
            'stock value': stock_value
        }), 200
        
    except Exception as e:
        if 'API response code' in str(e):
            return jsonify({"server error": str(e)}), 500
        return jsonify({"server error": str(e)}), 500

@app.route('/portfolio-value', methods=['GET'])
def get_portfolio_value():
    try:
        total_value = 0
        stocks = stocks_collection.find({}, {'_id': 0})
        for stock in stocks:
            current_price = get_stock_price(stock['symbol'])
            total_value += current_price * stock['shares']
        
        return jsonify({
            'date': datetime.now().strftime('%d-%m-%Y'),
            'portfolio value': round(total_value, 2)
        }), 200
        
    except Exception as e:
        if 'API response code' in str(e):
            return jsonify({"server error": str(e)}), 500
        return jsonify({"server error": str(e)}), 500

@app.route('/kill', methods=['GET'])
def kill_container():
    os._exit(1)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)  # Changed port to 8000