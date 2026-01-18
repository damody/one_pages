# Phase 5 附錄：內容恢復流程

> **載入條件：** 當 Phase 4 發現 `missing_technical_detail` 或 `unused_citation` Issue 時載入此檔案
>
> **v4.1 簡化：** 所有內容都恢復到 one_page.md（固定為 TECHNICAL 模式）

---

## 適用 Issue 類型

| Issue 類型 | 說明 | 恢復目標 |
|-----------|------|---------|
| `missing_technical_detail` | 技術實體（執行緒、函數、表格）遺失 | 從 materials.md 恢復到 one_page.md |
| `unused_citation` | Citation 未使用 | 從 materials.md 恢復到 one_page.md |

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

### 步驟 2：內容整合到 one_page.md

**恢復格式**：

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

---

### 步驟 3：篇幅處理

v4.1 使用 Yoga Layout 自動處理排版：
- **無篇幅限制**：所有內容都放 one_page.md
- **自動字體縮放**：Yoga 會根據內容量自動計算字體大小
- **最小字體約束**：本文 10pt、小字 8pt

---

### 步驟 4：保留 Citation 追溯性

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
