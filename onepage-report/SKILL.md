---
name: onepage-report
description: 從素材資料夾產生一頁投影片 + 演講稿
arguments: [input_path]
---

# 一頁投影片產生器

> 版本：v5.0（性能優化 - 平行 subagent + JSON 模板設計）

將素材（資料夾/PPTX/URL）轉換成專業的一頁投影片與演講稿。

## 架構說明

**主 agent 負責調控與 I/O**，subagent 專注於分析與生成：
- Phase 2：主 agent 讀取素材 + 平行 subagent WebSearch
- Phase 3：兩階段平行（one_page.md 先，4 個衍生檔案平行）
- Phase 4-5（審稿迴圈）：合併為單一 subagent（審稿+重寫）
- Phase 6：JSON 模板設計（subagent 不讀 Python 模組）
- 每個 Phase 完成後輸出到 `./output/phase{N}/`
- 支援從任意 Phase 繼續執行

**v5.0 性能優化：**
- Phase 2：主 agent 直接讀取 + 3 個平行 WebSearch subagent（9.5min → 4-5min）
- Phase 3：兩階段平行設計（5.5min → 3.5min）
- Phase 4-5：審稿+重寫合併，每輪 1 個 subagent（原本 2 個）
- Phase 6：JSON 模板設計，subagent context 減少 97%（98k → 15-20k tokens）
- 預估總時間：44min → ~15-20min

---

## 執行流程概述（v5.0）

| Phase | 說明 | 執行者 | 模型 | 規範檔案 | 預估時間 |
|-------|------|--------|------|----------|----------|
| 1 | 設定詢問 | **主 agent** | - | `{skill_dir}/phases/phase1-setup.md` | 1 min |
| 2 | 讀取素材 | **主 agent + 3 平行 subagent** | Haiku | `{skill_dir}/phases/phase2-input.md` | 4-5 min |
| 3 | 產生初稿 | **1+4 平行 subagent** | Haiku | `{skill_dir}/phases/phase3-draft.md` | 3.5 min |
| 4-5 | 審稿+重寫 | **主 agent + 合併 subagent** | Sonnet | `{skill_dir}/phases/phase4-review.md` | 3 min |
| 6 | 渲染輸出 | **主 agent + 輕量 subagent** | Haiku | `{skill_dir}/phases/phase6-render.md` | 2 min |

### 模型選擇策略

| 模型 | 速度 | 適用場景 |
|------|------|---------|
| **Haiku** | 快 5-6 倍 | Phase 3（格式化輸出）、Phase 6（結構化處理） |
| **Sonnet** | 標準 | Phase 2（理解文檔）、Phase 4-5（深度推理、審稿） |

**為何 Phase 3/6 用 Haiku：**
- 任務性質：主要是格式化和擴寫，不需要複雜推理
- 有明確範本：規範檔案已提供詳細格式要求
- 可驗證性：Phase 4 會進行審稿，即使有小錯也能修正

---

## 全域變數

| 變數 | 說明 | 預設值 |
|------|------|--------|
| `PURPOSE` | 報告目的 | - |
| `EVIDENCE` | 佐證強度 | E0 |
| `MAX_ITERATIONS` | 審稿輪數 | 5 |
| `LAYOUT_ENGINE` | 渲染引擎 | yoga_pywin32 |
| `LAYOUT_REVIEW_ROUNDS` | 排版審查輪數 | 2 |
| `REVIEW_WEB_SEARCH` | 審稿時是否啟用網路查證 | false |
| `CITATION_WEB_SEARCH` | Citation Map 是否啟用網路補充 | false |
| `RESUME_FROM` | 從哪個 Phase 繼續（1-6） | 1 |

### 渲染引擎選項

| LAYOUT_ENGINE | 說明 | 適用情境 |
|---------------|------|---------|
| `yoga_pywin32` | Yoga Layout + pywin32，自動排版 | Windows，推薦 |
| `pptx_shapes` | python-pptx Shapes API | 跨平台 |
| `svg_png` | SVG 生成轉 PNG | 精細圖表，不可編輯 |

### Yoga Layout 字體約束

| 元素類型 | 最小字體 |
|---------|---------|
| 標題 | 14pt |
| 本文 | 10pt |
| 小字註解 | 8pt |

---

## Phase 1：設定詢問（主 agent 執行）

**執行前請讀取：** `Read {skill_dir}/phases/phase1-setup.md`

主 agent 直接執行，使用 AskUserQuestion 工具詢問使用者設定。

---

## Phase 2-6：Subagent 執行

**每個 Phase 都使用 Task tool 呼叫 subagent**，prompt 格式如下：

```
請執行 Phase {N}：{Phase 說明}

**規範檔案：** 請讀取 {skill_dir}/phases/phase{N}-xxx.md

**輸入資料：** 請讀取 ./output/phase{N-1}/ 目錄下的所有檔案

**輸出位置：** ./output/phase{N}/

請嚴格按照規範執行，完成後將結果寫入輸出目錄。
```

