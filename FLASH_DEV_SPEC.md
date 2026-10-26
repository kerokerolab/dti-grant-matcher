# 2026 DTI 政府補助統編一鍵媒合儀表板 — Flash 模型專屬開發規格書 v2.1 (FLASH_DEV_SPEC.md)

> **給 Flash 開發模型的執行指令（System Instruction for Flash）**
> 請嚴格依照本規格書 v2.1 更新 `/Users/alantsai/Documents/gemini/2026_DTI政府補助快選儀表板/taiwan_grant_matcher.html`，並執行 `python3 update_portal_data.py` 將 48 筆全國補助規則與 22 家預抓取企業注入 `taiwan_grant_matcher.html` 與 `index.html`，最後執行第二節的自動化驗收腳本確認 100% 通過。

---

## 一、本次版面與互動調整核心規格（v2.1 必做規格）

### 1. 還原純「8 碼統一編號」查詢（移除 Autocomplete 與名稱模糊搜尋）
- **輸入框（`#ubnInput`）**：
  - 設為 `type="text" inputmode="numeric" maxlength="8" autocomplete="off"`，`placeholder="請輸入 8 碼統一編號（例如：28458491）"`。
  - 移除 `#autocompleteDropdown` 下拉選單容器與 `searchRemoteCompaniesByName` / `api/search?q=` 邏輯。
  - 保留財政部 8 碼統編邏輯檢核碼驗證（`validateTaiwanUBN`）。
- **隱藏連線模式切換器，預設一律走遠端 API**：
  - 畫面不得出現 `.conn-btn` 或 `#sqliteConfigBar`。預設呼叫 `fetchFromRemoteG0vApi(ubn)`，若離線則自動無感退回本地 `COMPANIES_DB` 快取。

### 2. 省略 STEP 2，將「公司人數」與「進階篩選」收合進 STEP 1 工商條件下方
- **省略 STEP 2 獨立區塊**：完全移除 `STEP 2` 標題列與獨立的進階篩選展開鈕。
- **一行式工商與人數膠囊摘要列（`#companySummaryPills`）**：
  - 常駐顯示一列精簡膠囊：`🏢 公司名稱`、`統編`、`📍 登記縣市`、`💰 資本額`、`🏭 製造業/💼 商業服務業`、`👥 員工人數區間`。
  - 右側配置 `#btnToggleCompanyDrawer`（「`⚙️ 檢視或修改工商與人數條件 ▾`」）。
- **初始採收合狀態的 `#companyDetailDrawer`（預設 `class="hidden ..."`）內部由上而下順序**：
  1. **1. 工商登記基本條件**：正式商工登記資訊摘要 (`#companyFullMeta`) ＋ 4 欄模擬設定（登記縣市 `#simCounty`、實收資本額 `#simCapital`、業別映射 `#simSector`、工廠登記 `#simFactory`）。
  2. **2. 貴公司目前勞保投保員工人數區間**（緊接在工商條件正下方）：`👤 30 人以下（含微型）`、`👥 31 ～ 199 人`、`🏢 200 人以上` 三顆 `.emp-btn` 按鈕。
  3. **3. 進階篩選條件**（緊接在公司人數下方）：精確勞保人數輸入框 (`#exactEmpCount`)、今年度已領過升級轉型補助互斥排除 (`#chkPriorUpgrade`)、自動隱藏已截止梯次 (`#chkHideExpired`)。
- **單行轉型方向過濾鈕（`#goalGroup`）接著放在收合區正下方**：
  - 採用單行水平排列（`flex items-center gap-2 overflow-x-auto no-scrollbar`），左側為 `🎯 轉型方向：`，右側同行排列 7 顆精簡文字膠囊鈕：
    - `全部需求` (`data-goal="all"`)
    - `01 AI 與雲端` (`data-goal="cloud_ai"`)
    - `02 研發創新` (`data-goal="rd_innov"`)
    - `03 人才培訓` (`data-goal="training"`)
    - `04 智慧製造` (`data-goal="smart_mfg"`)
    - `05 淨零節能` (`data-goal="carbon"`)
    - `06 行銷海外` (`data-goal="export_mkt"`)

