# 2026 政府補助統編一鍵快選系統（2D 跨世代高管版 ＋ 3D 政策浮島版）— AI 完整重製藍圖與規格書

> **文件用途**：本文件完整封裝「數位轉型學院（DTI）｜2026 政府補助統編一鍵快選儀表板」之系統架構、資料管線、確定性規則引擎、2D 跨世代高管 UI/UX 規格、3D Low-Poly 浮島沙盤規格，以及實戰踩坑防雷指南。  
> **重製方式**：您只需將本 `.md` 檔案直接上傳或貼給任何具備寫程式能力的 AI 模型（如 Gemini、Claude、ChatGPT、Cursor、Windsurf），並下達下方第一節的「一鍵重製啟動指令」，即可在完全不依賴外部 LLM API 的情況下，100% 重製出整套可自動排程更新並部署至 GitHub Pages 的完整系統。

---

## 一、 給其他 AI 模型的一鍵重製啟動指令（Master Prompt）

若要在新的環境讓 AI 模型從零打造本系統，請直接複製以下區塊貼給 AI：

```markdown
請擔任「資深全端系統架構師、政府開放資料管線工程師、跨世代高管 UI/UX 設計師與 Three.js 3D 互動工程師」，嚴格依照這份《AI 完整重製藍圖與規格書》，在目前資料夾內從零建立一套「100% 零 AI 執行期、純確定性規則引擎驅動（Rule-Based Mapping）的台灣政府補助與企業統編一鍵媒合系統」。

請依序建立並驗證以下核心檔案：
1. `companies_db.json` 與 `sync_gcis_companies.py`：企業統編抓取與多源備援管線（串接經濟部 GCIS OAS API 與 g0v 台灣公司資料 API `https://company.g0v.ronny.tw/api/show/{ubn}`，支援一般公司、獨資合夥商號、以及位於 `data.財政部.營業人名稱` 之社團法人／協會，並依營業項目代碼首碼確定性映射為 `manufacturing` 或 `service`）。
2. `local_sqlite_server.py` 與 `companies_local.sqlite`：支援百萬筆全國商工 CSV 串流匯入與毫秒級本地查詢之 SQLite 資料庫與輕量 HTTP API 伺服器（`127.0.0.1:8765`）。
3. `grants_rules.json` 與 `crawl_gov_grants.py`：收錄中央 8 大部會署（26 案）＋ 全台 22 縣市地方型 SBIR／北市 SITI／新北創新補助（22 案）共 48 筆真實補助規則，所有 `officialUrl` 必須直連該計畫專屬申辦入口（Deep Link），嚴禁退回空泛部會首頁，且金額單位一律標準化為「萬元」。
4. `taiwan_grant_matcher.html`（並同步複製為 `index.html`）：2D 跨世代高管（20–70 歲）瀑布流清單版。
5. `taiwan_grant_island_3d.html`：參考「HEART 政策島（https://puma.taipei/heart-island）」風格打造的 Three.js 3D Low-Poly 轉型群島互動沙盤版（預設 3D 群島視角，內建一鍵切換回 2D 清單視角）。
6. `update_portal_data.py`：雙緩衝原子交換同步器（Atomic Swap Injector），執行 Schema 與防雷稽核後，將最新 `companies_db.json` 與 `grants_rules.json` 原子注入上述三個 HTML 檔案。
7. `.github/workflows/weekly-sync-and-pages.yml`：每週自動排程巡檢政府補助網站並更新資料庫之 GitHub Actions 工作流。

