import sys
sys.path.insert(0, 'd:\\Github\\python_crawl\\lesson7_1')

from rates.crawler import fetch_rates, fetch_usd_rates_all_banks, fetch_gold_price
from rates.storage import write_cache

print("正在抓取匯率資料...")
raw_rates = fetch_rates()
print(f"匯率資料: {len(raw_rates) if raw_rates else 0} 筆")

print("\n正在抓取各銀行美金匯率...")
all_banks_usd = fetch_usd_rates_all_banks()
print(f"各銀行美金: {len(all_banks_usd) if all_banks_usd else 0} 筆")

print("\n正在抓取黃金價格...")
gold_price = fetch_gold_price()
print(f"黃金價格: {gold_price}")

if raw_rates:
    formatted_rates = [
        {
            'currency': rate.get('幣別', '').split('(')[0].strip(),
            'name': rate.get('幣別', ''),
            'buy': float(rate.get('本行即期買入', '')),
            'sell': float(rate.get('本行即期賣出', ''))
        }
        for rate in raw_rates
        if rate.get('本行即期買入', '-') not in ('-', '')
        and rate.get('本行即期賣出', '-') not in ('-', '')
        and rate.get('幣別', '')
    ]
    
    print(f"\n格式化後匯率: {len(formatted_rates)} 筆")
    print("\n正在寫入快取...")
    write_cache(formatted_rates, all_banks_usd, gold_price)
    print("快取寫入完成!")
    
    # 驗證
    from rates.storage import read_cache
    cached = read_cache()
    print(f"\n快取驗證:")
    print(f"  - 匯率筆數: {len(cached.get('rates', []))}")
    print(f"  - 各銀行美金: {len(cached.get('all_banks_usd', []))}")
    print(f"  - 黃金價格: {cached.get('gold_price')}")
