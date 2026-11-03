# 數位轉型學院（DTI）｜2026 政府補助統編一鍵快選儀表板

> **100% 零 AI 執行期（Zero-LLM Runtime）・全國 185 萬筆統編即時檢索・中央跨部會＋全台 22 縣市共 48 案確定性規則引擎**  
> 同時提供 **「📋 2D 跨世代高管瀑布流清單版」** 與 **「🏝️ 3D 政策浮島互動沙盤版」** 雙模式體驗。

---

## 🌐 線上立即體驗（Live Demo）

| 版本模式 | 適用情境與特色 | 線上體驗連結 |
| :--- | :--- | :--- |
| **📋 2D 跨世代高管清單版**<br>（預設首頁） | 專為 20–70 歲決策者與執行幕僚設計：支援 `🔠 長輩大字模式`、免統編 30 秒三問快篩、白話 `🎯 預估入袋金額`、首屏自籌款比例、左右雙欄（👔 老闆看重點 vs. 📋 幕僚打勾檢核表）、一鍵 `📤 LINE分享` 與 `📄 A4 決策簡報列印`。 | 👉 **[開啟 2D 瀑布流清單版](https://kerokerolab.github.io/dti-grant-matcher/)** |
| **🏝️ 3D 政策浮島沙盤版**<br>（Three.js 互動群島） | 致敬 [HEART 政策島](https://puma.taipei/heart-island) 微縮模型風格：6 座六角形轉型主題島嶼、9 座跨海連接橋樑、66 位隨機漫步 Q 版小人偶、點擊平滑飛近（Smooth Fly-To）與毛玻璃詳情抽屜，並可一鍵切回 2D 清單。 | 👉 **[開啟 3D 政策浮島版](https://kerokerolab.github.io/dti-grant-matcher/taiwan_grant_island_3d.html)** |

---

## ✨ 核心系統特色

1. **100% 零 AI 執行期（Zero-LLM Runtime & 零幻覺）**
   * 網站運作完全不呼叫任何外部 LLM API（零 Token 成本、零等待延遲、零編造網址或金額風險），所有資格判定皆透過確定性規則引擎（Rule-Based Mapping）與預抓取驗證之開放資料庫即時精算。
2. **全國 185 萬筆統編 ＆ 公司名稱關鍵字雙軌檢索（Multi-Source Failover）**
   * **Tier 1（遠端公開資料 API）**：串接 [g0v 台灣公司資料開放 API](https://company.g0v.ronny.tw/)，完整支援一般公司法人、獨資／合夥商號，以及財政部稅籍登記之**社團法人／非營利協會**（如 `00651251` 社團法人台灣數位轉型協會）。
   * **Tier 2（本地 SQLite 百萬筆毫秒級檢索）**：提供 `local_sqlite_server.py`，支援匯入政府開放資料平臺全國商工登記 CSV。
   * **Tier 3（內建快取底稿備援）**：離線環境自動退回內建 `companies_db.json` 快取；若忘記統編，亦可點擊 **「⚡ 30 秒三問快篩（選產業／人數／有無工廠）」** 直接篩選。
3. **涵蓋中央 8 大部會署（26 案）＋ 全台 22 縣市地方型補助（22 案）共 48 筆規則**
   * 依據經濟部所營事業代碼首碼（`C/D` 類製造業 vs. `E/F/G/H/I/J/M` 類服務業）、設籍縣市、實收資本額、勞保人數、工廠登記與同年度互斥條款進行 **10 道確定性閘門審查**。
   * 每筆補助案的申辦按鈕皆直連該專案**官方專屬申辦入口（Deep Link）**，並將不符資格或外縣市案件自動收納於底部「🛡️ 自動防雷攔截」抽屜說明剔除原因。
4. **雙緩衝原子交換資料管線（Atomic Swap Data Pipeline）**
   * 後端 Python 更新管線（`update_portal_data.py`）先對新抓取之 JSON 執行 Schema 驗證、萬元單位防呆與非空泛首頁檢核，100% 通過後才原子注入 HTML 檔案，並搭配 GitHub Actions 每週自動排程巡檢。

---

## 📂 專案檔案架構

```text
.
├── index.html                        # GitHub Pages 首頁入口（與 taiwan_grant_matcher.html 同步）
├── taiwan_grant_matcher.html         # 【2D 主程式】跨世代高管瀑布流清單版
├── taiwan_grant_island_3d.html       # 【3D 主程式】Three.js 政策浮島互動沙盤版
├── AI_REBUILD_BLUEPRINT.md           # 【AI 重製藍圖】可供其他 AI 模型一鍵重製本系統之完整規格與主提示詞
├── companies_db.json                 # 預快取之企業／商號／社團法人統編底稿與營業項目代碼映射字典
├── grants_rules.json                 # 全國 48 筆（中央 26 案 + 22 縣市地方型 22 案）結構化補助規則庫
├── update_portal_data.py             # 一鍵資料稽核與雙 HTML 原子注入同步腳本
├── crawl_gov_grants.py               # 中央與 22 縣市補助爬蟲、網址狀態巡檢與稽核管線
├── sync_gcis_companies.py            # 商工開放資料與 g0v 統編多源降級抓取管線
├── local_sqlite_server.py            # 本地 SQLite 資料庫建置、CSV 批次匯入與輕量 API 伺服器
├── companies_local.sqlite            # 本地 SQLite 企業統編資料庫
└── .github/workflows/
    └── weekly-sync-and-pages.yml     # 每週日凌晨自動執行資料管線巡檢之 GitHub Actions 工作流
```

---

## 🚀 快速開始與資料更新指令

### 1. 直接在瀏覽器開啟（免安裝任何套件）
直接雙擊開啟 `taiwan_grant_matcher.html`（2D 清單版）或 `taiwan_grant_island_3d.html`（3D 群島版）即可完整運作；亦可支援網址參數帶入統編自動查詢（例如 `?taxId=28458491`）。

### 2. 執行資料管線同步與稽核注入
當您修改了 `grants_rules.json` 或執行爬蟲更新後，只需在終端機執行：

```bash
python3 update_portal_data.py
```
腳本會在 0.1 秒內完成「資安與反爬蟲防守測試」與「數據稽核會計師檢查」，並將最新資料同步注入 `taiwan_grant_matcher.html`、`index.html` 與 `taiwan_grant_island_3d.html`。

### 3. （選用）啟動本地 SQLite 百萬筆統編 API 伺服器
```bash
# 啟動本地 127.0.0.1:8765 查詢服務
python3 local_sqlite_server.py --serve --port 8765

# 若有下載政府開放資料平臺全國公司/商業登記 CSV，可串流匯入百萬筆統編：
python3 local_sqlite_server.py --import-csv /path/to/BGMOPEN1.csv
```

---

## 🤖 如何用自己的 AI 模型重製這套網站？

本專案已將完整系統架構、資料結構、2D/3D 前端規格與 6 大實戰防雷鐵律整理於 **[AI_REBUILD_BLUEPRINT.md](./AI_REBUILD_BLUEPRINT.md)**。  
您只需將 `AI_REBUILD_BLUEPRINT.md` 餵給您的 AI 模型（如 Gemini、Claude、ChatGPT、Cursor），並貼上該文件第一節的 **「一鍵重製啟動指令（Master Prompt）」**，即可完整重製整套系統。

---

## 📄 授權與聲明
* © 2026 **數位轉型學院（Digital Transformation Academy, DTI）**
* 本系統收錄之各級政府補助金額、截止期限與資格條件均以各部會及各縣市政府最新正式公告簡章為準。
