# 台幣匯率轉換應用程式

現代化的台幣匯率轉換工具，採用優化架構設計，提供實時匯率轉換和自動更新功能。

## ✨ 核心功能

- 🔄 **實時匯率轉換**：精確的台幣與外幣轉換
- 📊 **雙欄式界面**：左側換算器 + 右側匯率表
- ⏰ **智能更新**：10分鐘自動更新 + 手動更新
- 💰 **靈活計算**：可調小數位數，支援截取模式
- 🔒 **離線支援**：網路中斷時使用本地快取
- 📱 **響應式設計**：適配不同螢幕尺寸

## 🚀 快速啟動

### 1. 環境準備
```bash
# 啟動虛擬環境
.venv\Scripts\activate

# 檢查依賴 (應已安裝)
pip list | findstr "streamlit\|requests\|beautifulsoup4"
```

### 2. 啟動應用
```bash
# 進入項目目錄
cd lesson7_1

# 啟動 Streamlit 應用
python -m streamlit run streamlit_app.py --server.port 8501
```

### 3. 訪問應用
開啟瀏覽器：http://localhost:8501

## ⚙️ 系統配置

### Windows 排程 (已配置)
- **任務名稱**: `Lesson7_1_UpdateRates`
- **執行頻率**: 每 10 分鐘
- **狀態檢查**: `schtasks /Query /TN "Lesson7_1_UpdateRates"`

### 手動更新
```bash
cd lesson7_1
python update_rates.py
```

## 📂 優化後結構

```
lesson7_1/
├── streamlit_app.py       # 🎯 主應用 (優化架構)
├── update_rates.py        # 🔄 更新服務 (簡化邏輯)  
├── config.py             # ⚙️ 配置管理 (新增)
├── rates/                # 📦 核心模組
│   ├── crawler.py        # 🕷️ 輕量化爬蟲
│   ├── normalize.py      # 🔧 資料處理
│   ├── storage.py        # 💾 快取管理
│   └── scheduler.py      # ⏲️ 任務調度
└── data/                 # 📄 資料檔案
    ├── rates_cache.json  # 實時快取
    └── sample_cache.json # 備援資料
```

## 🛠️ 技術亮點

### 架構優化
- **模組化設計**: 責任分離，易於維護
- **錯誤處理**: 多層級容錯機制  
- **性能提升**: 去除重量級依賴 (crawl4ai → requests)
- **代碼簡化**: 50%+ 代碼量減少

### 用戶體驗
- **即時響應**: 操作反饋更快速
- **精確計算**: 支援截取式小數處理
- **清晰界面**: 千分位分隔，狀態明確
- **容錯設計**: 網路異常時平滑降級

---

**項目狀態**: ✅ 已優化完成  
**架構版本**: v2.0 (簡化版)  
**維護狀態**: 生產就緒

如果環境無法安裝 Playwright，系統會自動退回到 `requests`+`BeautifulSoup` 的簡易抓取器；若沒有網路或抓取失敗，Streamlit 會使用內建的離線範例資料顯示介面。
