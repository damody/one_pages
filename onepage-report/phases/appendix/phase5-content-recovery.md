# Phase 5 附錄：內容恢復流程

> **載入條件：** 當 Phase 4 發現 `missing_technical_detail` 或 `unused_citation` Issue 時載入此檔案

---

## 適用 Issue 類型

| Issue 類型 | 說明 | 恢復目標 |
|-----------|------|---------|
| `missing_technical_detail` | 技術實體（執行緒、函數、表格）遺失 | 從 materials.md 恢復到 technical_appendix.md 或 one_page.md |
| `unused_citation` | Citation 未使用 | 檢查 Citation 內容，決定恢復到哪個檔案 |

---

## 恢復步驟

### 步驟 1：定位原始素材

從 Issue 中提取 Citation ID，然後從 materials.md 讀取對應內容。

**範例**：
```
Issue: "Q10：Android 完整流程的執行緒名稱遺失 [C6]"
→ 提取 Citation ID: C6
→ 從 ./output/phase2/materials.md 讀取 [C6] 區塊的內容
→ 從 ./output/phase2/citation_map.md 讀取 [C6] 的補充說明（如有）
```

---

### 步驟 2：判斷恢復目標位置

根據 DETAIL_LEVEL 和 Issue 類型，決定將內容恢復到哪個檔案：

| DETAIL_LEVEL | Issue 類型 | 恢復位置 |
|--------------|-----------|---------|
| BALANCED | missing_technical_detail | technical_appendix.md |
| BALANCED | unused_citation（技術細節）| technical_appendix.md |
| BALANCED | unused_citation（核心證據）| one_page.md + technical_appendix.md |
| TECHNICAL | missing_technical_detail | one_page.md（主報告包含所有細節）|
| TECHNICAL | unused_citation | one_page.md |
| EXECUTIVE | missing_technical_detail | technical_appendix.md |
| EXECUTIVE | unused_citation | technical_appendix.md（主報告極簡）|

**如何區分「技術細節」與「核心證據」**：
- **核心證據**：直接支持標題結論的數字、測試結果、效能改善數據
- **技術細節**：實作機制、執行緒列表、函數呼叫鏈、引擎差異分析

---

### 步驟 3：內容整合

**恢復到 technical_appendix.md 的格式**：

```markdown
## {主題名稱} [{Citation ID}]

{從 materials.md [{Citation ID}] 抽取的完整內容}

### 執行緒列表
1. **{執行緒名稱}**：{說明}
   - 執行位置：{程序名稱}
   - 優先級：{優先級}

2. **{執行緒名稱}**：{說明}
   ...

### 函數呼叫鏈
```
{函數名稱1}()
  → {函數名稱2}()
    → {函數名稱3}()
```

### 技術總結表
| 階段 | 執行緒 | 函數 | 同步機制 | 耗時 |
|------|--------|------|---------|------|
| {階段1} | {執行緒} | {函數} | {機制} | {時間} |
| ... | ... | ... | ... | ... |

（來源：materials.md [{Citation ID}]）
```

**恢復到 one_page.md 的格式**：

```markdown
## 證據

### {證據點標題}

{簡化摘要}。在 Android Touch2Photon 流程中，觸控事件經過以下執行緒處理：InputReader → InputDispatcher → ViewRootImpl → RenderThread。詳細的函數呼叫鏈和時序分析見技術附錄頁 2。[C6]

（如 DETAIL_LEVEL = TECHNICAL，則直接展開完整內容，不使用「詳見附錄」）
```

---

### 步驟 4：篇幅控制

**one_page.md 篇幅限制**：
- 如果恢復內容後超過篇幅（約 1500-2000 字），將詳細流程移到 technical_appendix.md
- 主報告保留摘要 + 引用附錄頁碼：「詳見技術附錄頁 X」

**technical_appendix.md 篇幅建議**：
- 單一主題章節不超過 1 頁（約 500-700 字 + 1-2 個表格/圖）
- 如內容過多，拆分為多個子章節

---

### 步驟 5：保留 Citation 追溯性

**關鍵原則**：
- ✓ 所有恢復的內容都必須標註 Citation ID
- ✓ 保留原始 materials.md 的引用來源
- ✗ 禁止憑空生成不在 materials.md 中的技術細節
- ✗ 禁止修改原始數字或結論
- ✗ 禁止將不同 Citation 混合而無法追溯

**範例**：

```markdown
✓ 正確：
## Android Touch2Photon 完整流程 [C6]
InputReader 執行緒負責讀取觸控事件，優先級為 Real-time。[C6]

✗ 錯誤：
## Android Touch2Photon 完整流程
InputReader 執行緒負責讀取觸控事件（優先級為 -8，這是標準配置）。
（問題：優先級 -8 不在 materials.md [C6] 中，是憑空生成的）
```

---

## 多個 Citation 同時遺失的處理

當 Issue 指出多個 Citation 未使用（例如 [C11][C12]）：

1. **檢查內容相關性**：這些 Citation 是否描述同一主題？
2. **合併或分開**：
   - 同一主題（如 C11、C12 都是引擎差異分析）→ 合併為一個章節
   - 不同主題 → 分開為不同章節
3. **保留所有 Citation ID**：
   ```markdown
   ## Unity vs Unreal 引擎差異分析 [C11][C12]

   Unity 採用 Double Buffering 架構... [C11]

   Unreal 採用 Pipelined 架構... [C12]
   ```

---

## 內容恢復的驗證

恢復內容後，必須檢查：

| 檢查項目 | 驗證方法 |
|---------|---------|
| 完整性 | Issue 提到的所有技術實體（執行緒/函數/表格）都已恢復？|
| 追溯性 | 每段恢復的內容都有 Citation ID？|
| 一致性 | 恢復的內容與 materials.md 原文一致？沒有憑空生成？|
| 位置正確 | 根據 DETAIL_LEVEL 恢復到正確檔案（one_page.md 或 technical_appendix.md）？|
| 引用連結 | one_page.md 有「詳見技術附錄頁 X」的引用？|
