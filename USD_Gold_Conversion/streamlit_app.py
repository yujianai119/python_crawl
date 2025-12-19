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


# 快取相關配置
@st.cache_data(ttl=300)
def get_cached_rates() -> Dict[str, Any]:
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
    
    return read_cache() or {}


def calculate_conversion(source_curr: str, target_curr: str, amount: float, 
                        source_currency: str, target: str, tradeable: List) -> tuple:
    """計算貨幣轉換"""
    converted = 0
    calc_info = ""

    def _display_code(label: str, fallback: str) -> str:
        if "(" in label and ")" in label:
            return label.split("(", 1)[1].split(")", 1)[0].strip()
        return fallback

    def _matches_rate(rate: Dict[str, Any], option_full: str, option_base: str) -> bool:
        # cache 可能只有 currency (例: "美金 (USD)")，也可能有 name
        label = (rate.get("name") or rate.get("currency") or "").strip()
        if not label:
            return False
        if label == option_full or label == option_base:
            return True
        # 容忍 "美金" 對上 "美金 (USD)" 之類
        return label.startswith(option_base + " (")

    # 用於匹配的完整字串（包含中文和代碼）
    source_match = source_currency
    target_match = target

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


def render_thermometer(rate_data: Dict[str, Any], currency: str) -> None:
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


def format_display_amount(amount: float, decimals: int) -> str:
    """格式化顯示金額"""
    if decimals <= 0:
        return f"{int(amount):,}"
    import math
    factor = 10 ** decimals
    display_amount = math.trunc(amount * factor) / factor
    return f"{display_amount:.{decimals}f}"


