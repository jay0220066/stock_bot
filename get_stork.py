import os 
import json
import pandas as pd


# ======================
# 基礎：讀 / 寫
# ======================

def load_stockdata(filename):
    # 指定 data 資料夾路徑
    filename += ".json"
    filepath = os.path.join("data", filename)

    if not os.path.exists(filepath):
        return []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            # 確保讀到的是 dict
            return data 
    except (json.JSONDecodeError, OSError):
        return []
    

# ======================
#查詢股價
# ======================

def get_price(name):

    stock_data = load_stockdata(name)
    if not stock_data:
        return f"\n 沒有{name}的內容 請更新list或檢查輸入內容 \n \n"
    result = ""
    key = stock_data[-1]
    result = (
    f"{name}目前股價為 \n"
    f"最高:{key['High']:.2f}\n"
    f"最低:{key['Low']:.2f}\n"
    f"開盤:{key['Open']:.2f}\n"
    f"收盤:{key['Close']:.2f}\n"
    f"成交量:{key['Volume']}\n"
    f"SMA(18):{key['SMA_18']:.2f}\n")
    
    return result
    
#print(get_price('AMD_AMD')) #測試用