完成所有檔案建置後，請直接執行 `python3 update_portal_data.py` 與自動化驗收測試腳本，確保 100% 通過且無任何 `undefined` 欄位或斷鏈。
```

---

## 二、 系統核心設計哲學與架構總覽

### 1. 為什麼採用「100% 零 AI 執行期（Zero-LLM Runtime）」架構？
* **零幻覺、100% 法規確定性**：政府補助的資格審查（設籍縣市、實收資本額、勞保人數、工廠登記、同年度互斥條款）屬於明確的法規邏輯，不可交由生成式 AI 自由發揮或憑印象編造金額與網址。
* **零 API 金鑰成本、純靜態即可部署**：前端完全使用原生 HTML5 + Tailwind CSS + Vanilla JavaScript + Three.js，搭配預先抓取並驗證過的 JSON 規則庫與公開免金鑰之統編 API，可直接部署於免費的 GitHub Pages、Vercel 或 Netlify，甚至支援雙擊 `file://` 離線開啟。
* **雙緩衝原子交換（Multi-Source Failover & Atomic Swap）**：借鏡金融量化交易行情管線，後端 Python 爬蟲更新資料時，必須先在暫存檔（`.staging`）通過 JSON Schema 驗證、萬元單位防呆與網址非首頁檢核，100% 通過後才以 `os.replace()` 原子覆寫正式資料庫與 HTML 內嵌常數，絕不因外部網站改版弄壞線上系統。

### 2. 專案目錄結構樹
```text
project_root/
├── index.html                        # GitHub Pages 預設首頁（與 taiwan_grant_matcher.html 同步）
├── taiwan_grant_matcher.html         # 【2D 主程式】跨世代高管瀑布流清單版（含三問快篩、雙欄抽屜、LINE分享）
├── taiwan_grant_island_3d.html       # 【3D 主程式】Three.js 政策浮島沙盤版（含6大六角島、跨島橋樑、66位漫步角色）
├── companies_db.json                 # 預抓取之真實企業／商號／社團法人統編快取底稿與行業代碼映射表
├── grants_rules.json                 # 全國 48 筆（中央 26 案 + 22 縣市地方型 22 案）結構化補助規則庫
├── sync_gcis_companies.py            # 商工開放資料與 g0v 統編多源降級抓取管線
├── crawl_gov_grants.py               # 中央與 22 縣市補助爬蟲、網址狀態巡檢與稽核管線
├── local_sqlite_server.py            # 本地 SQLite 資料庫建置、百萬筆 CSV 串流匯入與毫秒級 API 伺服器
├── companies_local.sqlite            # 本地 SQLite 統編資料庫檔案
├── update_portal_data.py             # 一鍵編排器與 HTML 內嵌常數原子注入腳本
└── .github/
    └── workflows/
        └── weekly-sync-and-pages.yml # 每週日凌晨自動巡檢更新之 GitHub Actions 排程
```

---

## 三、 資料管線與統編／補助規則引擎規格（Data & Rule Engine Spec）

### 1. 財政部 8 碼統一編號邏輯檢核演算法（必備防呆）
* **標準乘數權重陣列**：**`[1, 2, 1, 2, 1, 2, 4, 1]`**（切勿誤植第 5、6 碼順序）。
* **演算法規則**：
  1. 將 8 碼統編每位數字分別乘以對應權重 `[1, 2, 1, 2, 1, 2, 4, 1]`。
  2. 將每個乘積的「十位數」與「個位數」相加（即 `Math.floor(p / 10) + (p % 10)`），並加總 8 個結果為 `sum`。
  3. 若 `sum % 5 === 0`（2023 新制）或 `sum % 10 === 0`（舊制）則為合法統編；若第 7 碼（index `6`）為 `'7'`，且 `(sum + 1) % 5 === 0` 或 `(sum + 1) % 10 === 0`，亦屬合法統編。
* **查詢不硬阻擋原則**：前端即使遇到少數非標準檢核碼之特殊機關統編，只要滿 8 碼數字，仍應先發送遠端 API 查詢，確認查無公開資料才退回手動模擬模式。

### 2. 全國 185 萬筆統編三層多源查詢與「社團法人／協會」解析規格
由於經濟部商工行政資料開放平臺（`data.gcis.nat.gov.tw`）對非政府白名單 IP 設有限制（會回傳 `非授權介接之IP`），前端與 Python 爬蟲必須採用三層穿透架構：

