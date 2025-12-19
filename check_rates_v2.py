import requests
from bs4 import BeautifulSoup
import pandas as pd

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def check_post():
    # Try the rate page directly if possible
    url = "https://ipost.post.gov.tw/mst/index.jsp?cmd=POS4002_1"
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        print(f"POST: {resp.status_code}")
        if resp.status_code == 200:
            # Check if it's a frame
            if "frame" in resp.text:
                print("POST: Found frames")
            # Try to find table
            try:
                dfs = pd.read_html(resp.text)
                if dfs:
                    print(f"POST: Found {len(dfs)} tables")
                    # Check if any table has currency info
                    for i, df in enumerate(dfs):
                        if "幣別" in str(df) or "Currency" in str(df) or "美元" in str(df):
                            print(f"POST: Table {i} looks relevant")
                            print(df.head())
            except Exception as e:
                print(f"POST: No tables found or error: {e}")
    except Exception as e:
        print(f"POST: Error {e}")

def check_tcb():
    url = "https://www.tcb-bank.com.tw/"
    try:
        resp = requests.get(url, headers=headers, timeout=20)
        print(f"TCB: {resp.status_code}")
        if resp.status_code == 200:
            if "美元" in resp.text:
                print("TCB: Found '美元'")
            else:
                print("TCB: '美元' not found")
    except Exception as e:
        print(f"TCB: Error {e}")

def check_fubon():
    url = "https://www.fubon.com/banking/personal/deposit/foreign-currency/foreign-currency-rate/foreign-currency-rate"
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        print(f"FUBON: {resp.status_code}")
        if resp.status_code == 200:
            if "美元" in resp.text:
                print("FUBON: Found '美元'")
            else:
                print("FUBON: '美元' not found")
                # print(resp.text[:500])
    except Exception as e:
        print(f"FUBON: Error {e}")

if __name__ == "__main__":
    print("--- POST ---")
    check_post()
    print("--- TCB ---")
    check_tcb()
    print("--- FUBON ---")
    check_fubon()
