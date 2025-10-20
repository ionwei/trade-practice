from flask import Flask, render_template, jsonify, request
import yfinance as yf
import pandas as pd

app = Flask(__name__)



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data', methods=["POST"])
def get_data():
    symbol = request.form.get("symbol")
    sma = int(request.form.get("sma"))
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period=f"{sma}d") 

    hist["SMA"] = hist["Close"].rolling(sma).mean()

    # 簡單策略：收盤價 > SMA 就買，否則賣
    hist["Signal"] = hist["Close"] > hist["SMA"]
    hist["Daily_Return"] = hist["Close"].pct_change()
    hist["Strategy_Return"] = hist["Daily_Return"] * hist["Signal"].shift(1)

    total_return = (1 + hist["Strategy_Return"].dropna()).prod() - 1
    total_return_pct = round(total_return * 100, 2)

    result = {
        "symbol": symbol,
        "sma": sma,
        "strategy_return": total_return_pct
    }
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
