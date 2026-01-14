# Phase 3：產生初稿

根據素材內容與使用者設定，產生三到四份文件。

## 產出文件清單

| 文件 | 說明 | 格式規範 |
|------|------|----------|
| `one_page.md` | 主報告內容 | `Read {skill_dir}/templates/one-page-format.md` |
| `diagrams.md` | 圖表規格與生成指示 | `Read {skill_dir}/templates/diagrams-spec.md` |
| `table.md` | 數據比較表格（如有）| 見下方說明 |
| `glossary.md` | 術語詞彙表 | `Read {skill_dir}/templates/glossary-format.md` |
| `script.md` | 演講稿 | `Read {skill_dir}/templates/script-format.md` |

---

## 3.1 產生 one_page.md

**執行前請讀取：** `{skill_dir}/templates/one-page-format.md`

根據素材提取並整理內容，使用統一的完整格式。

**核心原則：**
- 內容密度要足夠讓主管做決策
- 每個 bullet 都要有實質內容
- 數字要具體（不要「大幅改善」，要「改善 81%」）
- 要有「已驗證」→「現況問題」→「為何可行」→「POC 設計」→「成功判定」的邏輯鏈
- 所有內容必須讓國中生能看懂

---

## 3.2 圖表內容識別

在產生圖表前，先掃描素材識別**所有**可視覺化的內容。

### 識別規則

| 內容類型 | 識別關鍵詞 | 圖表類型 |
|----------|-----------|---------|
| 改善對比 | 改善、優化、問題→解決、Before/After、降低、提升、消除 | `before_after` |
| 平台對比 | PC、手機、Android、iOS、平台、差異、對照表、vs | `platform_compare` |
| 流程步驟 | 步驟、流程、鏈路、pipeline、→、然後、接著、管線 | `flow` |
| 時間序列 | 延遲、latency、時序、從...到...、全鏈路、Input-to-Display | `timeline` |

### 強制圖表要求（必須產生）

| 位置 | 必須圖表 | 類型 | 說明 |
|------|----------|------|------|
| **主投影片** | 前後比較圖 | `before_after` | 必須有！展示改善前 vs 改善後的差異 |
| **附錄** | 系統架構圖 | `architecture` | 必須有！展示整體系統/技術架構 |
| **附錄** | 流程比較圖 | `platform_compare` | 如有參考 PC/其他平台/方法，必須有！ |

---

## 3.3 產生 diagrams.md

**執行前請讀取：** `{skill_dir}/templates/diagrams-spec.md`

根據 3.2 識別的內容，產生**多張圖表**。

---

## 3.4 產生 table.md（如有數據比較時）

當素材中包含數據比較時產生表格。

### 判斷是否需要表格

- 素材中有 Before/After 數據
- 素材中有多個方案的指標比較
- 素材中有時間序列的變化數據
- 使用者設定 E1/E2（需要實驗數據）

### table.md 格式

```markdown
## 指標比較表

| Metric | Baseline | Experimental | Delta | 說明 |
|--------|----------|--------------|-------|------|
| FPS_avg | 60 fps | 66 fps | +10% | 平均幀率提升 |
| FPS_1%low | 45 fps | 52 fps | +16% | 最低幀更穩定 |
| Power | 900 mW | 820 mW | -9% | 功耗降低 |
| Jank | 15 次 | 3 次 | -80% | 掉幀大幅減少 |

**測試條件**：
- 裝置：Dimensity 9300
- 場景：原神璃月港
- 時長：120 秒
```

### 表格設計原則

- 欄位數量：4-6 欄（太多會擠）
- 行數：3-8 行（太多考慮分組）
- Delta 欄：自動計算，顯示百分比或差值
- 重要數據可用粗體標示

---

## 3.5 產生 glossary.md

**執行前請讀取：** `{skill_dir}/templates/glossary-format.md`

掃描 one_page.md 中的專業術語，用**國中生能懂**的方式產生術語解釋。

**優先使用 Citation Map 補充說明：**
- Phase 2.8 已對每個 Citation 進行 web search 並整理了術語解釋
- 產生 glossary.md 時，優先從 Citation Map 的「補充說明 > 術語解釋」取用

---

## 3.6 產生 script.md

**執行前請讀取：** `{skill_dir}/templates/script-format.md`

演講稿，每段標註要看投影片的哪個區塊。

**核心原則：金字塔式邏輯承接**
- 一句承接一句
- 邏輯不斷鏈
- 結論是總結

---

## 3.7 術語標記

在 one_page.md 中，用 `[[術語]]` 標記需要解釋的術語：

```markdown
## 技術關鍵點
- 降低跨 [[cluster]] 的 [[migration]]，可減少 [[L2 cache]] miss
- 預估可改善 [[1% Low FPS]] 達 15%
```

這些標記會在 Phase 6 渲染時轉換為超連結。
