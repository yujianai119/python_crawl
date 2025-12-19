import sys
sys.path.insert(0, 'd:\\Github\\python_crawl\\lesson7_1')

import requests
import pandas as pd
from io import StringIO

url = "https://rate.bot.com.tw/gold?Lang=zh-TW"
print(f"Fetching from: {url}")

resp = requests.get(url, timeout=15)
print(f"Status code: {resp.status_code}")

# 使用 StringIO 避免警告
dfs = pd.read_html(StringIO(resp.text))
print(f"Found {len(dfs)} tables")

for i, df in enumerate(dfs):
    print(f"\n=== Table {i} ===")
    print(df.head(10))
    print(f"Columns: {df.columns.tolist()}")
    print(f"Shape: {df.shape}")

# 測試原本的函數
from rates.crawler import fetch_gold_price
result = fetch_gold_price()
print(f"\nFinal result: {result}")
