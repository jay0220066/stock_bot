import os
import yfinance as yf
import pandas as pd
import pyodbc

# SQL Server 連線設定
conn = pyodbc.connect(
    "Driver={SQL Server};"
    "Server=LAPTOP\\SQLEXPRESS;"          # 改成你的 SQL Server 名稱或 IP
    "Database=StockDB;"          # 你的資料庫名稱
    "Trusted_Connection=yes;"    # 如果用 Windows 驗證
)
cursor = conn.cursor()

# 讀取 stocklist
stocklist = pd.read_json("stocklist.json", typ="series")

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
        
        '''
        # 只插入新資料
        if last_date_db is None:
            new_rows = combined
        else:
            new_rows = combined[combined["Date"] > last_date_db]
        '''     
        if last_date_db:
            last_date_db = pd.to_datetime(last_date_db).date()
            new_rows = combined[combined["Date"] > last_date_db]
        else:
            new_rows = combined

        for _, row in new_rows.iterrows():
            cursor.execute(f"""
                INSERT INTO [{table_name}] (Date, [Open], [High], [Low], [Close], [Volume], [SMA_5], [SMA_10], [SMA_18])
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            row["Date"], row.get("Open"), row.get("High"), row.get("Low"), row.get("Close"),
            row.get("Volume"), row.get("SMA_5"), row.get("SMA_10"), row.get("SMA_18"))
        conn.commit()

        if update_type == 1:
            print(f"已更新 {company} ({symbol}) → {filename} 並增量同步到 SQL Server")
        else:
            print(f"已新增 {company} ({symbol}) → {filename} 並匯入 SQL Server")

    except Exception as e:
        print(f"抓取 {symbol} 失敗: {e}")

cursor.close()
conn.close()
