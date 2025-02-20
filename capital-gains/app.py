from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

STOCKS_URL = "http://stocks:8000"  # Updated URL to match the new stocks service

def get_stocks_from_service():
    try:
        response = requests.get(f"{STOCKS_URL}/stocks")
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def get_stock_value(stock_id):
    try:
        response = requests.get(f"{STOCKS_URL}/stock-value/{stock_id}")
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def calculate_capital_gains(stocks):
    total_gain = 0
    for stock in stocks:
        stock_value_data = get_stock_value(stock['id'])
        if stock_value_data:
            current_value = stock_value_data['stock value']
            purchase_value = float(stock['purchase price']) * float(stock['shares'])
            total_gain += current_value - purchase_value
    return total_gain

@app.route('/capital-gains', methods=['GET'])
def get_capital_gains():
    try:
        shares_gt = request.args.get('numsharesgt')
        shares_lt = request.args.get('numshareslt')
        
        # Get all stocks
        stocks = get_stocks_from_service()
        filtered_stocks = stocks
            
        # Apply share filters
        if shares_gt:
            shares_gt = int(shares_gt)
            filtered_stocks = [s for s in filtered_stocks if s['shares'] > shares_gt]
            
        if shares_lt:
            shares_lt = int(shares_lt)
            filtered_stocks = [s for s in filtered_stocks if s['shares'] < shares_lt]
            
        # Calculate gains for filtered stocks
        total_gain = calculate_capital_gains(filtered_stocks)
            
        return jsonify(round(total_gain, 2))
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)  # Changed port to 8080