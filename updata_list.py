import yfinance as yf
import json
import os
import pandas as pd
from get_stork import get_price
from yf_stock_v2_1 import stock_updata


FILE = "stocklist.json"
PRICE_DIR = "data"  # 股票 JSON 資料夾


# ======================
# 基礎：讀 / 寫
# ======================

def load_stock():
    if not os.path.exists(FILE):
        return {}
    try:
        with open(FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def save_stock(data):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ======================
# 功能：新增 / 刪除 / 查詢
# ======================

def add_stock(name, code):
    data = load_stock()
    result = ""
    if len(name) != len(code):
        return f"❌ 格式：加 名稱 代號"

    for i in range(len(name)):
        if name[i] in data or code[i] in data.values():
            result += f"{name[i]} 已存在 \n"
        else:

            '''
            stock = yf.Ticker(code[i])
            hist = stock.history(period="1d")
            if hist.empty:
                result += f"❌ 無法抓取 {name[i]} ({code[i]}) 的股價資料，不新增 \n"
                continue
            ''' 

            data[name[i]] = code[i]
            save_stock(data)

            result += f"✅ 已新增 {name[i]} ({code[i]})\n"
    
    return result


def remove_stock(name):
    data = load_stock()
    result = ""

    for i in range(0,len(name)):
        if name[i] not in data:
            if name[i] not in data.values():
                result += f"{name[i]} 不存在 \n"
            else:
                for k, v in data.items():
                    if v == name[i]:
                        key = k
                        data.pop(key)
                        result += f"🗑️ 已刪除 {key}\n"
                        break 
        else:
            data.pop(name[i])
            result += f"🗑️ 已刪除 {name[i]}\n"


    save_stock(data)

    return result


def list_stock():
    data = load_stock()

    if not data:
        return "📭 清單是空的"

    result = "📊 股票清單：\n"
    for name, code in data.items():
        result += f"- {name} ({code})\n"

    return result


# ======================
# 簡易自然語言解析
# ======================

def parse_command(text):
    text = text.strip()

    # 👉 新增
    if text.startswith("加"):
        parts = text.split()
        if len(parts) >= 3 and len(parts)%2 == 1:
            namelist = []
            codelist = []
            for i in range(0,(len(parts)-1)//2):
                namelist.append(parts[2*i+1])
                codelist.append(parts[2*i+2])
            return add_stock(namelist, codelist)
        else:
            return "❌ 格式：加 名稱 代號"

    # 👉 刪除
    elif text.startswith("刪"):
        parts = text.split()
        if len(parts) >= 2:
            parts = parts[1:]
            return remove_stock(parts)
        else:
            return "❌ 格式：刪 名稱or代號"

    # 👉 查詢清單
    elif text in ["查", "查詢", "list"]:
        return list_stock()

    # 👉 查股價
    elif text.startswith("股價"):
        parts = text.split()
        
        if len(parts) == 1:
            return "❌ 格式：股價 名稱or代號"
        
        data = load_stock()
        result = ""

        for i in range(1,len(parts)):
            key = ""
            value = ""

            if parts[i] in data :
                stock = parts[i] + "_" + data[parts[i]]
                result += get_price(stock)

            elif parts[i] in data.values():
                for k ,v in data.items():
                    if v == parts[i]:
                        stock =  k + "_" + v
                        result += get_price(stock)
            
            else:
                if parts[i] in data :
                    remove_stock(parts[i])
                    stock = parts[i] + "_" + data[parts[i]]
                    result += f"\n 沒有{name}的內容 請更新list或檢查輸入內容 \n \n"

                elif parts[i] in data.values():
                    for k ,v in data.items():
                        if v == parts[i]:
                            remove_stock(k)
                            stock =  k + "_" + v
                            result += f"\n 沒有{name}的內容 請更新list或檢查輸入內容 \n \n"
                
        return result
    
    elif text.startswith("更新"):   
        stock_updata()
        
        return "資料更新完成"
    

    return "❌ 無法辨識指令"


# ======================
# 主程式（CLI 測試用）
# ======================
'''
if __name__ == "__main__":
    print("📈 股票管理系統（輸入 exit 離開）")

    while True:
        cmd = input("👉 請輸入指令：")

        if cmd.lower() == "exit":
            break

        result = parse_command(cmd)
        print(result)
        
'''
print(parse_command("更新"))