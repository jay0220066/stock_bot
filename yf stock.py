import os
import yfinance as yf
import pandas as pd

# 讀取 stocklist
stocklist = pd.read_json("stocklist.json", typ="series")

# 逐一抓取並匯出
for company, symbol in stocklist.items():
    try:
        #抓取完整歷史股價
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="max").reset_index()

        #新增ma sam 
        hist["SMA_5"] = hist["Close"].rolling(window=5).mean()
        hist["SMA_10"] = hist["Close"].rolling(window=10).mean()
        hist["SMA_18"] = hist["Close"].rolling(window=18).mean()

        # 匯出成 JSON
        filename = os.path.join("data", f"{company}_{symbol}.json")
        hist.to_json(filename, orient="records", date_format="iso")

        print(f"已匯出 {company} ({symbol}) → {filename}")

    except Exception as e:
                print(f"抓取 {symbol} 失敗: {e}")
        