1. **Tier 1（遠端全國 185 萬筆開放資料 API）**：
   * 統編精確查詢：`https://company.g0v.ronny.tw/api/show/{ubn}`
   * 公司名稱關鍵字模糊查詢：`https://company.g0v.ronny.tw/api/search?q={keyword}`
   * **關鍵結構解析（支援公司、商號與社團法人協會）**：
     * **一般公司**：讀取 `data["公司名稱"]`、`data["公司所在地"]`、`data["實收資本額(元)"]`、`data["所營事業資料"]`。
     * **獨資／合夥商號**：讀取 `data["商業名稱"]`、`data["地址"]`、`data["資本額(元)"]`、`data["營業項目"]`。
     * **社團法人／財團法人／非營利協會（如 `00651251` 社團法人台灣數位轉型協會）**：在 g0v API 中，協會與非營利組織並非存放在 `公司名稱`，而是存放在 **`data["財政部"]`（財政部稅籍登記資料集）** 子物件下！解析器必須同時讀取 `data["財政部"]["營業人名稱"]`、`data["財政部"]["營業地址"]`、`data["財政部"]["組織別名稱"]` 與 `data["財政部"]["行業"]`，自動識別為「社團／財團法人協會」並映射為 `orgType: "company"`、`sector: "service"`。
2. **Tier 2（本地 SQLite 穿透查詢）**：若本機啟動 `local_sqlite_server.py`（`http://127.0.0.1:8765/api/company/{ubn}`），自動於 1.2 秒 Timeout 內向本地 SQLite 檢索。
3. **Tier 3（內建快取底稿備援）**：離線時自動讀取注入於 HTML 內的 `DEFAULT_COMPANIES_DB` 快取。

### 3. 營業項目代碼（所營事業代碼）確定性業別映射字典
| 代碼首字母 | 經濟部大類定義 | 系統確定性映射 (`sector`) | 說明與注意事項 |
| :--- | :--- | :--- | :--- |
| **`C`** | 製造業（`C1` 食品～`CZ` 其他製造） | `manufacturing` | 唯一標準製造業大類 |
| **`D`** | 電力及燃氣供應業 | `manufacturing` | 能源與工業公用事業 |
| **`E`** | 營造及工程服務業（含 `E605010` 電腦設備安裝業） | `service` | **防雷重點**：許多資訊軟體公司首碼為 `E605010`，屬工程安裝服務業，不可誤判為工廠製造業 |
| **`F` / `G` / `H`** | 批發零售餐飲業／運輸倉儲業／金融保險業 | `service` | 商業服務業主力客群 |
| **`I` / `J` / `M`** | 資訊及顧問服務業／文化運動休閒／專業科學技術服務 | `service` | 軟體、管顧、設計、旅遊服務業 |

### 4. `grants_rules.json` 標準欄位結構（48 筆補助案 Schema）
每一筆補助案物件必須嚴格遵守以下欄位名稱（前端 `evaluateGrant` 與卡片渲染 100% 綁定此 Schema）：
```json
{
  "id": "MOEA-SMESA-SBIR-CENTRAL",
  "title": "經濟部中小及新創企業署「小型企業創新研發計畫 (中央型 SBIR)」",
  "authority": "經濟部中小及新創企業署",
  "level": "central",
  "levelLabel": "中央部會",
  "category": "rd_innov",
  "categoryLabel": "02 企業研發創新",
  "shortHighlight": "全台最知名中小企業研發補助！先期研究最高 150 萬、研究開發最高 1,200 萬，全年隨到隨審。",
  "easyTag": "🟡 隨到隨審 · 需提創新研發計畫",
  "maxSubsidyMan": 1200,
  "perEmployeeCapMan": null,
  "subsidyRatio": "Phase 1 先期研究最高 150 萬；Phase 2 研究開發最高 600萬/年（2年1,200萬），補助上限 50%",
  "difficulty": "中高（須具備「創新性」研發標的或創新商模）",
  "easeWeight": 0.48,
  "deadline": "全年隨時線上受理（隨到隨審）",
  "urgencyWeight": 8,
  "isExpired": false,
  "officialUrl": "https://sbir.sme.gov.tw/",
  "secondaryUrl": "https://startup.sme.gov.tw/home/modules/funding/detail/?sId=2",
  "rules": {
    "smeOnly": true,
    "maxEmployees": null,
    "allowedOrgTypes": ["company", "business"],
    "allowedSectors": ["service", "manufacturing"],
    "requireFactoryReg": false,
    "allowedCounties": ["ALL"],
    "mutexGroup": null
  },
  "mutualExclusionNote": "同一研發標的不得重複向地方型 SBIR 或其他部會申請。",
  "checklist": [
    "符合中小企業認定標準之公司或商業登記證明",
    "國稅局與地方稅務局出具之最近一期無欠稅證明",
    "SBIR 計畫申請表與研發計畫書",
    "最近一期勞保局投保單位被保險人名冊"
  ]
}
```
* **6 大轉型方向分類代碼（`category`）**：
  1. `cloud_ai`：01 AI 與雲端
  2. `rd_innov`：02 研發創新（包含中央 SBIR/SIIR/TIIP 及全台 22 縣市地方型 SBIR／北市 SITI／新北創新補助）
  3. `training`：03 人才培訓
  4. `smart_mfg`：04 智慧製造
  5. `carbon`：05 淨零節能
  6. `export_mkt`：06 行銷海外

