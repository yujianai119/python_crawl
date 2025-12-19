"""Configuration settings for the exchange rate application."""

from pathlib import Path
from typing import Dict, Any

# Application paths
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
RATES_DIR = PROJECT_ROOT / "rates" / "data"
CACHE_FILE = DATA_DIR / "rates_cache.json"
SAMPLE_CACHE = DATA_DIR / "sample_cache.json"
LOG_FILE = RATES_DIR / "update.log"

# Application settings
APP_CONFIG = {
    "title": "台幣美元匯率轉換",
    "layout": "wide",
    "update_interval_seconds": 600,  # 10 minutes
    "max_cache_age_seconds": 600,
    "default_amount": 1000.0,
    "default_decimals": 0,
}

# Streamlit server settings
SERVER_CONFIG = {
    "port": 8501,
    "address": "localhost",
    "headless": True,
}

# UI text localization
UI_TEXT = {
    "table_controls": {
        "sort_ascending": "升序排列",
        "sort_descending": "降序排列",
        "format": "格式化",
        "autosize": "自動調整大小",
        "unpin_column": "取消固定欄位",
        "hide_column": "隱藏欄位",
        "search": "搜尋",
        "filter": "篩選",
        "download": "下載",
        "fullscreen": "全螢幕"
    }
}

# Exchange rate source settings
EXCHANGE_CONFIG = {
    "url": "https://rate.bot.com.tw/xrt?Lang=zh-TW",
    "encoding_fallbacks": ["utf-8", "big5", "cp950", "latin1"],
    "timeout_seconds": 10,
}

# Logging settings
LOG_CONFIG = {
    "format": "[{timestamp}] {level}: {message}",
    "encoding": "utf-8",
}

# UI text constants
UI_TEXT = {
    "converter_title": "匯率換算器",
    "rates_table_title": "匯率表", 
    "amount_label": "台幣金額 (NTD)",
    "decimals_label": "顯示小數位數",
    "target_label": "轉換貨幣",
    "estimate_label": "預估 {currency} 金額",
    "update_button": "手動更新",
    "last_updated": "最後更新：{time}",
    "no_tradeable": "目前無可交易的貨幣",
    "cannot_trade": "無法交易",
    "suspended_trading": "暫停交易",
    "update_complete": "更新完成",
    "update_failed": "更新失敗: {error}",
    "no_data_error": "無法取得匯率資料，請手動更新。",
    "offline_warning": "使用離線範例資料 (無網路或快取)。",
}

# Table column mappings
TABLE_COLUMNS = {
    "currency": "幣別",
    "buy": "本行即期買入", 
    "sell": "本行即期賣出",
    "tradeable": "可交易",
    "yes": "是",
    "no": "否",
}
