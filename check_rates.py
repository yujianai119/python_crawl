import requests
from bs4 import BeautifulSoup

def check_post():
    url = "https://ipost.post.gov.tw/mst/index.jsp?cmd=POS4002_1"
    try:
        resp = requests.get(url, timeout=10)
        print(f"POST: {resp.status_code}")
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            # Look for USD
            if "美元" in resp.text:
                print("POST: Found '美元'")
            else:
                print("POST: '美元' not found")
    except Exception as e:
        print(f"POST: Error {e}")

def check_tcb():
    url = "https://www.tcb-bank.com.tw/"
    try:
        resp = requests.get(url, timeout=10)
        print(f"TCB: {resp.status_code}")
        if resp.status_code == 200:
            if "美元" in resp.text:
                print("TCB: Found '美元'")
            else:
                print("TCB: '美元' not found")
    except Exception as e:
        print(f"TCB: Error {e}")

def check_cathay():
    url = "https://www.cathaybk.com.tw/cathaybk/personal/product/deposit/currency-billboard/"
    try:
        resp = requests.get(url, timeout=10)
        print(f"CATHAY: {resp.status_code}")
        if resp.status_code == 200:
            if "美元" in resp.text:
                print("CATHAY: Found '美元'")
            else:
                print("CATHAY: '美元' not found")
    except Exception as e:
        print(f"CATHAY: Error {e}")

def check_fubon():
    urls = [
        "https://www.fubon.com/banking/personal/deposit/foreign-currency/foreign-currency-rate/foreign-currency-rate",
        "https://www.fubon.com/banking/personal/deposit/foreign-currency/rate/rate.htm",
        "https://ebank.taipeifubon.com.tw/B2C/common/Index.faces"
    ]
    for url in urls:
        try:
            resp = requests.get(url, timeout=10)
            print(f"FUBON ({url}): {resp.status_code}")
            if resp.status_code == 200:
                if "美元" in resp.text:
                    print(f"FUBON: Found '美元' in {url}")
                    break
        except Exception as e:
            print(f"FUBON ({url}): Error {e}")

if __name__ == "__main__":
    check_post()
    check_tcb()
    check_cathay()
    check_fubon()