def main():
    """主應用程式 - 高速版本"""
    st.set_page_config(
        page_title="美元黃金轉換", 
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # 主標題再往上移動5行（共6行空白）
    st.markdown("<div style='font-size:2.5rem;font-weight:800;margin-bottom:0.5em;line-height:1.1;'>美元黃金轉換</div>", unsafe_allow_html=True)

    # 簡化 CSS
    st.markdown("""
    <style>
    .stApp {font-family:'Microsoft JhengHei',sans-serif;}
    #MainMenu{visibility:hidden;}footer{visibility:hidden;}.stDeployButton{display:none;}
    </style>
    """, unsafe_allow_html=True)
    
    # 快速載入資料
    # Ensure cache is fresh
    with st.spinner("載入中..."):
        data = get_cached_rates()
    
    if not data or 'rates' not in data:
        st.error("無法取得匯率資料")
        if st.button("立即更新", type="primary"):
            st.cache_data.clear()
            st.rerun()
        return
    
    rates = data['rates']
    updated_time = data.get('updated_at', '')
    
    # 顯示更新時間 - 已隱藏
    # if updated_time:
    #     try:
    #         dt = datetime.fromisoformat(updated_time)
    #         if dt.tzinfo is None:
    #             dt = dt.replace(tzinfo=timezone.utc)
    #         local_time = dt.astimezone().strftime("%H:%M:%S")
    #         st.caption(f"⏰ 最後更新: {local_time}")
    #     except:
    #         pass
    
    # 篩選可交易的貨幣
    tradeable = [r for r in rates if r.get("buy") and r.get("sell")]
    
    # 僅保留美金
    currencies = []
    if tradeable:
        currencies = [
            r.get("name", r.get("currency", "")).replace(" (USD)", "")
            for r in tradeable 
            if "美金" in r.get("name", "") or "USD" in r.get("currency", "")
        ]
    
    currency_options = ["新台幣"] + currencies

    # 初始化 session state
    if "source_curr_select" not in st.session_state:
        st.session_state.source_curr_select = currency_options[0]
    
    if "target_curr_select" not in st.session_state:
        # Default to USD if available
        usd_opt = next((c for c in currency_options if "美金" in c or "USD" in c), None)
        st.session_state.target_curr_select = usd_opt if usd_opt else currency_options[0]

    def on_source_change():
        val = st.session_state.source_curr_select
        if "新台幣" in val or "TWD" in val:
            usd_opt = next((c for c in currency_options if "美金" in c or "USD" in c), None)
            if usd_opt:
                st.session_state.target_curr_select = usd_opt
        else:
            twd_opt = next((c for c in currency_options if "新台幣" in c or "TWD" in c), None)
            if twd_opt:
                st.session_state.target_curr_select = twd_opt

    def on_target_change():
        val = st.session_state.target_curr_select
        if "新台幣" in val or "TWD" in val:
            usd_opt = next((c for c in currency_options if "美金" in c or "USD" in c), None)
            if usd_opt:
                st.session_state.source_curr_select = usd_opt
        else:
            twd_opt = next((c for c in currency_options if "新台幣" in c or "TWD" in c), None)
            if twd_opt:
                st.session_state.source_curr_select = twd_opt

    # 添加欄位寬度調整控制
    st.sidebar.markdown("---")
    st.sidebar.subheader("版面設定")
    col1_width = st.sidebar.slider("左欄寬度", min_value=1, max_value=10, value=1, step=1)
    col2_width = st.sidebar.slider("中欄寬度", min_value=1, max_value=10, value=1, step=1)
    col3_width = st.sidebar.slider("右欄寬度", min_value=1, max_value=10, value=2, step=1)

    # 三欄布局：換算器、溫度計、表格
    col1, col2, col3 = st.columns([col1_width, col2_width, col3_width])
    
    with col1:
        st.markdown("""
        <div style='font-size:1.5rem;font-weight:700;margin-bottom:0.5em;line-height:1.2;'>匯率換算器</div>
        """, unsafe_allow_html=True)
        
        if not tradeable:
            st.info("目前無可交易的貨幣")
        else:
            # 初始化金額狀態
            if 'current_amount' not in st.session_state:
                st.session_state.current_amount = 10000
            
            st.markdown('<p style="color: red; font-weight: bold; margin-bottom: 0;">轉換前貨幣</p>', unsafe_allow_html=True)
            source_currency = st.selectbox(
                "轉換前貨幣", 
                currency_options, 
                key="source_curr_select",
                on_change=on_source_change,
                label_visibility="collapsed"
            )
            
            # ver1 原始輸入格式（與中間欄滑桿雙向同步，支持千位分隔符）
            formatted_value = f"{st.session_state.current_amount:,}"
            amount_input = st.text_input(
                "金額", 
                value=formatted_value,
                help="請輸入數字，支持千位分隔符顯示"
            )
            
            # 處理文字輸入轉換為數值
            try:
                # 移除千位分隔符並轉為整數
                amount = int(amount_input.replace(",", "").replace(" ", ""))
                if amount < 0:
                    amount = 0
            except (ValueError, AttributeError):
                amount = st.session_state.current_amount
            
            # 檢查輸入框是否變更
            if amount != st.session_state.current_amount:
                st.session_state.current_amount = amount
                st.rerun()
            
            # 轉換貨幣和預估金額已移至中間欄
        
        # 手動更新按鈕
        decimals = st.number_input("顯示小數位數", min_value=0, max_value=6, value=0, step=1)
    
    with col2:
        # 中間欄：可拖拉金額拉桿
        if tradeable:
            # 調整間距使轉換貨幣選擇器與左側轉換前貨幣選擇器對齊
            st.markdown("<div style='margin-top: 0.5em;'></div>", unsafe_allow_html=True)
            st.markdown("<div style='margin-top: 0.75em;'></div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            st.markdown('<p style="color: red; font-weight: bold; margin-bottom: 0;">轉換貨幣</p>', unsafe_allow_html=True)
            target = st.selectbox(
                "轉換貨幣", 
                currency_options, 
                key="target_curr_select",
                on_change=on_target_change,
                label_visibility="collapsed"
            )
            
            # 從左欄取得decimals值
            if 'decimals' not in locals():
                decimals = 0
            
            # 貨幣轉換邏輯
            source_curr = "新台幣" if "新台幣" in source_currency or "TWD" in source_currency else source_currency.split('(')[0].strip()
            target_curr = "新台幣" if "新台幣" in target or "TWD" in target else target.split('(')[0].strip()
            input_amount = st.session_state.current_amount
            
            converted_amount, calculation_info = calculate_conversion(
                source_curr, target_curr, input_amount, source_currency, target, tradeable
            )
            
            display_str = format_display_amount(converted_amount, decimals)
            
            # 顯示轉換結果和計算式
            if converted_amount > 0 and calculation_info:
                st.markdown(f"""
                <div style="background: #f0f2f6; padding: 15px; border-radius: 8px; margin: 10px 0;">
                    <div style="font-size: 18px; font-weight: bold; color: #333;">預估金額</div>
                    <div style="font-size: 18px; font-weight: bold; color: #333;">{display_str}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # 隱藏計算過程
                # st.markdown(f"""
                # <div style="background: #e8f5e8; padding: 10px; border-radius: 5px; margin: 5px 0;">
                #     <div style="font-size: 12px; color: #2e7d32;">{calculation_info}</div>
                # </div>
                # """, unsafe_allow_html=True)
            elif converted_amount == 0 and source_curr == target_curr:
                st.markdown(f"""
                <div style="background: #f0f2f6; padding: 15px; border-radius: 8px; margin: 10px 0;">
                    <div style="font-size: 12px; color: #666;">同貨幣轉換</div>
                    <div style="font-size: 18px; font-weight: bold; color: #333;">{f'{input_amount:,}'}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.write("無法交易或找不到匯率資訊，請檢查匯率資料")
            
            # 整個拉桿區域上移（減少間距）
            # st.markdown("<br><br><br>", unsafe_allow_html=True)
            
            # 在滑桿前顯示當前值和對應美金金額
            current_val = st.session_state.current_amount
            if 'target' in locals() and target:
                # 使用 calculate_conversion 計算正確的轉換金額
                converted_slider, _ = calculate_conversion(
                    source_curr, target_curr, current_val, source_currency, target, tradeable
                )
                
                st.markdown(f"""
                <div style="text-align: left; font-size: 18px; font-weight: bold; color: #333; margin-bottom: 5px;">
                    {current_val:,} ({int(converted_slider):,})
                </div>
                """, unsafe_allow_html=True)

            # 可拖拉的金額滑桿（與左欄輸入框雙向同步）
            slider_amount = st.slider(
                "金額滑桿",
                min_value=0,
                max_value=500000,
                value=st.session_state.current_amount,
                step=1000,
                format=" ",
                help="拖動調整金額，會同步更新左欄輸入框",
                label_visibility="collapsed"
            )
            
            # 檢查滑桿是否變更
            if slider_amount != st.session_state.current_amount:
                st.session_state.current_amount = slider_amount
                st.rerun()
            

            

        else:
            st.markdown("<div style='text-align: center; padding: 50px; color: #999;'>等待匯率資料...</div>", unsafe_allow_html=True)
    
    with col3:
        # Add Chinese font styling for table
        st.markdown("""
        <style>
        .stDataFrame {
            font-family: 'Microsoft JhengHei', '微軟正黑體', sans-serif;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style='font-size:2rem;font-weight:700;margin-bottom:0.5em;line-height:1.2;'>美元</div>
        """, unsafe_allow_html=True)
        
        # Prepare table data in ver1 format
        all_banks_usd = data.get('all_banks_usd', [])
        display_data = []
        
        if all_banks_usd:
            display_data = []
            # Map for bank names
            name_map = {
                "臺灣銀行": "臺灣銀行"
            }
            
            # Filter for target banks - 僅保留臺灣銀行
            target_banks = ["臺灣銀行"]
            
            for rate in all_banks_usd:
                bank_name = rate.get("bank", "")
                if bank_name not in target_banks:
                    continue
                    
                display_name = name_map.get(bank_name, bank_name)
                buy = rate.get("buy")
                sell = rate.get("sell")
                
                # 計算匯損比例：(賣出價-買入價)/買入價 * 100%
                if buy is not None and sell is not None and buy > 0:
                    loss_ratio = ((sell - buy) / buy) * 100
                    loss_ratio_str = f"{loss_ratio:.2f}%"
                    loss_ratio_num = loss_ratio  # 用於排序的數值
                else:
                    loss_ratio_str = "N/A"
                    loss_ratio_num = float('inf')  # N/A 排在最後
                
                display_data.append({
                    "銀行": display_name,
                    "幣別": "美金",
                    "即期買入": str(buy) if buy is not None else "-",
                    "即期賣出": str(sell) if sell is not None else "-",
                    "匯損比例": loss_ratio_str,
                    "外匯匯率更新": "↓",
                    "_sort_key": loss_ratio_num  # 隱藏的排序鍵
                })
            
            # 按匯損比例從低到高排序
            display_data.sort(key=lambda x: x["_sort_key"])
            
            # 移除排序鍵，只保留顯示欄位
            for item in display_data:
                del item["_sort_key"]

        elif rates:
            display_data = []
            for rate in rates:
                # 只保留美金
                if "美金" not in rate.get("currency", "") and "USD" not in rate.get("currency", ""):
                    continue

                buy = rate.get("buy")
                sell = rate.get("sell")
                
                # 計算匯損比例：(賣出價-買入價)/買入價 * 100%
                if buy is not None and sell is not None and buy > 0:
                    loss_ratio = ((sell - buy) / buy) * 100
                    loss_ratio_str = f"{loss_ratio:.2f}%"
                    loss_ratio_num = loss_ratio  # 用於排序的數值
                else:
                    loss_ratio_str = "N/A"
                    loss_ratio_num = float('inf')  # N/A 排在最後
                
                display_data.append({
                    "銀行": "臺灣銀行",
                    "幣別": "美金",
                    "即期買入": str(buy) if buy is not None else "暫停交易",
                    "即期賣出": str(sell) if sell is not None else "暫停交易",
                    "匯損比例": loss_ratio_str,
                    "外匯匯率更新": "↓",
                    "_sort_key": loss_ratio_num  # 隱藏的排序鍵
                })
            
            # 按匯損比例從低到高排序
            display_data.sort(key=lambda x: x["_sort_key"])
            
            # 移除排序鍵，只保留顯示欄位
            for item in display_data:
                del item["_sort_key"]

        if display_data:
            # 使用 dataframe 顯示表格 (與黃金表格相同方式)
            df = pd.DataFrame(display_data)
            # 移除「外匯匯率更新」欄位,改用按鈕
            df_display = df.drop(columns=['外匯匯率更新'])
            
            # 設定置中對齊
            def highlight_red_bold(val):
                return 'color: red; font-weight: bold; font-size: 1.5em' if val not in [None, '', '-'] else ''

            styled_df = df_display.style.set_properties(
                subset=["幣別", "即期買入", "即期賣出", "匯損比例"], 
                **{'text-align': 'center'}
            ).applymap(highlight_red_bold, subset=["即期買入", "即期賣出", "匯損比例"])
            
            st.dataframe(
                styled_df,
                use_container_width=True,
                column_config={
                    "銀行": st.column_config.TextColumn("銀行", width="small"),
                    "幣別": st.column_config.TextColumn("幣別", width="small"),
                    "即期買入": st.column_config.TextColumn("即期買入", width="small"),
                    "即期賣出": st.column_config.TextColumn("即期賣出", width="small"),
                    "匯損比例": st.column_config.TextColumn("匯損比例", width="small"),
                },
                hide_index=True
            )
            
            # 在表格下方顯示匯率資料更新時間（使用匯率網站的更新時間）
            current_data = get_cached_rates()
            rates_update_time_str = current_data.get('rates_update_time', '')
            if rates_update_time_str:
                try:
                    # 網站時間格式: 2025/12/17 13:16
                    from datetime import datetime
                    # 解析並轉換格式
                    dt = datetime.strptime(rates_update_time_str, '%Y/%m/%d %H:%M')
                    time_str = dt.strftime('%Y年%m月%d日 %H:%M:%S')
                    st.markdown(f"<p style='color: blue; font-size: 14px;'>更新時間: {time_str}</p>", unsafe_allow_html=True)
                except:
                    pass
        else:
            st.warning("暫無匯率資料")
        
        # ...已移除定存利率假資料表格...
        
        # 黃金價格表格
        st.markdown("""
        <div style='font-size:2rem;font-weight:700;margin-bottom:0.5em;line-height:1.2;'>黃金存摺</div>
        """, unsafe_allow_html=True)
        
        # 準備黃金數據 - 重新獲取最新資料
        current_data = get_cached_rates()
        gold_data = []
        
        # 從快取中獲取黃金價格
        gold_price = current_data.get('gold_price', {})
        buy = gold_price.get('buy')
        sell = gold_price.get('sell')
        
        # 計算價差：賣出價 - 買入價
        if buy is not None and sell is not None:
            price_diff = sell - buy
            price_diff_str = f"{price_diff:,.0f}"
        else:
            price_diff_str = "N/A"
        
        gold_data.append({
            "銀行": "臺灣銀行",
            "每克黃金": "黃金 (GOLD)",
            "買入": f"{buy:,.0f}" if buy is not None else "",
            "賣出": f"{sell:,.0f}" if sell is not None else "",
            "價差": price_diff_str if buy is not None and sell is not None else ""
        })
        
        if gold_data:
            df_gold = pd.DataFrame(gold_data)
            def highlight_gold_red_bold(val):
                return 'color: red; font-weight: bold; font-size: 1.5em' if val not in [None, '', '-'] else ''

            styled_df_gold = df_gold.style.set_properties(
                subset=["每克黃金", "買入", "賣出", "價差"], 
                **{'text-align': 'center'}
            ).applymap(highlight_gold_red_bold, subset=["買入", "賣出", "價差"])
            
            st.dataframe(
                styled_df_gold,
                use_container_width=True,
                column_config={
                    "銀行": st.column_config.TextColumn("銀行", width="small"),
                    "每克黃金": st.column_config.TextColumn("每克黃金", width="small"),
                    "買入": st.column_config.TextColumn("買入", width="small"),
                    "賣出": st.column_config.TextColumn("賣出", width="small"),
                    "價差": st.column_config.TextColumn("價差", width="small"),
                },
                hide_index=True
            )
            
            # 在黃金更新按鈕下方顯示資料更新時間（使用黃金網站的更新時間）
            gold_update_time_str = gold_price.get('update_time', '')
            if gold_update_time_str:
                try:
                    # 網站時間格式: 2025/12/17 12:49
                    from datetime import datetime
                    # 解析並轉換格式
                    dt = datetime.strptime(gold_update_time_str, '%Y/%m/%d %H:%M')
                    time_str = dt.strftime('%Y年%m月%d日 %H:%M:%S')
                    st.markdown(f"<p style='color: blue; font-size: 14px;'>更新時間: {time_str}</p>", unsafe_allow_html=True)
                except:
                    pass


if __name__ == "__main__":
    main()