# `taiwan_grant_matcher.html` 跨世代高管（20–70 歲）UI/UX 優化實作規格書

> **目標頁面**：[DTI 數位轉型學院｜政府補助統編一鍵快選](https://kerokerolab.github.io/dti-grant-matcher/taiwan_grant_matcher.html)  
> **核心任務**：在不破壞既有規則引擎、統編檢核與防雷攔截邏輯的前提下，重構前端視覺層級、決策文案與交辦工作流，讓 **20 歲新創創辦人（行動端、高效率）** 到 **70 歲傳產董事長（大字級、白話指標、一鍵交辦幕僚）** 都能在 10 秒內完成評估與後續行動。

---

## 一、 核心 UI/UX 改版規格對照表

| 模組區塊 | 現況問題描述 | 具體修改規格（HTML / CSS / 文案） |
| :---- | :---- | :---- |
| **1\. 全域字級與閱讀無障礙** | 展開抽屜內的應備文件、資格紅線與底部剔除原因字級僅 `12px–13px`，次要說明採 `#334155` | 1\. 基礎內文字級提升至 `16px`（`1rem`），行高設為 `1.65`，所有微型 Badge 不低於 `14px`。 2\. 於頂部 Header 右側（`🏝️ 開啟 3D 群島版` 旁）新增 **「`🔠 長輩大字模式`」** 切換按鈕，點擊後於 `<body>` 切換 `.large-text-mode`（全站字級放大 `1.25 倍`），並以 `localStorage` 記憶狀態。 |
| **2\. 決策指標白話化** | 英雄區與卡片使用「固定權重計算」、「權重期望值 750 萬 🔋」、「過件難易度權重 88%」等工程統計術語 | 1\. 將 `依固定權重計算之總期望值` 改為 **「依歷史過件率折算・預估可入袋總額」**。 2\. 將單卡 `權重期望值約 X 萬 🔋` 改為 **「🎯 預估入袋金額：約 X 萬元」**，並在旁邊加上 `?` 提示氣泡說明計算公式（最高上限 × 過件難易度權重）。 3\. 將 `過件難易度權重 88%` 轉為視覺化標籤（如：`🟢 過件率極高（88%）・免寫厚重計畫書`、`🟡 過件率中等（50%）・需完整研發計畫`）。 |
| **3\. STEP 1 輸入與雙軌查詢** | 預設直接帶入 `00651251`（台灣數位轉型協會），且僅支援 8 碼統編數字，高管在外常忘記統編 | 1\. 預設狀態標註醒目的 **「📌 目前顯示：範例預覽（社團法人台灣數位轉型協會）」** 提示條，避免老闆誤以為系統故障或只能查協會。 2\. 輸入框 Placeholder 改為 `請輸入 8 碼統編 或 公司名稱關鍵字`，並新增 `✕ 清空重填` 按鈕。 3\. 在統編輸入框下方新增 **「⚡ 忘記統編？點此用 30 秒三問快篩（選產業／人數／有無工廠）」** 快速切換按鈕，點擊後直接展開並聚焦至工商條件面板。 |
| **4\. 行動端與平板觸控熱區** | 抽屜展開列 `點選展開：申請條件... ▼`、分類膠囊 `01 AI 與雲端` 高度偏小，長輩在手機或 iPad 易誤觸 | 1\. 所有按鈕、篩選膠囊、人數選擇卡與收合觸發列的 `min-height` 統一設為 `48px`（符合 WCAG 2.2 AAA 觸控標準）。 2\. 將單張補助卡片的「標題區與金額區」整塊設為可點擊展開抽屜的熱區（排除外部連結按鈕本身）。 |

---

## 二、 針對「老闆決策與交辦習慣」的四大功能擴充

### 1\. 升級「一鍵轉交幕僚／特助」分享與 PDF 簡報匯出

* **修改位置**：深藍色英雄區（Hero Recommendation Card）右上角，原 `📥 下載專屬補助攻略與檢核表 (.txt)` 按鈕處。  
* **實作內容**：  
  1. **新增「`📤 LINE 傳給特助／財務代辦`」按鈕（主視覺亮綠色）**：點擊後自動組裝「公司名稱 \+ 符合案數 \+ 最高可申請總額 \+ 黃金 3 步推薦清單 \+ 帶統編參數的網址 (`?taxId=XXXXXXXX`)」，呼叫 LINE Share URL 或 Web Share API（電腦版支援一鍵複製交辦訊息並彈出 Toast 提示）。  
  2. **將 `.txt` 下載升級為「`📄 匯出 A4 決策簡報 (PDF / 列印)`」**：搭配 `@media print` 專用列印樣式，自動展開黃金 3 步與符合清單重點，隱藏頂部導覽與不相關按鈕，讓高管可直接存成漂亮 A4 PDF 呈報董事會或交辦部門。  
  3. **保留原 `.txt` 下載為次要文字連結**：改為小字連結 `下載純文字檢核表 (.txt)`。

### 2\. 卡片首屏（收合狀態）直接露出「自籌款比例」與「截止倒數」

* **修改位置**：`✅ 符合貴公司資格的補助清單` 中每一張補助卡片的外層（不需點開抽屜即可看到）。  
* **實作內容**：  
  1. 在「最高補助上限」與「預估入袋金額」下方，新增一列高對比關鍵財務指標：  
     * **💰 補助比例／自籌要求**：例如 `政府補助 50%（企業需自籌 50%）` 或 `100% 實報實銷（免自籌款）`。  
     * **⏳ 申請時程狀態**：例如 `🟢 隨到隨審` 或 `🔥 距離截止剩 14 天（115/XX/XX 止）`。

### 3\. 展開抽屜改為「老闆看重點 vs. 幕僚看執行」雙視角分頁（或雙欄）

* **修改位置**：每張補助卡片點開後的 `點選展開：申請條件、防雷提醒與應備文件 ▼` 抽屜內部。  
* **實作內容**：  
  * **左欄／Tab 1【👔 老闆決策重點】**：只放 **💰 補助比例與額度計算**、**⏰ 申請期限與過件率**、**⚖️ 資格紅線與互斥條款提醒（粉紅警告框）**。  
  * **右欄／Tab 2【📋 幕僚送件執行】**：放置 **📋 送件應備文件自我檢核表（支援勾選進度顯示 `已備齊 2/5 項`）**，以及底部的 `🔗 前往本案專屬申辦入口 ↗` 與 `📄 查看官方作業要點 ↗`。

### 4\. 新增「預約顧問免費初審」商業轉換出口（CTA）

* **修改位置**：深藍色英雄區底部，以及每張補助卡片的外部申辦按鈕旁。  
* **實作內容**：  
  * 在 `🔗 前往計畫申辦入口 ↗` 旁並列一個次要高轉換按鈕 **「`💬 沒空寫計畫書？預約顧問免費初審`」**，點擊後可開啟諮詢表單或導向官方 LINE／預約連結，並自動帶入目前選定的計畫名稱。

---

## 三、 前端實作程式碼範本（可直接整合至 `taiwan_grant_matcher.html`）

### 1\. CSS 無障礙字級變數、大字模式與列印樣式

```css
:root {
  --font-scale: 1;
  --text-xs: calc(14px * var(--font-scale));
  --text-sm: calc(15px * var(--font-scale));
  --text-base: calc(16px * var(--font-scale));
  --text-lg: calc(18px * var(--font-scale));
  --text-xl: calc(22px * var(--font-scale));
  --text-2xl: calc(28px * var(--font-scale));
  --touch-min-height: 48px;
}

/* 長輩大字模式：全站字級放大 1.25 倍 */
body.large-text-mode {
  --font-scale: 1.25;
}

/* 強化內文、紅線警告與剔除原因的對比度與行高 */
body {
  font-size: var(--text-base);
  line-height: 1.65;
  color: #0F172A;
}

.grant-card-details,
.exclusion-reason-box,
.checklist-item {
  font-size: var(--text-base);
  line-height: 1.7;
  color: #1E293B;
}

/* 確保所有互動元件符合 48px 觸控標準 */
button,
.accordion-trigger,
.category-tab-pill,
.employee-size-card,
select,
input[type="text"],
input[type="number"] {
  min-height: var(--touch-min-height);
}

/* A4 決策簡報列印專用樣式 */
@media print {
  header,
  .filter-controls-toggle,
  .category-tabs,
  .action-buttons-row,
  .excluded-grants-section {
    display: none !important;
  }
  .grant-card-drawer {
    display: block !important;
  }
  body {
    background: #FFFFFF !important;
    font-size: 12pt;
  }
}
```

### 2\. JavaScript 模組：長輩大字模式、URL 統編參數綁定與一鍵交辦幕僚

```js
// 1. 長輩大字模式切換與記憶
function toggleLargeTextMode() {
  const isLarge = document.body.classList.toggle('large-text-mode');
  localStorage.setItem('dti_large_text_mode', isLarge ? '1' : '0');
  const btn = document.getElementById('btn-large-text');
  if (btn) {
    btn.textContent = isLarge ? '🔠 標準字體' : '🔠 長輩大字模式';
    btn.setAttribute('aria-pressed', isLarge);
  }
}

// 初始化讀取大字模式與網址 taxId 參數
window.addEventListener('DOMContentLoaded', () => {
  if (localStorage.getItem('dti_large_text_mode') === '1') {
    document.body.classList.add('large-text-mode');
    const btn = document.getElementById('btn-large-text');
    if (btn) btn.textContent = '🔠 標準字體';
  }

  // 支援幕僚點開老闆分享連結時自動帶入統編
  const params = new URLSearchParams(window.location.search);
  const sharedTaxId = params.get('taxId');
  if (sharedTaxId && /^\d{8}$/.test(sharedTaxId)) {
    const taxInput = document.querySelector('#tax-id-input');
    if (taxInput) {
      taxInput.value = sharedTaxId;
      // 觸發原有的統編查詢函式
      if (typeof triggerGrantSearch === 'function') triggerGrantSearch();
    }
  }
});

// 2. 一鍵生成「交辦特助／財務」LINE 摘要並分享或複製
function shareToAssistant(companyName, taxId, matchedCount, maxTotalWan, expectedTotalWan, top3Grants) {
  const shareUrl = `${window.location.origin}${window.location.pathname}?taxId=${encodeURIComponent(taxId)}`;
  const top3Text = top3Grants
    .map((g, idx) => `  ${idx + 1}. ${g.title}（最高 ${g.maxAmount} 萬／預估入袋 ${g.expectedAmount} 萬）`)
    .join('\n');

  const message = [
    `【政府補助快篩交辦單】`,
    `🏢 評估單位：${companyName}（統編：${taxId}）`,
    `✅ 符合資格：共 ${matchedCount} 案`,
    `💰 最高可申請總額：NT$ ${maxTotalWan} 萬元（依過件率折算預估約 ${expectedTotalWan} 萬元）`,
    ``,
    `📌 優先評估「黃金 3 步組合包」：`,
    top3Text,
    ``,
    `👉 點此查看完整應備文件與防雷紅線檢核表：`,
    shareUrl
  ].join('\n');

  // 行動端優先使用系統原生分享或 LINE 分享，桌面端複製到剪貼簿並開啟 LINE 網頁轉發
  if (navigator.share) {
    navigator.share({
      title: `${companyName} - 政府補助快篩交辦單`,
      text: message,
      url: shareUrl
    }).catch(() => {});
  } else {
    navigator.clipboard.writeText(message).then(() => {
      alert('✅ 已複製「補助交辦摘要與專屬連結」！您可直接貼上至 LINE 群組或 Email 交辦給特助與財務部門。');
      window.open(`https://line.me/R/share?text=${encodeURIComponent(message)}`, '_blank');
    });
  }
}
```

---

## 四、 給補助案介面 AI 的執行指令（Prompt 貼上區）

你可以直接複製下方區塊貼回補助案介面的對話中：

```
請根據以下 UI/UX 優化規格，幫我直接修改 `taiwan_grant_matcher.html`：

