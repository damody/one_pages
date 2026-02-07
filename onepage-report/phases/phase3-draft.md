# Phase 3：產生初稿（v2 - 兩階段平行設計）

> **執行者：主 agent 協調多個 subagent**
> **輸入：** `./output/phase2/`（素材、citation map、術語清單）
> **輸出：** `./output/phase3/`

---

## 3.0 架構概述（v2 改進）

```
Phase 3 v2 流程（預估 3.5 分鐘，vs 原本 5.5 分鐘）：
┌──────────────────────────────────────────────────────────────┐
│ 階段 1：產生核心報告                                          │
│ ┌────────────────────────────────────────────────────────┐   │
│ │ Subagent A (Haiku): one_page.md                        │   │
│ │ 輸入：materials.md, citation_map.md, terms.md          │   │
│ │ ⏱️ ~2 分鐘                                              │   │
│ └────────────────────────────────────────────────────────┘   │
│                         ↓                                    │
│ 階段 2：平行產生 4 個衍生檔案（同時啟動）                       │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌──────────┐ │
│ │ Subagent B  │ │ Subagent C  │ │ Subagent D  │ │Subagent E│ │
│ │ diagrams.md │ │ table.md    │ │ glossary.md │ │script.md │ │
│ │ ⏱️ ~1.5 min │ │ ⏱️ ~0.5 min │ │ ⏱️ ~1 min   │ │⏱️ ~1 min │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └──────────┘ │
│      ↑               ↑               ↑              ↑        │
│      └───────────────┴───────────────┴──────────────┘        │
│                 都讀取 one_page.md 作為輸入                    │
│                 ⏱️ 總計 ~1.5 分鐘（取最慢的）                   │
└──────────────────────────────────────────────────────────────┘
```

**核心改變**：
- ✅ 階段 2 的 4 個 subagent 平行執行
- ✅ 總時間從 5.5 分鐘減少到 ~3.5 分鐘
- ✅ 主 agent 在同一訊息中發起多個 Task

---

## 3.0.1 入口檢查

**IF `RESUME_FROM` > 3：**
1. 從 `./output/phase3/` 讀取 checkpoint，跳過本 Phase
2. 直接進入 Phase 4

**ELSE：** 正常執行下方流程

---

## 產出文件清單

| 文件 | 說明 | 階段 | 格式規範 |
|------|------|------|----------|
| `one_page.md` | 主報告內容 | 階段 1 | `{skill_dir}/templates/one-page-format.md` |
| `diagrams.md` | 圖表規格 | 階段 2 | `{skill_dir}/templates/diagrams-spec.md` |
| `table.md` | 數據比較表格 | 階段 2 | 見 3.4 節 |
| `glossary.md` | 術語詞彙表 | 階段 2 | `{skill_dir}/templates/glossary-format.md` |
| `script.md` | 演講稿 | 階段 2 | `{skill_dir}/templates/script-format.md` |

---

## 階段 1：產生 one_page.md

### 3.1.1 呼叫 Subagent A

```python
Task(
  description="Phase 3A：產生核心報告",
  subagent_type="general-purpose",
  model="haiku",
  prompt=f"""
請產生 one_page.md（主報告內容）。

## 規範
Read {skill_dir}/templates/one-page-format.md

## 輸入素材
{materials_content}

## Citation Map
{citation_map_content}

## 術語清單
{terms_content}

## 核心原則

1. **國中生能懂標準**：所有內容必須讓沒有技術背景的人也能理解
2. **內容完整性優先**：保留所有技術細節，不刪減任何素材內容
3. **數字要具體**：不要「大幅改善」，要「改善 81%」
4. **邏輯鏈完整**：已驗證 → 現況問題 → 為何可行 → POC 設計 → 成功判定
5. **Citation 保留**：所有論述都必須保留 [C1], [C2] 等標記
6. **術語標記**：專業術語加 [[術語]] 標記

## 輸出
請直接輸出完整的 one_page.md 內容（不需要寫入檔案，主 agent 會處理）。
"""
)
```

### 3.1.2 主 agent 寫入結果

```python
Write("./output/phase3/one_page.md", subagent_a_output)
```

---

## 階段 2：平行產生 4 個衍生檔案

### 3.2.1 主 agent 讀取 one_page.md

```
Read ./output/phase3/one_page.md
```

### 3.2.2 同時呼叫 4 個 Subagent

**⚠️ 重要：在同一個訊息中發起所有 4 個 Task，Claude Code 會平行執行**