### 3. 第一屏（Above the Fold）直接看到符合資格區塊 ＋ 3.5 秒篩選等待 ＋ 累計跳動 ＋ 瀑布流
- **緊湊化垂直高度**：縮減導覽列與 STEP 1 卡片內外距（`py-4 space-y-4`），確保開啟網頁第一屏免捲動即可直接看到深藍色「**符合資格共 N 案｜最高可申請總額 NT$ Y 萬元**」區塊與下方的「**✅ 符合貴公司資格的補助清單**」。
- **保留 3.5 秒篩選等待、Count-Up 累計跳動與瀑布流漸進浮現**：
  - 觸發查詢或條件變更時，`#countUpCases` 與 `#countUpMaxMan` 立即以 `requestAnimationFrame` 進行累計跳動。
  - 下方無條件等待 `3,500ms` 並顯示「`正在為您篩選適合申請案件...`」與動態進度光條，隨後以 `@keyframes waterfallCardIn`（每張延遲 `120ms`）由上而下漸進浮現符合卡片。

---

## 二、Flash 模型完工後的自動化驗收腳本（Verification Command）

修改完成並執行 `python3 update_portal_data.py` 後，必須執行以下驗收腳本確認 100% 通過：

```bash
python3 "/Users/alantsai/Documents/gemini/2026_DTI政府補助快選儀表板/update_portal_data.py" && python3 - << 'PY'
import json
html = open("/Users/alantsai/Documents/gemini/2026_DTI政府補助快選儀表板/taiwan_grant_matcher.html", encoding="utf-8").read()
idx_html = open("/Users/alantsai/Documents/gemini/2026_DTI政府補助快選儀表板/index.html", encoding="utf-8").read()
grants = json.load(open("/Users/alantsai/Documents/gemini/2026_DTI政府補助快選儀表板/grants_rules.json", encoding="utf-8"))

assert html == idx_html, "ERROR: index.html 與 taiwan_grant_matcher.html 不一致！"

# 1. 驗證已還原為純統編查詢、無 Autocomplete、無連線模式切換器、無 STEP 2
assert "autocompleteDropdown" not in html, "ERROR: autocompleteDropdown 尚未移除！"
assert 'maxlength="8"' in html, "ERROR: ubnInput 缺少 maxlength=8 限制！"
assert "conn-btn" not in html and "sqliteConfigBar" not in html, "ERROR: 連線模式切換器尚未移除！"
assert ">STEP 2<" not in html, "ERROR: STEP 2 標題尚未移除！"

# 2. 驗證 STEP 1 內部順序：工商條件 -> 公司人數 -> 進階篩選 -> 單行轉型方向過濾鈕
pos_drawer = html.find('id="companyDetailDrawer"')
pos_county = html.find('id="simCounty"')
pos_emp = html.find('data-emp="under30"')
pos_adv = html.find('id="exactEmpCount"')
pos_goal = html.find('id="goalGroup"')
assert -1 < pos_drawer < pos_county < pos_emp < pos_adv < pos_goal, (
    f"ERROR: STEP 1 區塊順序不正確: drawer={pos_drawer}, county={pos_county}, emp={pos_emp}, adv={pos_adv}, goal={pos_goal}"
)

# 3. 驗證 3.5 秒等待、累計跳動與瀑布流動畫存在
assert "正在為您篩選適合申請案件..." in html, "ERROR: 缺少『正在為您篩選適合申請案件...』提示文字！"
assert "countUpCases" in html and "countUpMaxMan" in html, "ERROR: 缺少數字累計跳動元素！"
assert "waterfallCardIn" in html, "ERROR: 缺少瀑布流漸進式動畫 waterfallCardIn！"

# 4. 驗證 48 筆全國補助案皆已寫入
assert len(grants) >= 48, f"ERROR: 補助案數量不足 ({len(grants)})"
for g in grants:
    assert g["officialUrl"] in html, f"ERROR: 缺少專案入口網址 {g['officialUrl']}"

print("ALL FLASH DEV SPEC v2.1 CHECKS PASSED 100%!")
PY
```