### 5. 確定性補助篩選與計分引擎（`evaluateGrant(grant)` 10 道閘門）
1. **時效閘門**：若 `grant.isExpired === true` 且勾選 `hideExpired`，予以攔截。
2. **中小企業認定閘門（`r.smeOnly`）**：依《中小企業認定標準》，**實收資本額 ≤ 1 億元（`paidInCapitalMan <= 10000`）或 經常僱用員工數 < 200 人**，只要符合其中一項即屬中小企業！只有當「資本額 > 1 億 **且** 員工 ≥ 200 人」時才判定為非中小企業。
3. **員工人數上限閘門（`r.maxEmployees`）**：例如「30 人以下服務業／製造業數位轉型培力補助」，若 `exactEmpCount > 30` 則攔截。
4. **組織型態閘門（`r.allowedOrgTypes`）**：區分 `company`（公司法人／社團法人）與 `business`（獨資／合夥商號，如 TIIP 產創平台不適用商號）。
5. **產業別閘門（`r.allowedSectors`）**：比對 `manufacturing` 或 `service`。
6. **工廠登記閘門（`r.requireFactoryReg`）**：製造業專案若要求合法工廠登記（或特定工廠登記），無廠登者自動攔截。
7. **設籍縣市閘門（`r.allowedCounties`）**：`["ALL"]` 表全國適用；地方型專案（如 `["臺北市"]`、`["臺中市"]`）僅限設籍該縣市企業符合，自動為使用者剔除其餘 21 個外縣市計畫。
8. **同年度互斥條款閘門（`r.mutexGroup === "MOEA_UPGRADE_2026"`）**：若勾選今年度已領過經濟部升級轉型或接班傳承補助，自動排除雲市集工業館 AI 點數等互斥計畫。
9. **動態補助上限試算（`dynamicMaxMan`）**：若有 `perEmployeeCapMan`（如每名員工補助 1 萬、上限 10 萬），則 `dynamicMaxMan = Math.min(maxSubsidyMan, exactEmpCount * perEmployeeCapMan)`。
10. **白話預估入袋金額與排序分數**：
    * `expectedValueMan = Math.round(dynamicMaxMan * easeWeight * 10) / 10`
    * `rankScore = expectedValueMan * (1 + urgencyWeight * 0.05)`（依此排序選出 Top 3 黃金組合包）。

---

## 四、 2D 跨世代高管版前端規格（`taiwan_grant_matcher.html`）

目標是讓 **20 歲新創創辦人（手機端快速查閱）** 到 **70 歲傳產董事長（大字級、白話指標、一鍵轉交特助）** 都能在第一屏、10 秒內完成決策：

### 1. 頂部極簡導覽列與無障礙「🔠 長輩大字模式」
* **左上角品牌識別**：淺藍底深藍字圓角方塊 **`DTI`**（`bg-sky-200 text-sky-900`）＋ 標題「**數位轉型學院｜政府補助統編一鍵快選**」（不放冗長副標題）。
* **右上角功能鈕**：
  * **`🏝️ 開啟 3D 群島版`**：點擊跳轉至 `./taiwan_grant_island_3d.html`（若已查詢統編，自動附帶 `?taxId=XXXXXXXX` 參數）。
  * **`🔠 長輩大字模式`**：點擊切換 `body.large-text-mode`，將全站 CSS 字級變數放大 `1.25 倍` 並儲存於 `localStorage`（`dti_large_text_mode`）。
  * **`↺ 重設條件`**：清空統編輸入框並恢復預設通用篩選條件。