1. **無障礙字級與長輩大字模式**：
   - 全站基礎內文字級調升至 `16px`，小標籤不低於 `14px`，加深內文顏色對比度（`#1E293B`）。
   - 在頂部 Header 新增「🔠 長輩大字模式」按鈕，切換 `body.large-text-mode`（透過 CSS 變數放大 1.25 倍字級並存入 `localStorage`）。
   - 所有可點擊按鈕、篩選膠囊、人數卡片與展開抽屜列的最小高度設為 `48px`。

2. **白話決策指標替換**：
   - 將所有「固定權重計算」、「權重期望值」文案改為「依歷史過件率折算・預估入袋金額」，並加上簡易提示說明計算方式。
   - 將過件難易度權重改為直覺燈號標籤（如：`🟢 過件率極高（88%）`）。

3. **STEP 1 預設範例提示與免統編快篩引導**：
   - 預設帶入的 `00651251`（社團法人台灣數位轉型協會）旁加上醒目的「範例預覽」標籤與「清空重填」按鈕。
   - 在統編輸入區下方新增「⚡ 忘記統編？點此用 30 秒三問快篩（選產業／人數／有無工廠）」引導按鈕，點擊後平滑展開並捲動至工商條件設定區。

4. **卡片首屏資訊強化與雙欄抽屜**：
   - 在每張補助卡片收合狀態下，直接顯示「企業自籌款比例（或 100% 實報實銷）」與「申請截止倒數／隨到隨審」Badge。
   - 展開抽屜內改為左右雙欄（行動端上下分區）：左欄「👔 老闆看重點（額度、期限、粉紅框資格紅線）」、右欄「📋 幕僚看執行（應備文件互動勾選清單、申辦入口連結）」。

5. **新增「一鍵 LINE 交辦幕僚」與「A4 決策簡報列印」**：
   - 在深藍色黃金 3 步英雄區新增「📤 LINE 傳給特助／財務代辦」按鈕（自動複製含 `?taxId=` 參數的交辦摘要並支援 LINE 分享）與「📄 匯出 A4 決策簡報 (PDF)」按鈕（觸發 `window.print()` 並附上 `@media print` 專用樣式）。
   - 網頁載入時自動解析網址 `?taxId=` 參數並帶入查詢。
```

