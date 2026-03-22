import json
import os

FILE = "stocklist.json"


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

    # 防重複 code
    if code in data.values():
        return f"{code} 已存在"

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
# 簡易自然語言解析
# ======================

def parse_command(text):
    text = text.strip()

    # 👉 新增：加 台積電 2330.TW
    if text.startswith("加"):
        parts = text.split()

        if len(parts) >= 3:
            return add_stock(parts[1], parts[2])
        else:
            return "❌ 格式：加 名稱 代號"

    # 👉 刪除：刪 台積電
    elif text.startswith("刪"):
        parts = text.split()

        if len(parts) >= 2:
            return remove_stock(parts[1])
        else:
            return "❌ 格式：刪 名稱"

    # 👉 查詢：查 / 查詢 / list
    elif "查" in text or text.lower() == "list":
        return list_stock()

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