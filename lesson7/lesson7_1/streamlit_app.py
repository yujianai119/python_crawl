import streamlit as st
import asyncio
import json
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
import time

# 匯率爬蟲 schema
SCHEMA = {
    "name": "匯率資訊",
    "baseSelector": "table[title='牌告匯率'] tr",
    "fields": [
        {"name": "幣別", "selector": "td[data-table='幣別'] div.print_show", "type": "text"},
        {"name": "現金本行買入", "selector": "td[data-table='本行現金買入']", "type": "text"},
        {"name": "現金本行賣出", "selector": "td[data-table='本行現金賣出']", "type": "text"},
        {"name": "即期本行買入", "selector": "td[data-table='本行即期買入']", "type": "text"},
        {"name": "即期本行賣出", "selector": "td[data-table='本行即期賣出']", "type": "text"},
    ]
}

RATE_URL = 'https://rate.bot.com.tw/xrt?Lang=zh-TW'

@st.cache_data(ttl=600, show_spinner=False)
def fetch_rates():
    async def _fetch():
        strategy = JsonCssExtractionStrategy(SCHEMA)
        run_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            extraction_strategy=strategy
        )
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=RATE_URL, config=run_config)
            data = json.loads(result.extracted_content)
            # 過濾無法交易的貨幣（即所有買入/賣出都為空）
            filtered = [item for item in data if any(item[k] and item[k].strip() for k in ["現金本行買入", "現金本行賣出", "即期本行買入", "即期本行賣出"])]
            return filtered
    return asyncio.run(_fetch())

st.set_page_config(page_title="台幣匯率轉換", layout="wide")
st.title("台幣匯率轉換工具")

# 手動更新按鈕
if st.button("手動更新匯率", type="primary"):
    st.cache_data.clear()
    st.experimental_rerun()

rates = fetch_rates()

col1, col2 = st.columns(2)

with col1:
    st.header("台幣轉換為其它貨幣")
    amount = st.number_input("請輸入台幣金額", min_value=1, value=1000)
    currency = st.selectbox("選擇幣別", [item["幣別"] for item in rates])
    # 取該幣別的即期本行賣出
    selected = next((item for item in rates if item["幣別"] == currency), None)
    rate = selected["即期本行賣出"] if selected else None
    if not rate or not rate.strip():
        st.warning("暫停交易")
    else:
        try:
            rate_val = float(rate.replace(',', ''))
            st.success(f"{amount} 台幣 ≈ {amount / rate_val:.4f} {currency}")
        except Exception:
            st.warning("匯率格式錯誤")

with col2:
    st.header("匯率表格")
    # 顯示表格，空值顯示暫停交易
    def show(val):
        return val if val and val.strip() else "暫停交易"
    show_rates = [
        {
            "幣別": item["幣別"],
            "現金本行買入": show(item["現金本行買入"]),
            "現金本行賣出": show(item["現金本行賣出"]),
            "即期本行買入": show(item["即期本行買入"]),
            "即期本行賣出": show(item["即期本行賣出"]),
        }
        for item in rates
    ]
    st.dataframe(show_rates, use_container_width=True)

st.caption("每10分鐘自動更新，亦可手動更新。資料來源：台灣銀行牌告匯率")
