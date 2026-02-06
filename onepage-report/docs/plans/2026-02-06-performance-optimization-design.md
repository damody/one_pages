# onepage-report 效能優化設計

> 日期：2026-02-06
> 目標：減少執行時間 60%、消除 context compact

## 問題分析

### 當前效能瓶頸

| Phase | Token 消耗 | 時間 | 主要問題 |
|-------|-----------|------|----------|
| Phase 2 | 58k | 9.5 min | Citation WebSearch 序列執行 |
| Phase 3 | 81k | 5.5 min | 5 個檔案序列產生 |
| Phase 4-5 | ~47k | ~4 min | 每輪 2 個 subagent，檔案重複讀取 |
| Phase 6 | 98k | 6.75 min | 讀取 8 個 Python 模組 (2500 行) x2 |

### 根本原因

1. **Phase 6 模組重複讀取**：主 agent 和 subagent 都讀取相同的 Python 模組
2. **缺乏平行化**：Phase 2/3 的獨立任務序列執行
3. **審稿迴圈效率低**：每輪審稿+重寫分成 2 個 subagent

---

## 新架構設計

### Phase 2：主 agent + 平行 WebSearch

```
階段 1：主 agent 直接處理（不用 subagent）
  - 讀取素材檔案（Glob + Read）
  - 整理成 materials.md
  - 建立初步 Citation Map（C1-C10）
  - 掃描術語清單

階段 2：平行 WebSearch（多個 subagent）
  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
  │ Subagent A  │ │ Subagent B  │ │ Subagent C  │
  │ C1-C3 搜尋  │ │ C4-C6 搜尋  │ │ C7-C10 搜尋 │
  └─────────────┘ └─────────────┘ └─────────────┘

階段 3：主 agent 合併結果
```

預估：9.5 min → 3.5 min

### Phase 3：兩階段平行

```
階段 1：產生核心報告
  Subagent A (Haiku): one_page.md

階段 2：平行產生 4 個衍生檔案（同時啟動）
  Subagent B: diagrams.md
  Subagent C: table.md
  Subagent D: glossary.md
  Subagent E: script.md
```

預估：5.5 min → 3.5 min

### Phase 4-5：合併審稿+重寫

```
當前：每輪 2 個 subagent（審稿 → 重寫）
新設計：每輪 1 個 subagent（審稿+重寫合併）

Subagent 輸出格式：
### ISSUES
（問題清單，或 "PASS"）

### ONE_PAGE.MD
（修正後內容，或 "NO_CHANGE"）

### DIAGRAMS.MD
（修正後內容，或 "NO_CHANGE"）

### TABLE.MD
（修正後內容，或 "NO_CHANGE"）
```

預估：每輪 context -50%

### Phase 6：JSON 模板設計（最大改動）

#### 核心概念：分離「資料產生」與「渲染邏輯」

```
當前流程（98k tokens）：
  Subagent 讀取 8 個 Python 模組 (2500 行)
      ↓
  Subagent 產生 render_final.py (300-500 行)
      ↓
  執行 Python 產生 PPTX

新流程（預估 15-20k tokens）：
  主 agent 呼叫 MCP yogalayout（取得座標）
      ↓
  Subagent 只需產生 slide_data.json（純資料）
      ↓
  固定 Python 渲染器讀取 JSON → PPTX
```

#### slide_data.json Schema

```json
{
  "metadata": {
    "title": "報告標題",
    "subtitle": "副標題",
    "total_pages": 2
  },
  "pages": [
    {
      "page": 1,
      "elements": [
        {
          "id": "title",
          "kind": "text",
          "content": "標題內容"
        },
        {
          "id": "section:xxx",
          "kind": "section",
          "title": "章節標題",
          "bullets": ["項目1", "項目2"]
        },
        {
          "id": "fig:main:xxx",
          "kind": "figure",
          "type": "before_after",
          "data": {
            "before": {"title": "改善前", "steps": [...]},
            "after": {"title": "改善後", "steps": [...]}
          }
        }
      ]
    }
  ]
}
```

#### 支援的圖表類型

| type | data 結構 |
|------|----------|
| `before_after` | `{before: {title, steps}, after: {title, steps}}` |
| `flow` | `{stages: [{title, nodes}]}` |
| `timeline` | `{points: [{time, label, duration}]}` |
| `platform_compare` | `{platforms: [{name, items: [{text, status}]}]}` |
| `architecture` | `{layers: [{name, components}]}` |

#### 新的 Phase 6 執行流程

```
主 Agent 執行：
1. 執行 yoga_converter.py 合併內容
   輸出：one_page_yoga.md, content.json

2. 呼叫 MCP yogalayout
   輸入：one_page_yoga.md
   輸出：layout.json（含所有元素座標）

3. 呼叫 Subagent（輕量，不讀 Python 模組）
   輸入：content.json + JSON Schema
   輸出：slide_data.json

4. 執行固定渲染器
   python render_from_json.py \
     --layout layout.json \
     --data slide_data.json \
     --output final.pptx
```

---

## 預估改善

| 指標 | 當前 | 新設計 | 改善 |
|------|------|--------|------|
| **總時間** | 44 分鐘 | 15-18 分鐘 | **-60%** |
| **Compact 次數** | 2 次 | 0 次 | **-100%** |
| **Phase 2 時間** | 9.5 min | 3.5 min | -63% |
| **Phase 3 時間** | 5.5 min | 3.5 min | -36% |
| **Phase 6 tokens** | 98k | ~20k | **-80%** |

---

## 實作計畫

### 需要修改的檔案

| 檔案 | 動作 | 說明 |
|------|------|------|
| `SKILL.md` | 修改 | 更新流程說明 |
| `phases/phase2-input.md` | 修改 | 主 agent 讀取 + 平行 WebSearch |
| `phases/phase3-draft.md` | 修改 | 兩階段平行設計 |
| `phases/phase4-review.md` | 修改 | 合併審稿+重寫 |
| `phases/phase5-revise.md` | 刪除 | 合併到 phase4-review.md |
| `phases/phase6-render.md` | 大改 | JSON 模板設計 |
| `templates/slide-data-schema.json` | 新增 | JSON Schema 定義 |
| `scripts/render_from_json.py` | 新增 | 固定渲染器 |

### 實作優先順序

```
Phase 1：Phase 6 重構（影響最大）
├── 1.1 設計 slide_data.json schema
├── 1.2 開發 render_from_json.py（整合現有 draw_*.py）
├── 1.3 修改 phase6-render.md
└── 1.4 測試：確認 JSON → PPTX 正常

Phase 2：Phase 3 平行化
├── 2.1 修改 phase3-draft.md（兩階段設計）
├── 2.2 測試：確認 4 個 subagent 平行執行
└── 2.3 驗證輸出品質

Phase 3：Phase 4-5 合併
├── 3.1 合併 phase4 + phase5 為單一檔案
├── 3.2 更新 prompt 結構
└── 3.3 測試審稿迴圈

Phase 4：Phase 2 平行化
├── 4.1 修改 phase2-input.md
├── 4.2 測試平行 WebSearch
└── 4.3 端到端測試

Phase 5：整合測試
├── 5.1 完整流程測試
├── 5.2 測量時間和 context 消耗
└── 5.3 微調
```
