# Synology NAS 部署指南 (Deployment Guide)

本指南將引導您將 `AI Stock Assistant` 部署至 Synology DS216+II 的 Container Manager 上。

## 前置準備 (Prerequisites)

1.  **安裝套件**: 請登入 DSM，在套件中心安裝/更新 **Container Manager** (舊稱 Docker)。
2.  **準備檔案**: 您需要將以下檔案上傳至 NAS 的一個資料夾 (例如 `/docker/ai-stock`)：
    *   `Dockerfile`
    *   `docker-compose.yml`
    *   `requirements.txt`
    *   `.dockerignore`
    *   `main.py` 及所有 `.py` 程式碼檔案
    *   `dashboard/` 資料夾 (包含 `Dockerfile`, `nginx.conf`, `src/`, `package.json` 等)
    *   `.env` (包含您的 API 金鑰)
    *   `SHIOAJI_PFX_PATH.pfx` (您的憑證檔)
    *   `service_account.json` (Google Sheets 憑證)

> **注意**: 請確保 `.env` 中的 `SHIOAJI_PFX_PATH` 環境變數設定正確。
> 如果在 NAS 上的檔案結構是平行的，建議設為 `SHIOAJI_PFX_PATH=./SHIOAJI_PFX_PATH.pfx`。

## 部署步驟 (Deployment Steps)

### 方法 A: 使用 Container Manager "專案 (Project)" 功能

**適用於**: 新版 DSM (7.2+) 或已安裝 Container Manager 的機型。
如果您在 Docker 左側選單有看到 **「專案 (Project)」**，請使用此方法。

1.  **開啟 Container Manager**。
2.  點選左側選單的 **「專案 (Project)」**。
3.  點選 **「新增 (Create)」**。
4.  **設定專案**:
    *   **專案名稱**: `ai-stock-bot`
    *   **路徑 (Path)**: 選擇您剛剛上傳檔案的資料夾 (例如 `/docker/ai-stock`)。
    *   **來源**: 選擇 **「使用現有的 docker-compose.yml」**。
5.  點選 **「下一步」** 並勾選 **「建立後立即啟動專案」**。
6.  完成！

---

### 方法 B: 使用 "任務排程表" (適用於舊版 Docker / 無 "專案" 選單)

**⚠️ 重要**: 如果您的 Docker 畫面只有「概況、容器、映像檔...」而**沒有「專案」**選單 (如 DS216+II 常見情況)，請務必使用此方法！

1.  **確認檔案路徑**:
    *   開啟 **File Station**，在 `ai-stock` 資料夾上按右鍵 -> **內容**。
    *   記下 **所在位置** (通常是 `/volume1/docker/ai-stock`)。

2.  **開啟「控制台 (Control Panel)」**:
    *   點選 **「任務排程表 (Task Scheduler)」**。

3.  **新增啟動腳本**:
    *   點選 **新增** -> **排程任務** -> **使用者定義的指令碼**。
    *   **一般** 分頁:
        *   任務名稱: `Start AI Stock`
        *   使用者帳號: **root** (一定要選 root)。
        *   已啟動: **不勾選** (我們只想手動執行一次來啟動它)。
    *   **排程** 分頁: (不用設定，因為我們只跑一次)。
    *   **任務設定** 分頁 -> **使用者定義的指令碼**:
        ```bash
        # 請確保路徑與您 File Station 看到的一致
        cd /volume1/docker/ai-stock
        
        # 啟動服務 (背景執行)
        /usr/local/bin/docker-compose up -d --build
        ```
    *   點選 **確定**。

4.  **執行部署**:
    *   在列表選取剛剛建立的 `Start AI Stock`。
    *   點選上方選單的 **「執行 (Run)」**。
    *   系統會詢問是否執行，選 **是**。

5.  **等待建置**:
    *   這一步包含下載 Python/Node 環境並編譯程式，DS216+II 可能需要 **15-20 分鐘**。
    *   您可以回到 Docker 的 **「容器 (Container)」** 分頁觀察，成功後會出現 `ai_stock_backend` 和 `ai_stock_frontend` 兩個綠燈容器。


### 驗證 (Verification)

當專案狀態變為綠燈 (Running) 後：

1.  **Web 介面**: 開啟瀏覽器輸入 `http://<NAS_IP>:5678` 即可看到全新的儀表板。
2.  **API 測試**: 可以嘗試於瀏覽器輸入 `http://<NAS_IP>:8000/docs` 查看後端 API 文件。

### 自動排程 (Scheduled Execution)

由於我們的後端容器 `backend` 此時是作為 Web Server (API) 長駐執行，我們需要另外設一個排程來執行「每日掃描」。

1.  開啟 **「控制台」** -> **「任務排程表」**。
2.  新增 -> **「排程任務」** -> **「使用者定義的指令碼」**。
3.  **一般**: 任務名稱 `Daily Stock Scan`, 使用者 `root`。
4.  **排程**: 每日 15:30 (台股收盤後)。
5.  **指令碼**:
    ```bash
    # 直接在我們已經跑起來的容器內執行 Python 腳本，省資源又快速！
    docker exec ai_stock_backend python main.py
    ```
    *   這行指令會呼叫正在運行的 `ai_stock_backend` 容器，執行裡面的 `main.py` 進行掃描、存檔 (SQLite) 並發送 LINE 通知。

### 更新程式碼

若您修改了程式碼並上傳覆蓋 NAS 檔案：
1.  回到 Container Manager -> 專案 -> `ai-stock-bot`。
2.  點選 **「動作」** -> **「重建 (Rebuild)」**。
3.  系統會重新 Build Docker Image 並重啟。

## 常見問題排除 (Troubleshooting)

*   **權限錯誤**: 確保 `service_account.json` 和 `.pfx` 檔案在 NAS 上有被讀取的權限。
*   **記憶體不足**: 若執行失敗，嘗試在 `docker-compose.yml` 增加 `mem_limit` 限制，或是減少 Pandas 一次處理的資料量。
*   **找不到裝置**: 確保 `.env` 檔名開頭有 `.`，且位於正確目錄。
