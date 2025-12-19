import sys
sys.path.insert(0, 'd:\\Github\\python_crawl\\lesson7_1')

# 測試函數
from rates.crawler import fetch_gold_price

result = fetch_gold_price()
print(f"Result: {result}")
print(f"Buy price: {result.get('buy')}")
print(f"Sell price: {result.get('sell')}")
