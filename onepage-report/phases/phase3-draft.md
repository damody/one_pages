# Phase 3：產生初稿

> **執行者：subagent**
> **輸入：** `./output/phase2/`（素材、citation map、術語清單）
> **輸出：** `./output/phase3/`

---

## 3.0 入口檢查

**IF `RESUME_FROM` > 3：**
1. 從 `./output/phase3/` 讀取 checkpoint，跳過本 Phase
2. 直接進入 Phase 4

**ELSE：** 正常執行下方流程

---

## 產出文件清單

| 文件 | 說明 | 格式規範 |
|------|------|----------|
| `one_page.md` | 主報告內容（包含所有技術細節）| `Read {skill_dir}/templates/one-page-format.md` |
| `diagrams.md` | 圖表規格 | `Read {skill_dir}/templates/diagrams-spec.md` |
| `table.md` | 數據比較表格（如有）| 見 3.4 節 |
| `glossary.md` | 術語詞彙表 | `Read {skill_dir}/templates/glossary-format.md` |
| `script.md` | 演講稿 | `Read {skill_dir}/templates/script-format.md` |

---

## 3.1 產生 one_page.md

**執行前請讀取：** `{skill_dir}/templates/one-page-format.md`

### 核心原則

1. **國中生能懂標準**：所有內容必須讓沒有技術背景的人也能理解
2. **內容完整性優先**：保留所有技術細節，不刪減任何素材內容
3. **數字要具體**：不要「大幅改善」，要「改善 81%」
4. **邏輯鏈完整**：已驗證 → 現況問題 → 為何可行 → POC 設計 → 成功判定
5. **內容密度極大化**：盡可能把所有細節塞進一頁，由 Phase 6 的 Yoga Layout 自動處理排版

### 內容處理策略

- **所有技術細節都放 one_page.md**：執行緒名稱、函數列表、程式碼片段等全部保留
- **不做內容分流**：Phase 6 會使用 Yoga Layout 自動計算字體大小，確保內容放得下
- **無字數限制**：不再限制 <=120 字等，寫多少就是多少
- **術語標記**：專業術語加 `[[術語]]` 標記，連結到 glossary.md 的解釋

### Citation 保留規則

所有論述都必須保留 Citation ID：
```markdown
- Android 觸控事件處理採用非同步機制，導致輸入延遲 [C6]
```

---

## 3.2 圖表內容識別

掃描素材識別可視覺化的內容：

| 內容類型 | 識別關鍵詞 | 圖表類型 |
|----------|-----------|---------|
| 改善對比 | 改善、優化、Before/After、降低、提升 | `before_after` |
| 平台對比 | PC、手機、Android、平台差異 | `platform_compare` |
| 流程步驟 | 步驟、流程、pipeline、→ | `flow` |
| 時間序列 | 延遲、latency、時序 | `timeline` |

### 強制圖表要求

| 位置 | 必須圖表 | 類型 |
|------|----------|------|
| 主投影片 | 前後比較圖 | `before_after` |
| 附錄 | 系統架構圖 | `architecture` |
| 附錄 | 流程/平台比較圖 | 視內容而定 |

---

## 3.3 產生 diagrams.md

**執行前請讀取：** `{skill_dir}/templates/diagrams-spec.md`

根據 3.2 識別的內容，產生多張圖表規格。

---

## 3.4 產生 table.md（如有數據比較時）

**產生條件：**
- 素材有 Before/After 數據
- 有多方案指標比較
- 設定 E1/E2 需要實驗數據

**格式：**
```markdown
## 指標比較表

| Metric | Baseline | Experimental | Delta | 說明 |
|--------|----------|--------------|-------|------|
| FPS_avg | 60 fps | 66 fps | +10% | 平均幀率提升 |
```

---

## 3.5 產生 glossary.md

**執行前請讀取：** `{skill_dir}/templates/glossary-format.md`

掃描 one_page.md 中的專業術語，用**國中生能懂**的方式產生術語解釋。

**優先使用 Citation Map 補充說明**（Phase 2.8 已整理）。

---

## 3.6 產生 script.md

**執行前請讀取：** `{skill_dir}/templates/script-format.md`

演講稿，每段標註要看投影片的哪個區塊。

**核心原則：金字塔式邏輯承接** - 一句承接一句，邏輯不斷鏈。

---

## 3.7 術語標記

在 one_page.md 中，用 `[[術語]]` 標記需要解釋的術語：

```markdown
- 降低跨 [[cluster]] 的 [[migration]]，可減少 [[L2 cache]] miss
```

這些標記會在 Phase 6 渲染時轉換為連結。

---

## 3.8 Checkpoint 寫入

1. 建立目錄：
   ```bash
   python -c "from pathlib import Path; Path('output/phase3').mkdir(parents=True, exist_ok=True)"
   ```

2. 使用 Write 工具寫入：
   - `./output/phase3/one_page.md`
   - `./output/phase3/diagrams.md`
   - `./output/phase3/table.md`（如無則寫「# 無數據表」）
   - `./output/phase3/glossary.md`
   - `./output/phase3/script.md`

3. 驗證（必須）：
   ```bash
   python -c "from pathlib import Path; files=['output/phase3/one_page.md','output/phase3/diagrams.md','output/phase3/table.md','output/phase3/glossary.md','output/phase3/script.md']; missing=[f for f in files if not Path(f).exists() or Path(f).stat().st_size==0]; print('missing_or_empty',missing); raise SystemExit(1 if missing else 0)"
   ```
