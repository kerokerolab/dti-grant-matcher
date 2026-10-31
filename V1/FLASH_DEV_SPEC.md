# 2026 DTI 政府補助統編一鍵媒合儀表板 — Flash 模型專屬開發規格書 (FLASH_DEV_SPEC.md)

> **給 Flash 開發模型的執行指令（System Instruction for Flash）**
> 當使用者請你依照本文件進行開發時，請**嚴格遵守本規格書的每一項條件，不要自行發想額外區塊，也絕對不要串接任何 LLM / AI API**。所有資料與規則皆已預先準備於同目錄下的 `grants_rules.json` 與 `companies_db.json`。請直接依據下方規格更新 `/Users/alantsai/Documents/gemini/2026_DTI政府補助快選儀表板/taiwan_grant_matcher.html` 並同步複製至 `/Users/alantsai/Documents/gemini/2026_DTI政府補助快選儀表板/index.html`，完成後執行本文件最後的「自動化驗收腳本」確認 100% 通過。

---

## 一、專案核心架構與限制（Zero-AI / Rule-Based Mapping）

1. **100% 零 AI 運作（Zero-LLM Runtime）**：
   - 系統在執行期（Runtime）完全不呼叫任何生成式 AI 模型。
   - 所有的統編資料查詢、資格過濾、金額計算、互斥攔截與「黃金 3 步最佳組合包」排序，100% 由**預抓取的結構化資料庫（`companies_db.json` ＋ `grants_rules.json`）**搭配**純 JavaScript 確定性規則映射（Deterministic Rule-Based Mapping）**在瀏覽器端毫秒級完成。
   - 介面文案中不得出現「AI 數位體質健檢」或「AI 運算」字樣，一律改為**「規則引擎精算：年度最佳補助組合包」**。
2. **單檔免伺服器可執行 ＋ 外部 JSON 自動載入雙支援**：
   - 為確保使用者直接在電腦雙擊 `taiwan_grant_matcher.html` 或 `index.html`（`file://` 協定）時不會因瀏覽器 CORS 阻擋 `fetch('./grants_rules.json')` 而白畫面，請將 `grants_rules.json` 與 `companies_db.json` 的最新內容**同步內嵌為 HTML 內的預設常數（`DEFAULT_GRANTS_DB` 與 `DEFAULT_COMPANIES_DB`）**，並在 `DOMContentLoaded` 時嘗試以 `fetch()` 讀取外部 `.json` 覆蓋（若處於 `file://` 環境 `fetch` 失敗則無縫使用內嵌常數）。

---

## 二、介面修改清單（針對現有 `taiwan_grant_matcher.html` 之精確變更）

### 1. 必須移除的區塊（Strict Removal List）
- **移除「5 組真實企業範例按鈕」**：
  - 刪除統編輸入框（`#ubnInput`）下方的「⚡ 點擊一鍵帶入 5 組真實企業統編範例」整塊 DOM 與所有 `.preset-btn` 按鈕，讓 STEP 1 搜尋區保持極簡乾淨。
  - 在 `#ubnInput` 的 `placeholder` 顯示：`"請輸入 8 碼企業統一編號（例如 28458491）"`。
- **移除底部的「顧問與開發者驗證專區（5 組統編盲測表）」抽屜**：
  - 刪除頁面最底部的 `#btnToggleDevDrawer` 與 `#devDrawerContent`（包含 5 組真實企業盲測對照表），僅保留「🛡️ 系統已自動為您過濾的不符資格／已截止補助案」這一個底部收合抽屜。
- **移除工商底稿中的測試備註列**：
  - 在展開的工商詳細資料區（`#companyFullMeta`）中，不顯示測試用 `note` 欄位，僅呈現正式商工登記欄位（統一編號、組織型態、核准設立日、登記地址、商工公示查詢連結）。

### 2. 必須保留與強化的 UI 設計規範（大字級 ＋ 手風琴展開）
- **大字級規範（禁止使用 `12px / text-xs`）**：
  - 全站 `body` 基準字級為 `16px`（`text-base`），最小輔助標籤為 `14px`（`text-sm`）。
  - 補助卡片標題為 `20px~24px`（`text-xl sm:text-2xl font-extrabold`），最高補助金額為 `24px~30px`（`text-2xl sm:text-3xl font-extrabold text-emerald-700`）。
