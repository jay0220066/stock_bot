#yf_stork_v2 函數版

import os
import yfinance as yf
import pandas as pd

def stock_updata():
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
                old_df["Date"] = pd.to_datetime(old_df["Date"]).dt.date #tz_localize(None)  Date 欄位轉成 tz-naive
                
                dates = pd.to_datetime(old_df["Date"])
                dates = dates.sort_values()

                last_date = dates.iloc[-2] if len(dates) >= 2 else dates.max()
                # 從最後一日的前一天開始抓新資料（+1天避免重複）
                ticker = yf.Ticker(symbol)
                new_df = ticker.history(start=last_date).reset_index()
            
                new_df["Date"] = new_df["Date"].dt.date
                update_type = 1
            
            else:
                # 沒有舊檔案就抓完整歷史
                ticker = yf.Ticker(symbol)
                new_df = ticker.history(period="max").reset_index()
                old_df = pd.DataFrame()
            # 11800145 amd vol 測試抓取

            # 新增移動平均欄位
            combined = pd.concat([old_df, new_df]).drop_duplicates(subset=["Date"],keep="last").sort_values("Date")

            # 如果合併後仍然是空的無法抓取
            if combined.empty:
                print(f"{company} ({symbol}) → 無法抓取該內容")
                continue

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
            
    
    return "資料更新完成"

if __name__ == "__main__":
    stock_updata()