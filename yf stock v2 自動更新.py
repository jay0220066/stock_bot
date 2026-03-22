import os
import yfinance as yf
import pandas as pd

# 讀取 stocklist
stocklist = pd.read_json("stocklist.json", typ="series")

# 逐一抓取並匯出
for company, symbol in stocklist.items():
    try:
        filename = os.path.join("data", f"{company}_{symbol}.json")
        update_type = 0

        # 如果已有 JSON，先讀取舊資料
        if os.path.exists(filename):
            old_df = pd.read_json(filename)
            last_date = pd.to_datetime(old_df["Date"]).max()
            # 從最後日期開始抓新資料（+1天避免重複）
            start_date = (last_date + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
            ticker = yf.Ticker(symbol)
            new_df = ticker.history(start=start_date).reset_index()
            update_type = 1
        
        else:
            # 沒有舊檔案就抓完整歷史
            ticker = yf.Ticker(symbol)
            new_df = ticker.history(period="max").reset_index()
            old_df = pd.DataFrame()

        # 新增移動平均欄位
        combined = pd.concat([old_df, new_df]).drop_duplicates(subset=["Date"]).sort_values("Date")
        combined["SMA_5"] = combined["Close"].rolling(window=5).mean()
        combined["SMA_10"] = combined["Close"].rolling(window=10).mean()
        combined["SMA_18"] = combined["Close"].rolling(window=18).mean()

        # 匯出成 JSON
        combined.to_json(filename, orient="records", date_format="iso")

        if update_type == 1:
            print(f"已更新 {company} ({symbol}) → {filename}")
        else:
            print(f"已新增 {company} ({symbol}) → {filename}")

    except Exception as e:
        print(f"抓取 {symbol} 失敗: {e}")
