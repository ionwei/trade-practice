from flask import Flask, render_template, jsonify, request
import os
import requests
import yfinance as yf
import pandas as pd

app = Flask(__name__)

FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data', methods=["POST"])
def get_data():
    symbol = request.form.get("symbol")
    sma = int(request.form.get("sma"))
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period=f"{sma*2}d") 

    hist["SMA"] = hist["Close"].rolling(sma).mean()

    # 簡單策略：收盤價 > SMA 就買，否則賣
    hist["Signal"] = hist["Close"] > hist["SMA"]
    hist["Daily_Return"] = hist["Close"].pct_change()
    hist["Strategy_Return"] = hist["Daily_Return"] * hist["Signal"].shift(1)

    total_return = (1 + hist["Strategy_Return"].dropna()).prod() - 1
    total_return_pct = round(total_return * 100, 2)
    print(hist["Strategy_Return"], total_return, total_return_pct)

    result = {
        "symbol": symbol,
        "sma": sma,
        "strategy_return": total_return_pct
    }
    return jsonify(result)

@app.route('/api/search_stock', methods=["POST"])
def search_stock():
    query = request.form.get("query", "").upper()
    if not query:
        return jsonify([])

    url = f"https://finnhub.io/api/v1/search?q={query}&token={FINNHUB_API_KEY}"
    response = requests.get(url)
    data = response.json()

    results = [
        {"symbol": item["symbol"], "name": item["description"]}
        for item in data.get("result", [])
    ]
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
