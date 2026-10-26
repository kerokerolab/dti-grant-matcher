# 2026 DTI 政府補助統編一鍵媒合儀表板 — Flash 模型專屬開發規格書 v2.0 (FLASH_DEV_SPEC.md)

> **給 Flash 開發模型的執行指令（System Instruction for Flash）**
> 請嚴格依照本規格書 v2.0 更新 `/Users/alantsai/Documents/gemini/2026_DTI政府補助快選儀表板/taiwan_grant_matcher.html` 與 `update_portal_data.py`，並執行 `python3 update_portal_data.py` 將 48 筆全國補助規則與 22 家預抓取企業注入 `taiwan_grant_matcher.html` 與 `index.html`，最後執行第五節的自動化驗收腳本確認 100% 通過。

---

## 一、本次三大核心升級需求（v2.0 必做規格）

### 1. 統編 ＋ 企業名稱模糊搜尋配 Autocomplete（邊打邊選）
- **輸入框改造**：
  - 移除 `#ubnInput` 的 `maxlength="8"` 限制，加入 `autocomplete="off"`。
  - `placeholder` 設為：`"請輸入企業名稱關鍵字（如：哇寶、威鴻）或 8 碼統編"`。
  - 在 `#ubnInput` 外層建立 `relative flex-1` 容器，下方放置 `#autocompleteDropdown` 下拉選單容器。
- **邊打邊選雙軌搜尋邏輯**：
  - **本地快取 0 延遲模糊比對**：當使用者輸入文字時，立即比對 `COMPANIES_DB` 內所有企業之 `name`、`ubn` 與 `county`，即時顯示匹配建議。
  - **遠端全國公司名稱搜尋 API（300ms Debounce）**：當輸入字數 `>= 2` 且非純 8 碼統編時，防抖 300ms 後透過 `fetch` 呼叫 `https://company.g0v.ronny.tw/api/search?q=${encodeURIComponent(query)}`，解析回傳之全國真實企業清單（提取 `統一編號`、`公司名稱`/`商業名稱`、`公司所在地`、`實收資本額(元)`、`所營事業資料`），寫入 `COMPANIES_DB` 快取並渲染至 `#autocompleteDropdown`。
  - **互動支援**：支援滑鼠點擊建議項目，以及鍵盤 `ArrowDown`、`ArrowUp`、`Enter`、`Escape` 選取；選中後將統編填入 `#ubnInput`，關閉下拉選單，並立即啟動補助篩選。

### 2. 隱藏查詢連線模式切換器，Default 一律走遠端 API
- **移除連線模式 UI**：
  - 完全移除畫面上方的「🔌 企業統編查詢連線模式（遠端公開 API / 本地 SQLite / 離線快取）」切換區塊（不得出現 `.conn-btn` 或 `#sqliteConfigBar`）。
- **底層預設邏輯**：
  - 預設固定使用遠端 API 即時查詢（`fetchFromRemoteG0vApi` 與 `searchRemoteCompaniesByName`），若網路離線或查無資料時自動無感退回本地 `COMPANIES_DB` 快取。

### 3. 無條件等待 3～5 秒 ＋ 數字累計跳動（Count-Up）＋ 瀑布流漸進式呈現符合案件
- **階段一（0.0s 起）：預先呈現總案數與最高可申請金額，並啟動累計跳動（Count-Up Animation）**：
  - 當觸發查詢或篩選條件變更時，先由 Rule-Based 引擎在背景算出符合資格案數 `N`（`#countUpCases`）與最高可申請總額 `Y` 萬元（`#countUpMaxMan`）。
  - 使用 `requestAnimationFrame` 在 `1,200ms` 內將 `N` 與 `Y` 由 `0` 累計跳動至最終數值。
- **階段二（0.0s ～ 3.5s）：無條件等待 3.5 秒並顯示動態篩選提示**：
  - 在 `3,500ms`（落在 3～5 秒區間）等待期間，於 `#eligibleGrantsContainer` 顯示動態篩選卡片，主標題必須包含文字：**`正在為您篩選適合申請案件...`**，搭配進度光條與階段副標題。
- **階段三（3.5s 後）：瀑布流漸進式（Staggered Waterfall Reveal）浮現符合卡片**：
  - 等待時間結束後，移除載入提示，渲染符合資格的補助卡片，每張卡片套用 CSS Keyframes `@keyframes waterfallCardIn`（由 `opacity: 0; transform: translateY(24px)` 漸變至 `opacity: 1; transform: translateY(0)`），並依序設定 `animation-delay: ${index * 120}ms`，達成由上而下瀑布流漸進浮現效果。
  - 注意：當使用者僅點擊卡片上的「➕ 點選展開：申請條件、防雷提醒與應備文件 ▾」手風琴按鈕時，直接展開該張卡片，**不得**重新觸發 3.5 秒等待動畫。

---

## 二、Flash 模型完工後的自動化驗收腳本（Verification Command）

修改完成並執行 `python3 update_portal_data.py` 後，必須執行以下驗收腳本確認 100% 通過：

```bash
python3 "/Users/alantsai/Documents/gemini/2026_DTI政府補助快選儀表板/update_portal_data.py" && python3 - << 'PY'
import json
html = open("/Users/alantsai/Documents/gemini/2026_DTI政府補助快選儀表板/taiwan_grant_matcher.html", encoding="utf-8").read()
grants = json.load(open("/Users/alantsai/Documents/gemini/2026_DTI政府補助快選儀表板/grants_rules.json", encoding="utf-8"))

# 1. 驗證連線模式切換器已隱藏、範例按鈕已移除
assert "conn-btn" not in html, "ERROR: 連線模式切換按鈕 conn-btn 尚未移除！"
assert "sqliteConfigBar" not in html, "ERROR: sqliteConfigBar 尚未移除！"
assert "preset-btn" not in html, "ERROR: preset-btn 尚未移除！"

# 2. 驗證企業名稱模糊搜尋與 Autocomplete 元件存在
assert "autocompleteDropdown" in html, "ERROR: 缺少 autocompleteDropdown 自動完成下拉選單！"
assert "company.g0v.ronny.tw/api/search" in html, "ERROR: 缺少企業名稱遠端模糊搜尋 API！"

# 3. 驗證 3~5 秒等待、累計跳動與瀑布流動畫存在
assert "正在為您篩選適合申請案件..." in html, "ERROR: 缺少『正在為您篩選適合申請案件...』提示文字！"
assert "countUpCases" in html and "countUpMaxMan" in html, "ERROR: 缺少數字累計跳動元素！"
assert "waterfallCardIn" in html, "ERROR: 缺少瀑布流漸進式動畫 waterfallCardIn！"

# 4. 驗證 48 筆全國補助案皆已寫入
assert len(grants) >= 46, f"ERROR: 補助案數量不足 ({len(grants)})"
for g in grants:
    assert g["officialUrl"] in html, f"ERROR: 缺少專案入口網址 {g['officialUrl']}"

print("ALL FLASH DEV SPEC v2.0 CHECKS PASSED 100%!")
PY
```
