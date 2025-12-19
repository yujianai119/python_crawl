"""
台幣匯率轉換應用 - 高速優化版本
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, List
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import json
import os

from rates.crawler import fetch_rates, fetch_usd_rates_all_banks, fetch_gold_price
from rates.storage import write_cache, read_cache, is_expired














# （檔案略長，已複製主要內容）
ndef render_thermometer(rate_data: Dict[str, Any], currency: str) -> None:
    """渲染溫度計，樣式與附件保持一致"""
    buy_rate = rate_data.get("buy", 0)
    sell_rate = rate_data.get("sell", 0)
    
    if not buy_rate or not sell_rate:
        return
    
    avg_rate = (buy_rate + sell_rate) / 2
    
    # 簡化範圍計算
    ranges = {
        "USD": (28, 35), "美金": (28, 35),
        "JPY": (0.15, 0.25), "日圓": (0.15, 0.25),
        "EUR": (32, 40), "歐元": (32, 40)
    }
    
    min_val, max_val = ranges.get(currency.split()[0], (avg_rate * 0.8, avg_rate * 1.2))
    percentage = max(0, min(100, (avg_rate - min_val) / (max_val - min_val) * 100))
    
    # 快速顏色判斷
    color = "#FF6B35" if percentage > 70 else "#FFB347" if percentage > 30 else "#87CEEB"
    status = "高溫" if percentage > 70 else "中溫" if percentage > 30 else "低溫"
    
    # 簡化版溫度計，適用於中間欄
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 15px;
        color: white;
        text-align: center;
        margin: 10px 0;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
    ">
        <div style="font-size: 14px; font-weight: 600; margin-bottom: 10px;">🔗 {currency.split()[0]} 溫度計</div>
        
        <!-- 大數字顯示 -->
        <div style="font-size: 20px; font-weight: bold; margin-bottom: 10px;">
            {avg_rate:.4f}
        </div>
        
        <!-- 溫度計 -->
        <div style="display: flex; flex-direction: column; align-items: center; margin-bottom: 10px;">
            <div style="
                width: 25px;
                height: 120px;
                background: rgba(255, 255, 255, 0.2);
                border: 2px solid rgba(255, 255, 255, 0.5);
                border-radius: 15px 15px 20px 20px;
                position: relative;
                margin-bottom: 5px;
            ">
                <div style="
                    position: absolute;
                    bottom: 2px;
                    left: 2px;
                    right: 2px;
                    height: {percentage}%;
                    background: {color};
                    border-radius: 12px 12px 18px 18px;
                "></div>
            </div>
            
            <!-- 底部圓球 -->
            <div style="
                width: 20px;
                height: 20px;
                background: {color};
                border: 2px solid rgba(255, 255, 255, 0.8);
                border-radius: 50%;
                margin-top: -3px;
            "></div>
        </div>
        
        <!-- 百分比和狀態 -->
        <div style="font-size: 16px; font-weight: bold; margin-bottom: 5px;">
            {percentage:.0f}%
        </div>
        <div style="font-size: 10px; opacity: 0.9; margin-bottom: 10px;">
            🌡️ {status}
        </div>
        
        <!-- 買賣價格 -->
        <div style="font-size: 10px; text-align: left;">
            <div style="margin: 3px 0; padding: 4px 6px; background: rgba(76, 175, 80, 0.3); border-radius: 4px;">
                💰 {buy_rate:.4f}
            </div>
            <div style="margin: 3px 0; padding: 4px 6px; background: rgba(244, 67, 54, 0.3); border-radius: 4px;">
                💸 {sell_rate:.4f}
            </div>
            <div style="margin: 3px 0; padding: 4px 6px; background: rgba(255, 193, 7, 0.3); border-radius: 4px;">
                ⚖️ {avg_rate:.4f}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    source_display = _display_code(source_currency, "TWD" if source_curr == "新台幣" else source_curr)
    target_display = _display_code(target, "TWD" if target_curr == "新台幣" else target_curr)
    
    if source_curr == "新台幣" and target_curr != "新台幣":
        target_row = next((r for r in tradeable if _matches_rate(r, target_match, target_curr)), None)
        if target_row and target_row.get("sell"):
            converted = amount / target_row["sell"]
            calc_info = f"計算式: {amount:,} TWD ÷ {target_row['sell']:.2f} = {converted:,.2f} {target_display}"
    
    elif source_curr != "新台幣" and target_curr == "新台幣":
        source_row = next((r for r in tradeable if _matches_rate(r, source_match, source_curr)), None)
        if source_row and source_row.get("buy"):
            converted = amount * source_row["buy"]
            calc_info = f"計算式: {amount:,} × {source_row['buy']:.2f} = {converted:,.2f} TWD"
    
    elif source_curr != "新台幣" and target_curr != "新台幣":
        source_row = next((r for r in tradeable if _matches_rate(r, source_match, source_curr)), None)
        target_row = next((r for r in tradeable if _matches_rate(r, target_match, target_curr)), None)
        
        if source_row and target_row and source_row.get("buy") and target_row.get("sell"):
            twd_amount = amount * source_row["buy"]
            converted = twd_amount / target_row["sell"]
            calc_info = f"計算式: {amount:,} {source_display} × {source_row['buy']:.2f} ÷ {target_row['sell']:.2f} = {converted:,.2f} {target_display}"
    
    else:
        converted = amount
        calc_info = f"同貨幣無需轉換: {converted:,}"
    
    return converted, calc_info
    # 用於匹配的完整字串（包含中文和代碼）
    source_match = source_currency
    target_match = target
    def _matches_rate(rate: Dict[str, Any], option_full: str, option_base: str) -> bool:
        # cache 可能只有 currency (例: "美金 (USD)")，也可能有 name
        label = (rate.get("name") or rate.get("currency") or "").strip()
        if not label:
            return False
        if label == option_full or label == option_base:
            return True
        # 容忍 "美金" 對上 "美金 (USD)" 之類
        return label.startswith(option_base + " (")
    def _display_code(label: str, fallback: str) -> str:
        if "(" in label and ")" in label:
            return label.split("(", 1)[1].split(")", 1)[0].strip()
        return fallback
ndef calculate_conversion(source_curr: str, target_curr: str, amount: float, 
                        source_currency: str, target: str, tradeable: List) -> tuple:
    """計算貨幣轉換"""
    converted = 0
    calc_info = ""def get_cached_rates() -> Dict[str, Any]:
    """獲取快取的匯率資料"""
    if is_expired(300):
        raw_rates, rates_update_time = fetch_rates()
        all_banks_usd = fetch_usd_rates_all_banks()
        gold_price = fetch_gold_price()
        
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
            if formatted_rates:
                write_cache(formatted_rates, all_banks_usd, gold_price, rates_update_time)
    
    return read_cache() or {}@st.cache_data(ttl=300)n# 快取相關配置