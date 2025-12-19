import os
import json
from rates.storage import read_cache
from streamlit_app import get_cached_rates

cache_file = "d:/Github/python_crawl/lesson7_1/data/rates_cache.json"

if os.path.exists(cache_file):
    os.remove(cache_file)
    print("Deleted cache file")

print("Calling get_cached_rates()...")
# We need to mock st.cache_data or just call the inner logic if possible.
# But get_cached_rates is decorated.
# Instead, let's just run the logic manually.

from rates.crawler import fetch_rates, fetch_usd_rates_all_banks
from rates.storage import write_cache

raw_rates = fetch_rates()
all_banks_usd = fetch_usd_rates_all_banks()

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

print(f"Writing cache with {len(formatted_rates)} rates and {len(all_banks_usd)} bank rates")
write_cache(formatted_rates, all_banks_usd)

# Now read it back
with open(cache_file, "r", encoding="utf-8") as f:
    data = json.load(f)
    print("Cache content keys:", data.keys())
    if "all_banks_usd" in data:
        print(f"all_banks_usd length: {len(data['all_banks_usd'])}")
    else:
        print("all_banks_usd MISSING")
