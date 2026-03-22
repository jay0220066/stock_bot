import os
import yfinance as yf
import pandas as pd
import pyodbc
from datetime import datetime

# SQL Server 連線設定
conn = pyodbc.connect(
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=LAPTOP\\SQLEXPRESS;"
    "Database=StockDB;"
    "Trusted_Connection=yes;"
)
cursor = conn.cursor()

# 讀取 stocklist
stocklist = pd.read_json("stocklist.json", typ="series")

# 安全轉換 NaN → None
def safe_value(val):
    return None if pd.isna(val) else val

# log 檔案
log_file = "update_log.txt"

# 逐一抓取並匯出 + 匯入 SQL Server
for company, symbol in stocklist.items():
    try:
        filename = os.path.join("data", f"{company}_{symbol}.json")
        update_type = 0

        # 如果已有 JSON，先讀取舊資料
        if os.path.exists(filename):
            old_df = pd.read_json(filename)
            last_date = pd.to_datetime(old_df["Date"]).max()
            start_date = (last_date + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
            ticker = yf.Ticker(symbol)
            new_df = ticker.history(start=start_date).reset_index()
            update_type = 1
        else:
            ticker = yf.Ticker(symbol)
            new_df = ticker.history(period="max").reset_index()
            old_df = pd.DataFrame()

        # 合併並去重
        combined = pd.concat([old_df, new_df]).drop_duplicates(subset=["Date"]).sort_values("Date")

        # 確保 Date 欄位是 tz-naive
        combined["Date"] = pd.to_datetime(combined["Date"])
        if combined["Date"].dt.tz is not None:   # 如果有時區，轉成 tz-naive
            combined["Date"] = combined["Date"].dt.tz_convert(None)

        # 新增移動平均欄位
        combined["SMA_5"] = combined["Close"].rolling(window=5).mean()
        combined["SMA_10"] = combined["Close"].rolling(window=10).mean()
        combined["SMA_18"] = combined["Close"].rolling(window=18).mean()

        # 匯出成 JSON
        combined.to_json(filename, orient="records", date_format="iso")

        # 建立 SQL TABLE (以檔名為表格名)
        table_name = f"{company}_{symbol}"
        cursor.execute(f"""
        IF OBJECT_ID('{table_name}', 'U') IS NULL
        BEGIN
            CREATE TABLE [{table_name}] (
                Date DATE PRIMARY KEY,
                [Open] FLOAT,
                [High] FLOAT,
                [Low] FLOAT,
                [Close] FLOAT,
                [Volume] BIGINT NULL,
                [SMA_5] FLOAT NULL,
                [SMA_10] FLOAT NULL,
                [SMA_18] FLOAT NULL
            )
        END
        """)
        conn.commit()

        # 查 SQL Server 最後日期
        cursor.execute(f"SELECT MAX(Date) FROM [{table_name}]")
        result = cursor.fetchone()
        last_date_db = result[0]

        if last_date_db:
            last_date_db = pd.Timestamp(last_date_db)
            if last_date_db.tz is not None:   # 如果有時區，轉成 tz-naive
                last_date_db = last_date_db.tz_convert(None)
            new_rows = combined[combined["Date"] > last_date_db]
        else:
            new_rows = combined

        # 匯入新資料並統計筆數 (防止重複插入)
        insert_count = 0
        for _, row in new_rows.iterrows():
            cursor.execute(f"""
                INSERT INTO [{table_name}] (Date, [Open], [High], [Low], [Close], [Volume], [SMA_5], [SMA_10], [SMA_18])
                SELECT ?, ?, ?, ?, ?, ?, ?, ?, ?
                WHERE NOT EXISTS (SELECT 1 FROM [{table_name}] WHERE Date = ?)
            """,
            row["Date"],
            safe_value(row.get("Open")),
            safe_value(row.get("High")),
            safe_value(row.get("Low")),
            safe_value(row.get("Close")),
            safe_value(row.get("Volume")),
            safe_value(row.get("SMA_5")),
            safe_value(row.get("SMA_10")),
            safe_value(row.get("SMA_18")),
            row["Date"])
            insert_count += cursor.rowcount  # 只有成功插入才會算
        conn.commit()

        # 顯示結果
        if update_type == 1:
            msg = f"已更新 {company} ({symbol}) → {filename} 並增量同步到 SQL Server，共新增 {insert_count} 筆"
        else:
            msg = f"已新增 {company} ({symbol}) → {filename} 並匯入 SQL Server，共匯入 {insert_count} 筆"

        print(msg)

        # 寫入 log
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now()} - {msg}\n")

    except Exception as e:
        msg = f"抓取 {symbol} 失敗: {e}"
        print(msg)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now()} - {msg}\n")

cursor.close()
conn.close()
