from rates.crawler import fetch_usd_rates_all_banks
import pandas as pd

print("Fetching rates...")
rates = fetch_usd_rates_all_banks()
print(f"Fetched {len(rates)} rates")
for r in rates:
    print(r)