- **STEP 1：一行式工商摘要膠囊列 ＋ 點選展開微調面板**：
  - 輸入統編後，若命中 `companies_db.json`，自動帶出公司名稱、縣市、資本額、產業別與工廠登記狀態；若輸入未預先快取的 8 碼統編，通過財政部統編 Checksum 檢核後，自動展開「⚙️ 檢視或修改工商條件」面板，讓使用者直接透過下拉選單設定縣市、資本額、產業分類（映射 `industryCodePrefixMapping`）與工廠登記。
- **STEP 2：兩排直覺大按鈕篩選 ＋ 進階篩選收合手風琴**：
  - 第一排：`30 人以下（含微型）`、`31 ～ 199 人`、`200 人以上`。
  - 第二排：6 大數位轉型需求分類按鈕（`全部轉型需求`、`01 AI 與雲端工具導入`、`02 企業研發與創新 (SBIR/TIIP)`、`03 員工數位培訓與人才`、`04 智慧製造與產線升級`、`05 淨零與智慧節能轉型`、`06 數位行銷及海外拓展`）。
  - 進階篩選抽屜（預設收合）：包含「精確勞保人數輸入框 `#exactEmpCount`」、「今年度已領升級轉型互斥補助勾選框 `#chkPriorUpgrade`」、「自動隱藏已截止梯次 `#chkHideExpired`」。
- **方案 B 專屬「年度最佳補助組合包（黃金 3 步）」深藍摘要卡**：
  - 標題改為：`✨ 規則引擎精算 ＆ 年度最佳補助組合包`。
  - 顯示符合總案數、最高可申請總額（萬元）、依過件率權重計算之期望值總額（萬元），以及「📥 下載專屬補助攻略與檢核表 (.txt)」按鈕。
  - 顯示排序前 3 名的黃金組合卡片（點擊任一卡片自動捲動至下方對應補助卡並展開其手風琴）。
  - 「📊 點此展開各計畫最高上限 vs. 權重期望值對比圖 ▾」預設收合，點擊才展開。
- **手風琴式（Accordion）符合資格補助清單**：
  - 每張卡片預設只顯示：① 主辦機關標籤＋轉型分類標籤＋難易度標籤（`easyTag`）、② 計畫名稱与右側最高補助金額、③ 一句話白話亮點（`shortHighlight`）、④ 底部「➕ 點選展開：申請條件、防雷提醒與應備文件 ▾」按鈕與**直達該案主要入口的按鈕**。
  - 點擊展開按鈕後，直接在該卡片下方滑出（Accordion）：補助比例明細、申請期限、審查委員防雷與互斥提醒、可打勾的應備文件檢核表（Checklist）。支援多張卡片同時展開對比。

---

## 三、官方簡章網站「直達各案主要申辦入口（Deep Links）」規範

所有補助卡片與展開區域的官方連結，**嚴禁只連到部會首頁**（如 `wda.gov.tw`、`trade.gov.tw`、`moeaea.gov.tw`、`moenv.gov.tw`），必須 100% 採用 `grants_rules.json` 中的 `officialUrl`（以及選配的 `secondaryUrl` 備用法規／公告連結）：

- 當 `grant.secondaryUrl` 存在時，在手風琴展開區內同時提供「🔗 前往本案專屬申辦入口 ↗」(`grant.officialUrl`) 與「📄 查看官方作業要點／公告專頁 ↗」(`grant.secondaryUrl`) 兩個直達連結。
- 卡片外層右上角按鈕文案統一改為：**`🔗 前往計畫申辦入口 ↗`**（連結至 `grant.officialUrl`）。