* **WCAG 2.2 AAA 觸控標準**：全站所有按鈕、篩選膠囊、人數卡片、下拉選單與手風琴觸發列之 `min-height` 一律設為 `48px`。

### 2. 第一屏 STEP 1 整合式面板（省略獨立 STEP 2，確保第一屏直見符合資格區塊）
* **雙軌輸入框（`#ubnInput`）**：
  * **預設保持空白（`value=""`）**，Placeholder 為 `請輸入 8 碼統編 或 公司名稱關鍵字（如：00651251、哇寶、威鴻）`。
  * 輸入框內右側配置 **`✕ 清空重填`** 按鈕。
  * 當輸入滿 8 碼合法數字統編時，**免按按鈕自動觸發查詢**；當輸入中文／英文公司名稱關鍵字並按「`🔍 立即查詢補助`」或 `Enter` 時，自動先搜本地快取再搜遠端 `api/search?q=` 取回統編與工商資料。
* **免統編快篩引導鈕**：輸入框下方配置 **`⚡ 忘記統編？點此用 30 秒三問快篩（選產業／人數／有無工廠） ▾`**，點擊後自動展開下方工商條件抽屜並聚焦至產業別選單。
* **一行式工商與人數膠囊摘要列（`#companySummaryPills`）＋ 預設收合抽屜（`#companyDetailDrawer`）**：
  * 常駐一行顯示：`🏢 公司名稱`、`統編`、`📍 設籍縣市`、`💰 資本額`、`🏭 製造業 / 💼 商業服務業`、`👥 員工人數區間`。
  * 點擊右側「**⚙️ 檢視或修改工商與人數條件 ▾**」才向下展開抽屜，抽屜內部由上而下依序收納：
    1. **1. 工商登記基本條件**：正式公示資料連結 ＋ 4 欄設定（登記縣市、實收資本額、**主要產業別 [三問之1]**、**工廠登記狀態 [三問之2]**）。
    2. **2. 貴公司目前勞保投保員工人數區間 [三問之3]**：`👤 30 人以下`、`👥 31 ～ 199 人`、`🏢 200 人以上`。
    3. **3. 進階篩選條件**：精確勞保人數輸入框、今年度已領過升級轉型補助（互斥排除）、自動隱藏已截止梯次。
* **單行轉型方向過濾鈕（`#goalGroup`）＋ 右上角圓形紅底件數標記（`.goal-count-badge`）**：
  * 同行水平排列 `🎯 轉型方向：` 與 7 顆按鈕（`全部需求`、`01 AI 與雲端`、`02 研發創新`、`03 人才培訓`、`04 智慧製造`、`05 淨零節能`、`06 行銷海外`）。
  * 每顆按鈕右上角配置圓形紅底白字徽章（`#goalBadge-all` ～ `#goalBadge-export_mkt`），即時顯示該分類下符合資格的補助件數。

### 3. 第一屏深藍色英雄區（Count-Up 累計跳動 ＋ LINE分享 ＋ A4 決策簡報列印）
* **白話總額統計（Count-Up 跳動）**：
  * 主標題：`符合資格共 N 案｜最高可申請總額 NT$ Y 萬元`（透過 `requestAnimationFrame` Cubic Ease-Out 在 1.2 秒內從 0 累計跳動至目標值）。
  * 副標題：**`🎯 依歷史過件率折算・預估可入袋總額：約 Z 萬元`**（附 `?` 提示氣泡說明計算公式）。