---

## Phase 2：讀取素材（v2 平行設計）

**執行流程：** 詳見 `{skill_dir}/phases/phase2-input.md`

**v2 改進：主 agent 直接讀取 + 平行 WebSearch**
- 階段 1：主 agent 直接讀取素材（不用 subagent）
- 階段 2：3 個平行 subagent 執行 WebSearch（若 `CITATION_WEB_SEARCH = true`）
- 階段 3：主 agent 合併結果

**階段 1：主 agent 讀取**
```
Read {input_path}/**/*.txt
Read {input_path}/**/*.md
執行 extract_pptx.py / extract_pdf.py（如有）
建立初步 citation_map.md + terms.md
Write ./output/phase2/materials.md
Write ./output/phase2/citation_map.md
Write ./output/phase2/terms.md
```

**階段 2：平行 WebSearch（若啟用）**
```python
# 同時發起 3 個 Task（平行執行）
Task(description="Phase 2A：WebSearch C1-C3", ...)
Task(description="Phase 2B：WebSearch C4-C6", ...)
Task(description="Phase 2C：WebSearch C7+", ...)
```

**階段 3：合併結果**
```
解析 subagent 回傳的 JSON
更新 citation_map.md 加入補充說明
```

---

## Phase 3：產生初稿（v2 兩階段平行）

**執行流程：** 詳見 `{skill_dir}/phases/phase3-draft.md`

**v2 改進：兩階段平行設計**
- 階段 1：Subagent A 產生 one_page.md（核心報告）
- 階段 2：4 個 subagent 平行產生衍生檔案
- 總時間從 5.5 分鐘減少到 ~3.5 分鐘

**階段 1：產生核心報告**
```python
Task(
  description="Phase 3A：產生核心報告",
  model="haiku",
  prompt="讀取 materials.md, citation_map.md, terms.md，產生 one_page.md"
)
Write("./output/phase3/one_page.md", subagent_a_output)
```

**階段 2：平行產生 4 個衍生檔案**
```python
# 在同一訊息中發起 4 個 Task（平行執行）
Task(description="Phase 3B：產生 diagrams.md", ...)
Task(description="Phase 3C：產生 table.md", ...)
Task(description="Phase 3D：產生 glossary.md", ...)
Task(description="Phase 3E：產生 script.md", ...)

# 等待完成後寫入
Write("./output/phase3/diagrams.md", ...)
Write("./output/phase3/table.md", ...)
Write("./output/phase3/glossary.md", ...)
Write("./output/phase3/script.md", ...)
```

---

## Phase 4-5：審稿+重寫（v2 合併設計）

**執行流程：** 詳見 `{skill_dir}/phases/phase4-review.md`

**v2 改進：審稿+重寫合併為單一 subagent**
- 每輪 1 個 subagent（vs 原本 2 個）
- 3 輪總計 3 個 subagent（vs 原本 6 個）
- Context 減少 ~50%（檔案只讀 1 次）

**步驟 1：主 agent 讀取檔案**
```
IF 第 1 輪：
    Read ./output/phase3/one_page.md
    Read ./output/phase3/diagrams.md
    Read ./output/phase3/table.md
ELSE：
    Read ./output/phase5/one_page.md
    Read ./output/phase5/diagrams.md
    Read ./output/phase5/table.md
```

**步驟 2：主 agent 呼叫合併 subagent**
- 將讀取的內容嵌入 prompt
- Subagent **不使用任何工具**
- Subagent 同時回傳：
  - ISSUES（問題清單，或 "PASS"）
  - 修正後的 ONE_PAGE.MD、DIAGRAMS.MD、TABLE.MD（或 "NO_CHANGE"）

**步驟 3：主 agent 解析並寫入結果**
```
Write ./output/phase4/issues.md
IF one_page != "NO_CHANGE": Write ./output/phase5/one_page.md
IF diagrams != "NO_CHANGE": Write ./output/phase5/diagrams.md
IF table != "NO_CHANGE": Write ./output/phase5/table.md
```

### 多輪迭代

```
WHILE 迭代計數 <= MAX_ITERATIONS:
    呼叫合併 subagent（審稿+重寫）
    IF ISSUES == "PASS": BREAK
    IF 達到上限: 執行強制保守輸出
```

---

## Phase 6：渲染輸出（v2 - JSON 模板設計）

**執行流程：** 詳見 `{skill_dir}/phases/phase6-render.md`

**v2 改進（減少 80% context）**：
- ✅ Subagent 不再讀取 Python 模組
- ✅ Subagent 只產生 `slide_data.json`（結構化資料）
- ✅ 固定渲染器 `render_from_json.py` 處理 PPTX 產生
- ✅ MCP 呼叫移到主 agent（避免 subagent prompt 過大）