| 計畫 ID | 計畫名稱 | 主要申辦入口直達網址 (`officialUrl`) | 備用要點／公告專頁 (`secondaryUrl`) |
| :--- | :--- | :--- | :--- |
| `MOEA-DOC-30SERV` | 30人以下服務業數位轉型培力補助 | `https://www.dtts.org.tw/` | `https://www.aoc.gov.tw/showPublic/320` |
| `MOEA-SMESA-30MFG` | 30人以下製造業數位轉型培力補助 | `https://www.sme.gov.tw/caas/article-caas-3066-17217` | `https://law.moea.gov.tw/LawContent.aspx?id=GL001795` |
| `MOEA-IDA-CLOUD-AI` | 雲市集工業館－AI 工具庫點數補助計畫 | `https://www.sme.gov.tw/caas/article-caas-3059-17073` | `null` |
| `MOEA-IDA-CLOUD-SOL-EXPIRED` | 115年度雲市集工業館－一般雲端解決方案點數補助 | `https://www.sme.gov.tw/caas/article-caas-3059-17073` | `null` |
| `MOEA-DOC-SMART-SERV` | 商業服務業智慧化與數位轉型推動計畫 | `https://www.smebiz.org.tw/project-digital.php` | `null` |
| `MOEA-DOC-SMART-CARBON` | 商業服務業智慧減碳補助計畫 | `https://www.sme.gov.tw/caas/article-caas-3066-15510` | `null` |
| `MOEA-EA-ENERGY` | 商業服務業節能設備汰換與系統節能專案補助 | `https://www.essc.org.tw/subsidy/change_apply/info.aspx` | `https://www.essc.org.tw/subsidy/eco_apply_info/info.aspx` |
| `MOENV-RECA-CIRCULAR` | 補助資源循環創新及研究發展計畫 | `https://www.moenv.gov.tw/information-service/convenience-services/subsidy/reca/36771.html` | `https://www.moenv.gov.tw/information-service/convenience-services/subsidy/reca/1413.html` |
| `MOEA-IDA-MFG-LEAP` | 協助中小型製造業數位轉型躍升計畫 | `https://www.ida.gov.tw/ctlr?PRO=project.rwdProjectView&id=2814` | `https://assist.nat.gov.tw/wSite/ct?xItem=289605&ctNode=150&mp=2` |
| `MOL-WDA-HR-UPGRADE` | 企業人力資源提升計畫（大人提／小人提） | `https://tkyhkm.wda.gov.tw/cp.aspx?n=29A4659822CE8222` | `https://0800280280.sme.gov.tw/ebook/html/page.php?id=378&gid=72&bgid=40` |
| `MOEA-TITA-EXPORT` | 補助業界開發國際市場計畫 | `https://www.imdp.org.tw/` | `https://www.trade.gov.tw/Pages/Detail.aspx?nodeid=39&pid=784718` |
| `MOEA-SMESA-SBIR-CENTRAL` | 小型企業創新研發計畫 (中央型 SBIR) | `https://sbir.sme.gov.tw/` | `https://sbir.org.tw/cross/info` |
| `MOEA-IDA-TIIP` | 產業升級創新平台輔導計畫 (TIIP) | `https://eii.nat.gov.tw/tiip/plan_type.php?Mid=8` | `https://assist.nat.gov.tw/GIP/wSite/ct?xItem=289624&ctNode=150&mp=2` |
| `MODA-ADI-DIGIPLUS` | DIGITAL+ 數位創新補助平台 | `https://digiplus.adi.gov.tw/` | `null` |
| `LOCAL-TAIPEI-SITI` | 臺北市產業發展獎勵補助計畫 (SITI) | `https://www.industry-incentive.taipei/about/3` | `https://www.industry-incentive.taipei/about/9` |
| `LOCAL-ALL-COUNTIES-SBIR` | 各縣市地方產業創新研發推動計畫 (地方型 SBIR) | `https://startup.sme.gov.tw/home/modules/funding/detail/?sId=87` | `https://sbir.sme.gov.tw/` |

---

## 四、核心 Rule-Based Mapping 演算法規格（Flash 請直接套用）

請確保前端 JavaScript 中的 `evaluateGrantsForCompany()` 採用以下確定性規則邏輯（欄位名稱與 `grants_rules.json` 完全一致）：