* **右上角行動按鈕群**：
  1. **`📤 LINE分享`（亮綠色 `#06C755` 主按鈕）**：
     * **防雷設計**：絕不可在電腦版直接呼叫 `https://line.me/R/share?text=...`（電腦版會被重導向回 LINE 首頁），也不可將包含換行字元的多行長文塞進 `social-plugins.line.me/lineit/share?url=...&text=...`（會因雙重編碼觸發 `/lineit/login` 之 `HTTP ERROR 400`）。
     * **正確實作**：點擊後立即將完整多行摘要＋`?taxId=` 專屬連結複製到剪貼簿，並在桌機版彈出內建的 **「📤 LINE 分享補助快篩結果」互動視窗（`#lineShareModal`）**，提供：
       * 多行摘要預覽框（可直接於電腦版 LINE 按 `Cmd+V` / `Ctrl+V` 貼上）。
       * **`💬 喚起電腦／手機 LINE App 傳送`**：呼叫原生 `line://msg/text/${encodeURIComponent(fullText)}` 直接喚起電腦或手機內的 LINE App。
       * **`🌐 LINE 網頁版分享連結`**：僅傳遞純淨的 `url` 參數（`https://social-plugins.line.me/lineit/share?url=${encodeURIComponent(shareUrl)}`），零錯誤開啟官方網頁分享器。
  2. **`📄 匯出 A4 決策簡報 (PDF / 列印)`**：呼叫 `window.print()`，搭配 `@media print` 自動將所有符合卡片的雙欄抽屜展開並隱藏導覽列與無關按鈕。
  3. **`📥 下載純文字檢核表 (.txt)`**：保留於下方作為次要文字連結。
* **黃金 3 步推薦卡 ＆ 預約顧問免費初審 CTA**：
  * 顯示前 3 名最優先推薦方案，底部配置 **`💬 沒空寫計畫書？預約顧問免費初審`** 按鈕（開啟 `#consultModal` 免費初審預約視窗）。

### 4. 3.5 秒無條件篩選等待 ＋ 瀑布流卡片（首屏財務時程露出 ＆ 老闆/幕僚雙欄抽屜）
* **3.5 秒篩選動態**：每次查詢統編或切換條件時，下方無條件等待 `3,500ms`，顯示轉動圖示、「**正在為您篩選適合申請案件...**」與漸進光條；滿 3.5 秒後以 `@keyframes waterfallCardIn`（每張間隔 `120ms`）由上而下浮現卡片（展開／收合單張卡片細節時傳入 `renderAll(false)`，不重新觸發 3.5 秒等待）。
* **卡片收合狀態（首屏直見關鍵指標）**：
  * 顯示過件率白話燈號（`🟢 過件率極高（88%）・免寫厚重計畫書` 等）、計畫名稱、一句話亮點。
  * 直接露出 **`💰 補助比例／自籌要求`**（如 `100% 實報實銷／免企業自籌款` 或 `政府補助上限 50%（企業需自籌 50%）`）與 **`⏳ 申請時程狀態`**。
  * 右側顯示最高補助上限、`🎯 預估入袋金額`、`🔗 前往計畫申辦入口 ↗`（直連該計畫 Deep Link）與 `💬 預約顧問初審`。
  * 整塊卡片標題與金額區皆設有 `onclick="toggleCardDetail(id)"` 可直接點開抽屜。
* **卡片展開狀態（左右雙欄分工 `.grant-card-drawer`）**：
  * **左欄【👔 老闆決策重點】**：補助比例與額度計算、申請期限與審查門檻、以及粉紅高對比警告框 **「⚖️ 資格紅線與互斥條款提醒」**。
  * **右欄【📋 幕僚送件執行】**：支援互動打勾的 **「📋 送件應備文件自我檢核表」**（勾選 Checkbox 時即時更新 `已備齊 X/Y 項` 進度），以及底部申辦入口與作業要點連結。

---

## 五、 3D 政策浮島沙盤版規格（`taiwan_grant_island_3d.html`）

