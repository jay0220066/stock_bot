import os
import yfinance as yf
import pandas as pd
import pyodbc
from datetime import datetime

# ====== SQL Server 連線 ======
conn = pyodbc.connect(
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=LAPTOP\\SQLEXPRESS;"
    "Database=StockDB;"
    "Trusted_Connection=yes;"
)
cursor = conn.cursor()
cursor.fast_executemany = True

# ====== stocklist ======
stocklist = pd.read_json("stocklist.json", typ="series")

def safe_value(val):
    return None if pd.isna(val) else val

log_file = "update_log.txt"

for company, symbol in stocklist.items():
    try:
        filename = os.path.join("data", f"{company}_{symbol}.json")
        update_type = 0

        # ====== 舊資料 ======
        if os.path.exists(filename):
            old_df = pd.read_json(filename)

            if not old_df.empty:
                old_df["Date"] = pd.to_datetime(old_df["Date"], utc=True).dt.tz_convert(None)

                last_date = old_df["Date"].max()
                start_date = (last_date + pd.Timedelta(days=1)).strftime("%Y-%m-%d")

                ticker = yf.Ticker(symbol)
                new_df = ticker.history(start=start_date).reset_index()

                update_type = 1
            else:
                new_df = pd.DataFrame()
        else:
            ticker = yf.Ticker(symbol)
            new_df = ticker.history(period="max").reset_index()
            old_df = pd.DataFrame()

        # ====== 新資料處理 ======
        if not new_df.empty:
            new_df["Date"] = pd.to_datetime(new_df["Date"], utc=True).dt.tz_convert(None)

        # ====== 合併（只給 JSON / 指標用）=====
        combined = pd.concat([old_df, new_df]) \
            .drop_duplicates(subset=["Date"]) \
            .sort_values("Date")

        # ====== 技術指標 ======
        combined["SMA_5"] = combined["Close"].rolling(5).mean()
        combined["SMA_10"] = combined["Close"].rolling(10).mean()
        combined["SMA_18"] = combined["Close"].rolling(18).mean()

        # ====== 存 JSON ======
        combined.to_json(filename, orient="records", date_format="iso")

        # ====== 建立 SQL Table ======
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

        # ====== 只抓 DB 最後日期 ======
        cursor.execute(f"SELECT MAX(Date) FROM [{table_name}]")
        result = cursor.fetchone()
        last_date_db = result[0]

        if not new_df.empty:
            if last_date_db:
                last_date_db = pd.Timestamp(last_date_db)
                new_rows = new_df[new_df["Date"] > last_date_db]
            else:
                new_rows = new_df
        else:
            new_rows = pd.DataFrame()

        # 🔥 防重（重要）
        if not new_rows.empty:
            new_rows = new_rows.drop_duplicates(subset=["Date"])

        # ====== INSERT（只寫 new_df）=====
        insert_count = 0

        for _, row in new_rows.iterrows():
            try:
                cursor.execute(f"""
                    INSERT INTO [{table_name}]
                    (Date, [Open], [High], [Low], [Close], [Volume], [SMA_5], [SMA_10], [SMA_18])
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                row["Date"],
                safe_value(row.get("Open")),
                safe_value(row.get("High")),
                safe_value(row.get("Low")),
                safe_value(row.get("Close")),
                safe_value(row.get("Volume")),
                safe_value(row.get("SMA_5")),
                safe_value(row.get("SMA_10")),
                safe_value(row.get("SMA_18"))
                )

                insert_count += 1

            except Exception:
                # 🔥 如果重複就跳過（最穩）
                continue

        conn.commit()

        # ====== LOG ======
        if update_type == 1:
            msg = f"已更新 {company} ({symbol}) → 新增 {insert_count} 筆"
        else:
            msg = f"已新增 {company} ({symbol}) → 匯入 {insert_count} 筆"

        print(msg)

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now()} - {msg}\n")

    except Exception as e:
        msg = f"抓取 {symbol} 失敗: {e}"
        print(msg)

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now()} - {msg}\n")

cursor.close()
conn.close()