```python
# 同時發起 4 個 Task（平行執行）
Task(
  description="Phase 3B：產生 diagrams.md",
  subagent_type="general-purpose",
  model="haiku",
  prompt=f"""
請根據 one_page.md 產生 diagrams.md（圖表規格）。

## 規範
Read {skill_dir}/templates/diagrams-spec.md

## 重要限制
- **不要讀取** diagrams-spec-types.md（該檔案是 Phase 6 渲染器參考，與你無關）
- **不要寫尺寸**：所有尺寸由 yoga_converter 自動計算，不需要指定像素
- **不要寫顏色/箭頭樣式**：視覺細節由 Phase 6 渲染器自動決定

## 主報告內容
{one_page_content}

## 素材參考
{materials_content}

## 輸出
請直接輸出完整的 diagrams.md 內容。
"""
)

Task(
  description="Phase 3C：產生 table.md",
  subagent_type="general-purpose",
  model="haiku",
  prompt=f"""
請根據 one_page.md 產生 table.md（數據比較表格）。

## 主報告內容
{one_page_content}

## 素材參考
{materials_content}

## 輸出格式
| Metric | Baseline | Experimental | Delta | 說明 |
|--------|----------|--------------|-------|------|

如果沒有數據比較，輸出：
# 無數據表
本報告不含數據比較表格。
"""
)

Task(
  description="Phase 3D：產生 glossary.md",
  subagent_type="general-purpose",
  model="haiku",
  prompt=f"""
請根據 one_page.md 產生 glossary.md（術語詞彙表）。

## 規範
Read {skill_dir}/templates/glossary-format.md

## 主報告內容
{one_page_content}

## Citation Map 補充說明（優先使用）
{citation_map_content}

## 術語清單
{terms_content}

## 核心原則
用**國中生能懂**的方式解釋每個術語。

## 輸出
請直接輸出完整的 glossary.md 內容。
"""
)

Task(
  description="Phase 3E：產生 script.md",
  subagent_type="general-purpose",
  model="haiku",
  prompt=f"""
請根據 one_page.md 產生 script.md（演講稿）。

## 規範
Read {skill_dir}/templates/script-format.md

## 主報告內容
{one_page_content}

## 核心原則
金字塔式邏輯承接 - 一句承接一句，邏輯不斷鏈。
每段標註要看投影片的哪個區塊。

## 輸出
請直接輸出完整的 script.md 內容。
"""
)
```

### 3.2.3 主 agent 收集結果並寫入

等待所有 4 個 subagent 完成後：

```python
Write("./output/phase3/diagrams.md", subagent_b_output)
Write("./output/phase3/table.md", subagent_c_output)
Write("./output/phase3/glossary.md", subagent_d_output)
Write("./output/phase3/script.md", subagent_e_output)
```

---

## 3.3 驗證

Write 工具會回報寫入結果。如果所有 Write 成功（無錯誤回傳），直接進入下一個 Phase，不需要額外的 Bash 驗證。

---

## 附錄 A：內容規範摘要

### one_page.md 核心原則

1. **國中生能懂標準**：所有內容必須讓沒有技術背景的人也能理解
2. **內容完整性優先**：保留所有技術細節，不刪減任何素材內容
3. **數字要具體**：不要「大幅改善」，要「改善 81%」
4. **邏輯鏈完整**：已驗證 → 現況問題 → 為何可行 → POC 設計 → 成功判定
5. **內容密度極大化**：盡可能把所有細節塞進一頁，由 Phase 6 的 Yoga Layout 自動處理排版

### Citation 保留規則

所有論述都必須保留 Citation ID：
```markdown
- Android 觸控事件處理採用非同步機制，導致輸入延遲 [C6]
```

### 術語標記

在 one_page.md 中，用 `[[術語]]` 標記需要解釋的術語：
```markdown
- 降低跨 [[cluster]] 的 [[migration]]，可減少 [[L2 cache]] miss
```

---

## 附錄 B：圖表識別規則

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

## 附錄 C：與 v1 的差異

| 項目 | v1（原設計） | v2（新設計） |
|------|-------------|-------------|
| 執行方式 | 1 個 subagent 序列產生 5 個檔案 | 階段 1: 1 個, 階段 2: 4 個平行 |
| 預估時間 | 5.5 分鐘 | 3.5 分鐘 |
| Subagent 數量 | 1 個 | 5 個（但 4 個平行） |
| 階段 2 依賴 | N/A | 都讀取 one_page.md |
