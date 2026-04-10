
# 📈 股票 LINE Bot

> 一個以 Python 打造的輕量級股票查詢 LINE Bot，整合 Yahoo Finance，支援即時查詢、自訂股票清單與自動資料更新，適合作為實務專案與系統設計展示。

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/status-active-success)
'''


## ✨ 功能特色

- 📊 即時股票價格查詢（Yahoo Finance）
- 🧠 自訂股票清單管理（stocklist.json）
- 🔄 自動更新歷史資料（JSON 儲存）
- 💬 LINE Bot 指令互動
- 📁 無資料庫設計（輕量、易部署）


---

## 📂 專案結構

```text
stock-line-bot/
│
├── data/                     # 股票歷史資料
├── stocklist.json            # 股票清單
├── updata_list.py            # 指令解析 / 股票管理
├── yf_stock_v2_1.py          # 股票資料抓取
├── line_bot.py               # LINE Webhook Server
├── requirements.txt
└── README.md
```

---

## 🚀 快速開始

### 1️⃣ 下載專案

```bash
git clone https://github.com/your-username/stock-line-bot.git
cd stock-line-bot
```

### 2️⃣ 安裝套件

```bash
pip install -r requirements.txt
```

### 3️⃣ 設定環境變數

建立 `.env` 檔案：

```env
LINE_CHANNEL_ACCESS_TOKEN=your_token
LINE_CHANNEL_SECRET=your_secret
```

### 4️⃣ 啟動服務

```bash
python line_bot.py
```

---

## 📡 LINE Bot 設定

1. 前往 LINE Developers Console
2. 建立 Messaging API Channel
3. 設定 Webhook URL：

```text
https://your-domain.com/callback
```

4. 開啟 Webhook 功能

---

## 💬 指令列表

| 指令             | 說明     |
| -------------- | ------ |
| 查/查詢            | 查詢股票列表 |
| 股價 台積電         | 查詢股票價格 |
| 股價 台積電         | 查詢股票價格 |
| 新增 台積電 2330.TW | 加入股票   |
| 刪除 台積電         | 移除股票   |
| 更新                | 更新股票資料   |

---

## 🔄 資料流程

```text
使用者輸入
   ↓
指令解析
   ↓
讀取 stocklist.json
   ↓
呼叫 yfinance API
   ↓
更新 /data JSON
   ↓
回傳結果給 LINE
```

---

## ⚠️ 已知問題

* ⏱️ LINE Webhook Timeout（同步請求過久）
* 📅 時區問題（tz-naive / tz-aware）
* 🔁 同日資料可能重複寫入
* 📉 Yahoo Finance 偶發錯誤

---

## 🛠️ 未來規劃

* [ ] 非同步處理（async / queue）
* [ ] 導入資料庫（SQLite / Redis）
* [ ] 技術指標（MA / RSI）
* [ ] AI 自然語言解析
* [ ] 程式交易推送

---

## 🧠 設計說明

### 為何使用 JSON 而非資料庫？

* 簡化架構（適合 MVP）
* 無需額外部署成本
* 易於除錯與維護


## 📦 套件需求

```txt
yfinance
pandas
flask
line-bot-sdk
python-dotenv
```

---

## 🤝 貢獻

歡迎提出 Issue 或 Pull Request 一起改進專案。

---

## 📄 License

MIT License

---

## 👨‍💻 作者

jay0220066 (Oscar)

---

## ⭐ 支持專案

如果這個專案對你有幫助，歡迎幫忙點個 Star ⭐

```
```

