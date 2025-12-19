import requests
import pandas as pd
from bs4 import BeautifulSoup
from typing import List, Dict, Any


def _count_cjk(text: str) -> int:
    if not text:
        return 0
    count = 0
    for ch in text:
        o = ord(ch)
        # Basic CJK Unified Ideographs range and some common extensions
        if (0x4E00 <= o <= 0x9FFF) or (0x3400 <= o <= 0x4DBF) or (0xF900 <= o <= 0xFAFF):
            count += 1
    return count


def _best_soup(content: bytes, encodings):
    best = None
    best_score = -1
    best_soup_obj = None
    for enc in encodings:
        try:
            html = content.decode(enc, errors="replace")
        except Exception:
            continue
        s = BeautifulSoup(html, "html.parser")
        # try to extract some currency texts as a heuristic
        nodes = s.select("td[data-table='幣別'] div.print_show")
        sample = " ".join(n.get_text("", strip=True) for n in nodes[:10])
        score = _count_cjk(sample)
        if score > best_score:
            best_score = score
            best = enc
            best_soup_obj = s
    return best_soup_obj, best


def fetch_rates(url: str = "https://rate.bot.com.tw/xrt?Lang=zh-TW") -> tuple[List[Dict[str, Any]], str]:
    """Simple requests + BeautifulSoup scraper.

    Returns tuple of (rates_list, update_time).
    """
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    content = resp.content
    # Try several likely encodings and pick the one with the most CJK chars in currency column
    encodings_to_try = [
        resp.encoding or "utf-8",
        resp.apparent_encoding or "utf-8",
        "utf-8",
        "big5",
        "cp950",
        "latin1",
    ]
    soup, used_enc = _best_soup(content, encodings_to_try)
    if soup is None:
        soup = BeautifulSoup(content, "html.parser")
    
    # 抓取更新時間
    update_time = None
    time_span = soup.find('span', class_='time')
    if time_span:
        update_time = time_span.get_text(strip=True)
    
    rows = []
    table = soup.find("table", attrs={"title": "牌告匯率"})
    if not table:
        return rows, update_time
    for tr in table.select("tr"):
        cols = tr.find_all("td")
        if not cols:
            continue
        # currency
        currency_node = tr.select_one("td[data-table='幣別'] div.print_show")
        currency = currency_node.get_text(strip=True) if currency_node else ""
        buy_node = tr.select_one("td[data-table='本行即期買入']")
        sell_node = tr.select_one("td[data-table='本行即期賣出']")
        buy = buy_node.get_text(strip=True) if buy_node else ""
        sell = sell_node.get_text(strip=True) if sell_node else ""
        rows.append({"幣別": currency, "本行即期買入": buy, "本行即期賣出": sell})
    return rows, update_time


def fetch_usd_rates_all_banks() -> List[Dict[str, Any]]:
    """Fetch USD rates for all banks from findrate.tw"""
    url = "https://www.findrate.tw/USD/"
    try:
        dfs = pd.read_html(url)
        if len(dfs) < 2:
            return []
        df = dfs[1] # Table 1 is usually the main table
        
        rates = []
        for _, row in df.iterrows():
            bank_name = row.get("銀行名稱", "")
            buy = row.get("即期買入", "")
            sell = row.get("即期賣出", "")
            
            # Convert to float or None
            try:
                buy = float(buy)
            except:
                buy = None
            try:
                sell = float(sell)
            except:
                sell = None
                
            rates.append({
                "bank": bank_name,
                "buy": buy,
                "sell": sell
            })
        return rates
    except Exception as e:
        print(f"Error fetching all banks: {e}")
        return []


def fetch_gold_price() -> Dict[str, Any]:
    """Fetch gold price from Taiwan Bank"""
    url = "https://rate.bot.com.tw/gold?Lang=zh-TW"
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        
        # 抓取更新時間
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.text, 'html.parser')
        update_time = None
        time_div = soup.find('div', class_='pull-left')
        if time_div:
            import re
            time_text = time_div.get_text(strip=True)
            # 提取時間格式: 2025/12/17 12:49
            time_match = re.search(r'(\d{4}/\d{1,2}/\d{1,2}\s+\d{1,2}:\d{2})', time_text)
            if time_match:
                update_time = time_match.group(1)
        
        # 使用 pandas 讀取表格
        from io import StringIO
        import re
        dfs = pd.read_html(StringIO(resp.text))
        
        if not dfs:
            return {"buy": None, "sell": None, "update_time": update_time}
        
        # 第一個表格就是黃金存摺價格表
        df = dfs[0]

        # 嘗試從表格中的「時間」欄抓最後一筆時間 (例如 15:19)
        try:
            time_col = None
            for col in df.columns:
                if isinstance(col, str) and '時間' in col:
                    time_col = col
                    break
            table_last_time = None
            if time_col is None:
                # 有些網站會用第一欄作為時間顯示
                first_col = df.columns[0]
                if isinstance(first_col, str) and '時間' in first_col:
                    time_col = first_col

            if time_col is not None:
                # 取出最後一個非空、符合 HH:MM 的欄位值
                for v in reversed(df[time_col].tolist()):
                    if pd.isna(v):
                        continue
                    s = str(v).strip()
                    m = re.search(r'(\d{1,2}:\d{2})', s)
                    if m:
                        table_last_time = m.group(1)
                        break

            # 若原先未從頁面文字取得日期時間，且表格有時間，則以今天日期補成 YYYY/MM/DD HH:MM
            if update_time is None and table_last_time:
                from datetime import datetime
                today = datetime.now().strftime('%Y/%m/%d')
                update_time = f"{today} {table_last_time}"
        except Exception:
            # best-effort, 不要讓解析錯誤影響價格擷取
            pass
        
        buy_price = None
        sell_price = None
        
        # 遍歷每一行，找到包含「本行賣出」和「本行買進」的行
        for idx, row in df.iterrows():
            # 將整行轉成字串檢查
            row_str = ' '.join([str(v) for v in row.values])
            
            # 找到「本行賣出」那一行，取得第三欄 (1 公克價格)
            if '本行賣出' in row_str:
                if len(row) >= 3:
                    val = str(row.iloc[2])
                    if pd.notna(val) and val != 'nan':
                        try:
                            # 從字串中提取第一個數字 (例如 "4407  買進" -> 4407)
                            match = re.search(r'\d+', val)
                            if match:
                                sell_price = float(match.group())
                        except Exception as e:
                            pass
            
            # 找到「本行買進」那一行，取得第三欄 (1 公克價格)
            if '本行買進' in row_str:
                if len(row) >= 3:
                    val = str(row.iloc[2])
                    if pd.notna(val) and val != 'nan':
                        try:
                            # 從字串中提取第一個數字 (例如 "4359  回售" -> 4359)
                            match = re.search(r'\d+', val)
                            if match:
                                buy_price = float(match.group())
                        except Exception as e:
                            pass
        
        return {"buy": buy_price, "sell": sell_price, "update_time": update_time}
    except Exception as e:
        print(f"Error fetching gold price: {e}")
        import traceback
        traceback.print_exc()
        return {"buy": None, "sell": None, "update_time": None}


__all__ = ["fetch_rates", "fetch_usd_rates_all_banks", "fetch_gold_price"]
