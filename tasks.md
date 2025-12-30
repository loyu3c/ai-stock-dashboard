# AI 股票波段選股小幫手 - 開發任務清單

## 第一階段：基礎建設 (Phase 1: Infrastructure, Days 1-7)
- [x] **環境設定 (Environment Setup)**
    - [x] 建立 `requirements.txt` (套件: `shioaji`, `pandas`, `pandas_ta`, `gspread`, `google-auth`, `line-bot-sdk`)
    - [x] 設定 `config.py` 管理環境變數 (API Keys, Token)
    - [x] 建立 `.gitignore` (排除 `service_account.json`, `.env`, `*.pfx`)
- [x] **GCP 與 權限驗證 (GCP & Auth)**
    - [x] 在 GCP 啟用 Google Sheets API & Drive API
    - [x] 產生並下載 `service_account.json`
    - [x] 測試 GSpread 連線 (讀取/寫入簡單數據)
- [x] **Shioaji (永豐金) 串接**
    - [x] 實作 `ShioajiLogin` 類別 (處理 CA PFX 憑證)
    - [x] 實作 `DataFetcher` 下載日 K 線 (OHLC)
    - [x] 將數據儲存至本機 (CSV/Parquet) 作為緩存

## 第二階段：分析引擎 (Phase 2: Analysis Engine, Days 8-14)
- [x] **技術指標 (Technical Analysis)**
    - [x] 實作 `TechIndicators` 類別 (基於 `pandas_ta`)
    - [x] 計算 SMA (10, 20), MACD, RSI, KD
- [x] **紅綠燈邏輯 (Signal Logic)**
    - [x] 實作 `StrategyAnalyzer` 類別
    - [x] 定義 **綠燈** 邏輯 (Price > MA20 & MACD > 0 & KD 黃金交叉)
    - [x] 定義 **紅燈** 邏輯 (Price < MA10 or RSI > 80)
    - [x] 定義 **黃燈** 邏輯 (預設/觀望)
- [x] **市場掃描 (Scanner)**
    - [x] 建立 `MarketScanner` 遍歷所有目標股票
    - [x] 產生每日報表 DataFrame

## 第三階段：雲端與通知 (Phase 3: Cloud & Notification, Days 15-30)
- [x] **Google Sheets 同步 (Google Sheets Sync)**
    - [x] 實作 `SheetManager` 更新「每日報表」分頁
    - [x] 透過 API 應用條件格式 (Conditional Formatting, 自動上色)
- [x] **Line 通知 (Messaging API)**
    - [x] 設定 Messaging API (Channel Access Token & User ID)
    - [x] 實作 `LineNotifier` 類別 (使 `push_message` 主動推播)
    - [x] 發送每日摘要 (例：「今日前 5 名綠燈潛力股」)
- [x] **自動化 (Automation)**
    - [x] 建立 `main.py` 程式進入點
    - [x] 設定系統排程 (Windows Task Scheduler / Cron)

## 第四階段：AI 與 交易 (Phase 4: AI & Trading, Month 2)
- [ ] **AI 信心分數 (AI Confidence Scoring)**
    - [ ] 串接 Gemini API 進行籌碼/新聞面分析 (選配)
- [ ] **模擬與自動交易 (Simulation/Trading)**
    - [ ] 開啟 Shioaji `simulation=True` 模式
    - [ ] 實作 `OrderExecutor` 下單模組
    - [ ] 實作風險控管 (每日最大虧損限制)

## 第五階段：網頁儀表板 (Phase 5: Web Dashboard)
- [x] **專案初始化 (Project Init)**
    - [x] 使用 Vite 建立 React + TailwindCSS 專案
    - [x] 安裝必要套件 (axios, shadcn/ui, recharts)
- [x] **資料串接 (Data Fetching)**
    - [x] 實作 Google Sheets API 連線 (前端直接讀取 CSV)
    - [x] 解析並處理 CSV/JSON 資料格式
- [x] **UI 開發 (UI Development)**
    - [x] **總覽頁面**: 顯示紅綠燈統計、本日焦點股
    - [x] **個股詳情**: (目前以表格呈現，包含技術指標數值)
    - [x] **筛选器**: (已透過分類統計卡片與排序列表呈現)
    - [x] **導航佈局 (Layout)**: 實作左側功能選單 (Sidebar)
