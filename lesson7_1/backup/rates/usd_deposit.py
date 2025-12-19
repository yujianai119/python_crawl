import requests
import pandas as pd
from bs4 import BeautifulSoup
from typing import List, Dict, Any

def fetch_usd_deposit_rates(url: str = "https://www.cardu.com.tw/news/detail.php?nt_pk=6&ns_pk=38413") -> List[Dict[str, Any]]:
    """爬取台灣各銀行美元定存利率表格"""
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    # 找到標題為「美元定存利率比較表」的表格
    table = None
    for t in soup.find_all("table"):
        if t.find(string=lambda s: s and "美元定存利率比較表" in s):
            table = t
            break
    if table is None:
        # fallback: 取第一個有6欄的表
        for t in soup.find_all("table"):
            if t.find_all("tr") and len(t.find_all("tr")[0].find_all(["td","th"])) >= 6:
                table = t
                break
    if table is None:
        return []
    # 解析表格
    df = pd.read_html(str(table))[0]
    # 標準化欄位
    df.columns = [str(c).strip() for c in df.columns]
    # 只保留有銀行欄
    if "銀行" not in df.columns:
        return []
    # 轉成 dict list
    result = []
    for _, row in df.iterrows():
        result.append({
            "銀行": row.get("銀行"),
            "1個月": row.get("1個月") or row.get("1月"),
            "3個月": row.get("3個月"),
            "6個月": row.get("6個月"),
            "9個月": row.get("9個月"),
            "1年": row.get("1年") or row.get("一年")
        })
    return result
