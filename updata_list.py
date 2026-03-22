import yfinance as yf
import json
import os

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

    if name in data:
        return f"{name} 已存在"

    if code in data.values():
        return f"{code} 已存在"
    
    stock = yf.Ticker(code)
    hist = stock.history(period="1d")
    if hist.empty:
        return f"❌ 無法抓取 {name} ({code}) 的股價資料，不新增"

    data[name] = code
    save_stock(data)

    return f"✅ 已新增 {name} ({code})"


def remove_stock(name):
    data = load_stock()

    if name not in data:
        return f"{name} 不存在"

    data.pop(name)
    save_stock(data)

    return f"🗑️ 已刪除 {name}"


def list_stock():
    data = load_stock()

    if not data:
        return "📭 清單是空的"

    result = "📊 股票清單：\n"
    for name, code in data.items():
        result += f"- {name} ({code})\n"

    return result


# ======================
# 股價讀取
# ======================

def load_price(code):
    filepath = os.path.join(PRICE_DIR, f"{code}.json")
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None


# ======================
# 簡易自然語言解析
# ======================

def parse_command(text):
    text = text.strip()

    # 👉 新增
    if text.startswith("加"):
        parts = text.split()
        if len(parts) >= 3:
            return add_stock(parts[1], parts[2])
        elif len(parts) == 1:
            # 格式2：只輸入「加」
            name = input("👉 請輸入股票名稱：")
            code = input("👉 請輸入股票代號：")
            return add_stock(name, code)
        else:
            return "❌ 格式：加 名稱 代號"

    # 👉 刪除
    elif text.startswith("刪"):
        parts = text.split()
        if len(parts) >= 2:
            return remove_stock(parts[1])
        elif len(parts) == 1:
            # 格式2：只輸入「刪」
            name = input("👉 請輸入要刪除的股票名稱：")
            return remove_stock(name)
        else:
            return "❌ 格式：刪 名稱"

    # 👉 查詢清單
    elif text in ["查", "查詢", "list"]:
        return list_stock()

    # 👉 查股價
    elif text.startswith("股價"):
        parts = text.split()
        data = load_stock()

        if len(parts) >= 2:
            results = []
            for name in parts[1:]:
                if name not in data:
                    results.append(f"❌ {name} 不在清單中")
                    continue

                code = data[name]
                price = load_price(code)
                if not price:
                    results.append(f"❌ 沒有 {name} ({code}) 的股價資料")
                    continue

                results.append(
                    f"📈 {name} ({code}) 股價：開 {price['Open']} 高 {price['High']} 低 {price['Low']} 收 {price['Close']}"
                )
            return "\n".join(results)

        elif len(parts) == 1:
            # 格式2：只輸入「股價」
            name = input("👉 請輸入要查詢的股票名稱：")
            if name not in data:
                return f"❌ {name} 不在清單中"
            code = data[name]
            price = load_price(code)
            if not price:
                return f"❌ 沒有 {name} ({code}) 的股價資料"
            return f"📈 {name} ({code}) 股價：開 {price['Open']} 高 {price['High']} 低 {price['Low']} 收 {price['Close']}"

        else:
            return "❌ 格式：股價 名稱1 名稱2 ..."

    return "❌ 無法辨識指令"


# ======================
# 主程式（CLI 測試用）
# ======================

if __name__ == "__main__":
    print("📈 股票管理系統（輸入 exit 離開）")

    while True:
        cmd = input("👉 請輸入指令：")

        if cmd.lower() == "exit":
            break

        result = parse_command(cmd)
        print(result)