**主 agent 執行步驟**：
1. 執行 `yoga_converter.py` 合併內容 → `one_page_yoga.md`, `content.json`
2. 呼叫 MCP yogalayout 取得座標 → `layout.json`
3. 呼叫輕量 subagent 產生 `slide_data.json`（讀取 `{skill_dir}/templates/phase6-subagent-prompt.md`）
4. 執行 `render_from_json.py` 產生 PPTX

**Subagent 呼叫**：
```python
Task(
  description="Phase 6：產生 slide_data.json",
  subagent_type="general-purpose",
  model="haiku",  # 輕量任務用 Haiku
  prompt=f"""
{phase6_subagent_prompt}  # 從 templates/phase6-subagent-prompt.md 讀取

## 輸入
{one_page_yoga_content}
{content_json}

請產生 slide_data.json。
"""
)
```

**預估 token**：15-20k（vs 原本 98k）

---

## 輸出檔案

```
./output/
├── phase1/                      # Phase 1 checkpoint
│   └── config.md
├── phase2/                      # Phase 2 checkpoint
│   ├── materials.md
│   ├── citation_map.md
│   └── terms.md
├── phase3/                      # Phase 3 checkpoint
│   ├── one_page.md              # 包含所有技術細節
│   ├── diagrams.md
│   ├── table.md
│   ├── glossary.md              # bypass: 直接傳到 Phase 6
│   └── script.md                # bypass: 直接傳到 Phase 6
├── phase4/                      # Phase 4 checkpoint
│   └── issues.md                # 審稿結果（最多 3 個問題）
├── phase5/                      # Phase 5 checkpoint（審稿迴圈只處理 3 個文件）
│   ├── one_page.md              # 包含所有技術細節
│   ├── diagrams.md
│   └── table.md
├── iterations/                  # 多輪迭代版本保留
│   ├── iter1/phase4/, phase5/
│   └── iter2/phase4/, phase5/
├── final.pptx                   # 最終輸出：主投影片
├── script.txt                   # 演講稿
└── glossary.md                  # 術語詞彙表
```

**Bypass 文件說明：**
- `script.md` 和 `glossary.md` 從 Phase 3 直接傳到 Phase 6，不進入審稿迴圈
- Phase 4-5 只處理 `one_page.md`、`diagrams.md`、`table.md` 三個文件
- 優化效果：減少 I/O 量，加速審稿迴圈執行

---

## 錯誤處理

**執行前請讀取：** `Read {skill_dir}/reference/error-handling.md`

---

## 檔案結構（v5.0）

```
onepage-report/
├── SKILL.md                     # 本檔案（主入口）
├── phases/                      # 執行階段規範
│   ├── phase1-setup.md
│   ├── phase2-input.md          # v2: 平行 WebSearch 設計
│   ├── phase3-draft.md          # v2: 兩階段平行設計
│   ├── phase4-review.md         # v2: 審稿+重寫合併
│   ├── phase5-revise.md         # 已整合到 phase4-review.md
│   ├── phase6-render.md         # v2: JSON 模板設計
│   ├── phase6-render-pptx-shapes.md  # 備選渲染方式
│   ├── phase6-render-svg.md     # 備選渲染方式
│   └── appendix/                # 附錄檔案（按需載入）
│       ├── phase4-checklist-detail.md
│       └── phase5-content-recovery.md
├── templates/                   # 輸出模板與格式規範
│   ├── one-page-format.md
│   ├── diagrams-spec.md
│   ├── glossary-format.md
│   ├── script-format.md
│   ├── slide-data-schema.json   # v2: JSON Schema 定義
│   ├── slide-data-example.json  # v2: 範例資料
│   ├── phase6-subagent-prompt.md # v2: 輕量 subagent prompt（102 行）
│   ├── experiment-plan.md
│   └── appendix/
│       └── diagrams-spec-types.md
├── reference/                   # 技術參考文件
│   ├── render_pywin32.py        # pywin32 渲染器
│   ├── modules_pywin32/         # pywin32 圖表模組
│   ├── svg-generation.md
│   ├── pptx-shapes.md
│   └── error-handling.md
└── scripts/                     # Python 腳本
    ├── extract_pptx.py
    ├── extract_pdf.py
    ├── pptx_reference.py
    ├── yoga_converter.py        # Markdown 轉 Yoga 格式
    └── render_from_json.py      # v2: 固定 JSON 渲染器（轉換 JSON → PPTX）
```

---

## 核心原則提醒

1. **國中生能懂標準**：所有內容必須讓沒有技術背景的人也能理解
2. **內容完整性**：絕對禁止刪減內容，由 Yoga Layout 自動處理排版
3. **Sub Agent 審稿**：每輪審稿必須使用獨立的 Sub Agent
4. **完整輸出**：每輪重寫都要輸出完整的 Markdown 文件
5. **Citation 追溯**：所有論述都要能追溯到素材來源
6. **Yoga 自動排版**：內容量不限制，Phase 6 自動計算字體大小（最小 10pt，小字 8pt）