```javascript
function evaluateGrantsForCompany() {
  const comp = state.currentCompany;
  // 法規閘門 1：中小企業認定標準（實收資本額 <= 1億元 或 經常僱用員工數 < 200人）
  const isSME = (comp.paidInCapital <= 100000000) || (state.empRange !== "over200" && state.exactEmpCount < 200);
  // 法規閘門 2：30人以下微小型企業認定
  const isUnder30 = state.empRange === "under30" && state.exactEmpCount <= 30;

  const eligible = [];
  const excluded = [];

  GRANTS_DB.forEach((grant) => {
    const reasons = [];

    // 1. 時效閘門
    if (grant.isExpired && state.hideExpired) {
      reasons.push("本梯次已截止受理（" + grant.deadline + "）");
    }
    // 2. 中小企業資格閘門
    if (grant.rules.smeOnly && !isSME) {
      reasons.push("不符中小企業認定標準（實收資本額逾 1 億元且經常僱用員工達 200 人以上）");
    }
    // 3. 員工人數上限閘門
    if (grant.rules.maxEmployees !== null && !isUnder30) {
      reasons.push(`超過員工人數上限（限 ${grant.rules.maxEmployees} 人以下，目前設定為 ${state.exactEmpCount} 人）`);
    }
    // 4. 組織型態閘門 (company vs business)
    if (!grant.rules.allowedOrgTypes.includes(comp.orgType)) {
      reasons.push("組織型態不符（限依『公司法』設立之公司，獨資／合夥商號不適用）");
    }
    // 5. 產業別閘門 (manufacturing vs service)
    if (!grant.rules.allowedSectors.includes(comp.sector)) {
      const reqSectorName = grant.rules.allowedSectors.includes("manufacturing") ? "製造業" : "商業服務業";
      reasons.push(`產業別不符（限「${reqSectorName}」，貴公司為「${comp.sectorLabel}」）`);
    }
    // 6. 工廠登記閘門
    if (grant.rules.requireFactoryReg && !comp.hasFactoryReg) {
      reasons.push("缺少工廠登記（要求具備合法工廠登記或特定工廠登記證）");
    }
    // 7. 設籍縣市閘門
    if (!grant.rules.allowedCounties.includes("ALL") && !grant.rules.allowedCounties.includes(comp.county)) {
      reasons.push(`設籍縣市不符（限設籍「${grant.rules.allowedCounties.join("／")}」，貴公司登記於「${comp.county}」）`);
    }
    // 8. 同年度互斥群組閘門
    if (grant.rules.mutexGroup === "MOEA_UPGRADE_2026" && state.priorUpgradeConflict) {
      reasons.push("觸發同年度互斥條款（今年已獲低碳化／智慧化升級轉型或接班傳承補助）");
    }

    // 轉型需求分類過濾
    const goalFilteredOut = (state.selectedGoal !== "all" && grant.category !== state.selectedGoal);

    // 確定性金額試算公式（支援按人頭上限計算）
    let effectiveMaxMan = grant.maxSubsidyMan;
    if (grant.perEmployeeCapMan) {
      effectiveMaxMan = Math.min(grant.maxSubsidyMan, Math.max(1, state.exactEmpCount) * grant.perEmployeeCapMan);
    }

    // 固定權重計分公式（取代 AI 評分）
    const weight = grant.easeWeight || 0.6;
    const urgency = grant.urgencyWeight || 5;
    const expectedValueMan = Math.round(effectiveMaxMan * weight * 10) / 10;
    const rankScore = expectedValueMan * (1 + urgency * 0.05);

    const enriched = {
      ...grant,
      effectiveMaxMan,
      expectedValueMan,
      rankScore,
      reasons
    };

    if (reasons.length === 0 && !goalFilteredOut) {
      eligible.push(enriched);
    } else {
      if (goalFilteredOut && reasons.length === 0) {
        enriched.reasons = ["目前已篩選特定轉型方向（切換為「全部轉型需求」即可顯示）"];
      }
      excluded.push(enriched);
    }
  });

  eligible.sort((a, b) => b.rankScore - a.rankScore);
  return { eligible, excluded, isSME, isUnder30 };
}
```

---

## 五、Flash 模型完工後的自動化驗收腳本（Verification Command）

Flash 模型修改完 `taiwan_grant_matcher.html` 並同步複製到 `index.html` 後，**必須執行以下終端機指令**，確保所有條件 100% 通過才算完工：

```bash
cp "/Users/alantsai/Documents/gemini/2026_DTI政府補助快選儀表板/taiwan_grant_matcher.html" "/Users/alantsai/Documents/gemini/2026_DTI政府補助快選儀表板/index.html" && python3 - << 'PY'
import json
html = open("/Users/alantsai/Documents/gemini/2026_DTI政府補助快選儀表板/taiwan_grant_matcher.html", encoding="utf-8").read()
grants = json.load(open("/Users/alantsai/Documents/gemini/2026_DTI政府補助快選儀表板/grants_rules.json", encoding="utf-8"))

# 1. 驗證公司範例按鈕與盲測表已移除
assert "preset-btn" not in html, "ERROR: preset-btn 範例按鈕尚未移除！"
assert "btnToggleDevDrawer" not in html, "ERROR: 底部盲測表抽屜尚未移除！"
assert "AI 數位體質健檢" not in html, "ERROR: 仍殘留 AI 數位體質健檢字樣！"

# 2. 驗證所有 16 筆補助案的專屬入口網址 (Deep Links) 皆已寫入 HTML
for g in grants:
    assert g["officialUrl"] in html, f"ERROR: 缺少專案入口網址 {g['officialUrl']}"

# 3. 驗證不再出現純部會首頁連結
for bare_url in ['"https://www.wda.gov.tw/"', '"https://www.trade.gov.tw/"', '"https://www.moeaea.gov.tw/"', '"https://www.moenv.gov.tw/"']:
    assert bare_url not in html, f"ERROR: 仍殘留部會首頁網址 {bare_url}"

print("ALL FLASH DEV SPEC CHECKS PASSED 100%!")
PY
```