參考 [沈伯洋 HEART 政策島](https://puma.taipei/heart-island) 之微縮模型美學（Tabletop Miniature Diorama），以獨立檔案實作，並與 2D 版共用同一套資料與規則引擎：

### 1. 視覺風格與 6 座蜂巢狀六角形浮島配置
* **海面與光影**：海面與背景採用粉藍綠色（`#5caab9`），搭配柔和半球光（`HemisphereLight`）與開啟 `PCFSoftShadowMap` 陰影的暖陽方向光（`DirectionalLight`）。
* **6 座緊密拼接的六角形主題島嶼（`ISLAND_CONFIGS`）**：
  * 每座島由下層米白石材斜坡底座、上層主題色六角平台、以及外圈**雙色立體條紋護欄（`createStripedHexRim`：黃黑斜紋、紅白條紋、橘藍積木）**構成。
  * **島上微縮地景（`createIslandMiniatureDiorama`）**：
    * `01 AI 與雲端`：紅磚鐘樓、主政大樓、橘色穿梭小巴士、圓潤多球體樹冠（Puffy Trees）。
    * `02 研發創新`：白色研發圓頂建築、黃黑戶外展演舞台、藍色實驗室側翼。
    * `03 人才培訓`：橘頂學院建築、白色尖頂市集帳篷攤位、校園林木。
    * `04 智慧製造`：綠地測試球場、階梯看台、橘頂控制站。
    * `05 淨零節能`：層疊綠丘、葉片會動態旋轉的白色風力發電機（`rotatingBlades`）、濃密都市微森林。
    * `06 行銷海外`：港灣倉庫、紅藍綠堆疊貨櫃、延伸入海的木棧碼頭。

### 2. 9 座跨島連接橋樑與外圍衛星沙洲
* **跨島橋樑（`BRIDGE_LINKS` + `createBridgeBetweenIslands`）**：在相鄰六角島的水道之間架設 4 種實體連接橋樑：
  1. **黃色護欄跨海行人天橋**（`yellow_truss`）
  2. **白色橋塔雙向斜張車道橋**（`cable_road`，含白色車道分隔線）
  3. **橘白藍彩色方塊浮筒步道橋**（`colorful_pontoon`）
  4. **溫潤木棧跨海步道橋**（`wood_pier`）
* **外圍裝飾小沙洲與搖曳帆船（`createSurroundingSatelliteIsletsAndBoats`）**：於群島外圍海面配置「紅白條紋燈塔小島」、「雙色陽傘沙灘小島」、「綠丘沙洲」，以及 6 艘隨波微幅搖曳的「橘底座白帆小船」。

### 3. 全場景 66 位不同穿搭外觀之 Q 版角色隨機走動（`walkingCharacters`）
* 建立 **10 款不同穿搭與外觀特徵** 的 3D Q 版人偶（`createChibiCharacterMesh`：包含橘背心＋蓬鬆捲髮＋圓框眼鏡導覽員、藍西裝企業代表、白袍背包工程師、黃安全帽廠長、紅帽 T 設計師、綠背心永續師等）。
* 每座島上配置 **8 位角色**在島內隨機挑選散步座標走動與駐足，每座跨島橋樑上配置 **2 位行人**來回穿梭；走動時透過正弦波同步驅動左／右腿與左／右手臂前後擺動及身體輕快彈跳。

### 4. 3D 座標投影標籤、平滑運鏡（Smooth Fly-To）與雙模式切換
* **純白圓角膠囊島名牌（`.heart-island-pill`）**：透過 `worldVec.project(camera)` 將 3D 座標即時投影為銳利的 HTML 標籤，呈現「橘紅編號 ＋ 粗體島名 ＋ 綠底符合案數與總額」。
* **島上補助地標（`.grant-pin-marker`）**：3.5 秒雷達波紋掃描完成後，各島上方以彈跳動畫浮現符合資格的代表補助標記（`💰 最高 X 萬｜計畫簡稱`）。
* **點擊飛近與右側毛玻璃詳情抽屜（`#islandSideDrawer`）**：點擊任一轉型方向按鈕、3D 島嶼或補助標記時，鏡頭透過 `lerp` 阻尼平滑飛近該島，並於右側滑出詳情抽屜呈現完整條件與申辦入口。
* **頂部雙模式切換**：內建 `[🏝️ 3D 群島地圖] [📋 2D 瀑布流清單]` 一鍵切換，並提供跨頁連結直通獨立 2D 版。

---

## 六、 實戰踩坑防雷指南（AI 重製時必須嚴格遵守的 6 大鐵律）

1. **【防雷 1】統編邏輯檢核權重不可誤植**：
   * 財政部標準權重陣列為 `[1, 2, 1, 2, 1, 2, 4, 1]`，切勿寫成 `[1, 2, 1, 2, 4, 1, 4, 1]`，否則會導致 `28458491`、`22099131`（台積電）等大量合法統編被誤判失敗。
2. **【防雷 2】社團法人／協會統編位於 g0v API 的 `財政部` 子物件**：
   * 查詢如 `00651251`（社團法人台灣數位轉型協會）時，`company.g0v.ronny.tw/api/show/00651251` 回傳的 `data` 沒有 `公司名稱` 或 `商業名稱`，必須讀取 `data["財政部"]["營業人名稱"]` 與 `data["財政部"]["營業地址"]`。
3. **【防雷 3】`E605010`（電腦設備安裝業）屬於服務業，非製造業**：
   * 經濟部營業項目代碼只有 `C`（製造業）與 `D`（電力燃氣）映射為 `manufacturing`；`E` 開頭（如 `E605010`）必須映射為 `service`，否則資服業會被誤判去申請工廠補助。
4. **【防雷 4】前端 `evaluateGrant` 欄位名稱必須與 `grants_rules.json` 100% 一致**：
   * 讀取標題用 `grant.title`（非 `grant.name`）、機關用 `grant.authority`（非 `grant.agency`）、權重用 `grant.easeWeight`（非 `grant.weights.historicalApprovalRate`）、檢核表用 `grant.checklist`（非 `grant.prepDocs`），避免發生 `TypeError: Cannot read properties of undefined` 導致下方補助卡片空白。
5. **【防雷 5】桌機版 LINE 分享不可用 `line.me/R/share`，且 `social-plugins` 不可帶多行換行文字**：
   * `https://line.me/R/share` 在電腦版會直接跳回 LINE 首頁；而 `https://social-plugins.line.me/lineit/share?url=...&text=...` 若傳入含 `\n` 的多行長文，重導向至 `/lineit/login` 時會拋出 `HTTP ERROR 400`。桌機版應採用內建 `#lineShareModal` 視窗（自動複製全文至剪貼簿 ＋ 提供 `line://msg/text/...` 喚起電腦版 LINE App ＋ 僅傳遞純淨 `?url=` 給 `social-plugins.line.me`）。
6. **【防雷 6】GitHub Actions 自動更新排程不宜掛載 `on: push` 自動 Commit**：
   * 若在 `.github/workflows/weekly-sync-and-pages.yml` 設定每次 `push` 都讓 `github-actions[bot]` 修改時間戳記並自動 `git commit & push`，會導致本機下一次推送時因遠端有新 Commit 而被拒絕（`! [rejected] main -> main (fetch first)`）。應僅設定 `schedule`（每週定期）與 `workflow_dispatch`（手動觸發）。

---

## 七、 自動化驗收與 GitHub Pages 部署指令

### 1. 本機一鍵注入與 JavaScript 引擎驗收指令
在終端機執行以下指令，即可自動完成 48 筆補助規則稽核、SQLite 同步、HTML 原子注入與語法驗證：

```bash
python3 update_portal_data.py
```

### 2. 部署至 GitHub Pages 指令
```bash
git init
git branch -M main
git add -A
git commit -m "feat: initial release of 2026 DTI Government Grant Matcher (2D & 3D Island)"
git remote add origin https://github.com/<您的GitHub帳號>/<您的Repo名稱>.git
git push -u origin main
```
推送後至 GitHub Repo 的 **Settings ➔ Pages ➔ Build and deployment**，將 Source 設為 `Deploy from a branch`、Branch 選 `main` / `/(root)` 並儲存，等待約 1 分鐘即可透過以下兩個網址使用：
* **2D 跨世代高管清單版**：`https://<您的GitHub帳號>.github.io/<您的Repo名稱>/`（或 `/taiwan_grant_matcher.html`）
* **3D 政策浮島沙盤版**：`https://<您的GitHub帳號>.github.io/<您的Repo名稱>/taiwan_grant_island_3d.html`
