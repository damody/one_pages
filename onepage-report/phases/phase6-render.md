# Phase 6：渲染輸出

> **執行者：subagent**
> **輸入：** `./output/phase5/`（或 `./output/phase3/` 如審稿通過）
> **輸出：** `./output/one_page.pptx` + 其他檔案

---

## 6.0 入口檢查

**IF `RESUME_FROM` = 6：**
1. 從 `./output/phase5/` 讀取以下檔案作為輸入：
   - `one_page.md` → 主報告內容（包含所有技術細節）
   - `diagrams.md` → 圖表規格
   - `table.md` → 數據表
   - `glossary.md` → 術語詞彙表
   - `script.md` → 演講稿
   - `citation_map.md` → 來源對照表
2. 如果 `phase5/` 不存在，從 `phase3/` 讀取（表示審稿通過無需修改）
3. 使用讀取的檔案進行渲染

**ELSE（正常流程）：**
- 使用 Phase 5 產生的內容進行渲染

---

## 6.1 建立輸出目錄

```bash
python -c "from pathlib import Path; Path('output').mkdir(parents=True, exist_ok=True)"
```

---

## 6.1.4 圖表內容結構化（AI 預處理）

**目標**：將 `diagrams.md` 的自然語言描述轉換為結構化 JSON，讓後續渲染程式不需要解析自然語言。

**為什麼需要這一步？**
- `diagrams.md` 是自然語言描述（ASCII art、列表、自由格式文字）
- 不同專案的 diagrams.md 格式可能不同
- 硬編碼的正則式無法適應所有格式
- AI 可以理解任何格式的自然語言並提取結構化資訊

**輸入**：`./output/phase5/diagrams.md`
**輸出**：`./output/diagrams_structured.json`

### 結構化 JSON 標準格式

```json
{
  "diagrams": {
    "main:xxx": {
      "type": "before_after",
      "title": "圖表標題",
      "before": {
        "title": "改善前",
        "steps": ["步驟1", "步驟2", "步驟3"],
        "highlights": [
          {"text": "重點標注", "color": "red", "position": "步驟2"}
        ]
      },
      "after": {
        "title": "改善後",
        "steps": ["步驟1", "步驟2（改善）", "步驟3"],
        "highlights": [
          {"text": "改善效果", "color": "green", "position": "步驟2"}
        ]
      }
    },
    "appendix:1xxx": {
      "type": "flow",
      "title": "流程圖標題",
      "stages": [
        {
          "title": "階段1",
          "nodes": ["節點A", "節點B", "節點C"],
          "description": "階段說明"
        },
        {
          "title": "階段2",
          "nodes": ["節點D", "節點E"],
          "description": "階段說明"
        }
      ]
    },
    "appendix:2xxx": {
      "type": "platform_compare",
      "title": "平台對比標題",
      "platform1": {
        "name": "PC",
        "features": [
          {"text": "特性1", "status": "ok"},
          {"text": "特性2", "status": "warning"}
        ]
      },
      "platform2": {
        "name": "Android",
        "features": [
          {"text": "特性1", "status": "fail"},
          {"text": "特性2", "status": "ok"}
        ]
      }
    },
    "appendix:3xxx": {
      "type": "timeline",
      "title": "時間軸標題",
      "points": [
        {"time": "T0", "label": "事件1", "description": "說明"},
        {"time": "T1", "label": "事件2", "description": "說明"}
      ],
      "metrics": [
        {"name": "指標1", "target": ">=5%", "method": "量測方法"},
        {"name": "指標2", "target": "持平", "method": "量測方法"}
      ]
    },
    "appendix:4xxx": {
      "type": "comparison",
      "title": "對比標題",
      "left": {
        "name": "選項A",
        "features": ["特性1", "特性2", "特性3"],
        "pros": ["優點1"],
        "cons": ["缺點1"]
      },
      "right": {
        "name": "選項B",
        "features": ["特性1", "特性2", "特性3"],
        "pros": ["優點1"],
        "cons": ["缺點1"]
      }
    }
  }
}
```

### 執行 AI 預處理

讀取 `./output/phase5/diagrams.md`，然後產生結構化 JSON：

**AI Prompt 範本**：

```
請將以下 diagrams.md 內容轉換為結構化 JSON 格式。

## 輸入
{diagrams.md 內容}

## 輸出要求

根據每個圖表的類型，提取對應的結構化資料：

1. **before_after 類型**：提取 before/after 的步驟列表、重點標注
2. **flow 類型**：提取每個階段的標題和節點列表
3. **platform_compare 類型**：提取兩個平台的特性對比（ok/warning/fail 狀態）
4. **timeline 類型**：提取時間點和對應事件，以及量測指標
5. **comparison 類型**：提取左右對比的名稱、特性、優缺點

## 輸出格式

直接輸出 JSON，不要加 markdown code block：
{
  "diagrams": {
    "main:xxx": {...},
    "appendix:1xxx": {...}
  }
}
```

**使用 Write 工具儲存結果：**

```bash
# AI 產生的 JSON 直接用 Write 工具寫入
Write("./output/diagrams_structured.json", ai_generated_json)
```

**驗證結構化結果：**

```bash
python -c "
import json
from pathlib import Path

p = Path('output/diagrams_structured.json')
if not p.exists():
    raise SystemExit('diagrams_structured.json not found')

data = json.loads(p.read_text(encoding='utf-8'))
diagrams = data.get('diagrams', {})
print(f'結構化完成：{len(diagrams)} 個圖表')

for fig_id, content in diagrams.items():
    fig_type = content.get('type', 'unknown')
    print(f'  - {fig_id} ({fig_type})')
"
```

**下一步：** 在 6.1.5 執行 yoga_converter 時，使用 `--diagrams-structured ./output/diagrams_structured.json` 參數來使用此結構化資料。

---

## 6.1.5 內容合併（真正的 One Page）

**目標**：將 `one_page.md` 和 `diagrams.md` 合併成一個統一的 Markdown，讓 yogalayout 能夠一次性計算所有內容（文字 + 圖表）的佈局。

**為什麼需要合併？**
- yogalayout 只讀取單一 Markdown 檔案
- 分開的 `one_page.md` 和 `diagrams.md` 會導致附錄圖無法被納入佈局計算
- 合併後，yogalayout 能自動決定：一頁能塞多少內容、是否需要分頁、字體大小

**執行轉換：**

```bash
# 基本用法（從 diagrams.md 解析圖表內容）
python {skill_dir}/scripts/yoga_converter.py \
  --one-page ./output/phase5/one_page.md \
  --diagrams ./output/phase5/diagrams.md \
  --output ./output/one_page_yoga.md \
  --content-json ./output/content.json \
  --mode one_page

# 進階用法（使用 AI 預處理的結構化 JSON）
python {skill_dir}/scripts/yoga_converter.py \
  --one-page ./output/phase5/one_page.md \
  --diagrams ./output/phase5/diagrams.md \
  --output ./output/one_page_yoga.md \
  --content-json ./output/content.json \
  --mode one_page \
  --diagrams-structured ./output/diagrams_structured.json
```

**參數說明：**
- `--mode one_page`：盡量把所有內容（包括附錄圖）塞到一頁
- `--mode multi_page`：主內容一頁，附錄圖另外分頁
- `--diagrams-structured`：（可選）指定 AI 預處理過的結構化圖表 JSON。如果提供此參數，將直接使用 JSON 中的圖表內容，跳過從 diagrams.md 解析的步驟。這對於格式複雜或非標準的 diagrams.md 特別有用。

**驗證合併結果：**

```bash
python -c "
from pathlib import Path
p = Path('output/one_page_yoga.md')
if not p.exists():
    raise SystemExit('one_page_yoga.md not found')
content = p.read_text(encoding='utf-8')
fig_count = content.count('<fig ')
print(f'合併完成：找到 {fig_count} 個圖表標籤')
if fig_count == 0:
    print('警告：沒有找到圖表標籤，請檢查 diagrams.md')
"
```

**合併後的 Markdown 格式：**

```markdown
# 標題
> 副標題

## 已驗證的成功要素
- 項目 1
- 項目 2

<fig id="main:before_after" ratio="21:9" kind="diagram" alt="前後對比圖" />

## 現況與問題
- 問題 1
- 問題 2

<fig id="appendix:android_flow" ratio="21:9" kind="diagram" alt="Android 全鏈路" />

## 技術關鍵點
...

<fig id="appendix:platform_compare" ratio="21:9" kind="diagram" alt="PC vs Android" />
```

**⚠️ 重要**：後續的 yogalayout 呼叫要使用 `./output/one_page_yoga.md`，不是原始的 `one_page.md`。

---

## 6.2 儲存 diagrams.md 並產生圖表

**根據 `LAYOUT_ENGINE` 選擇渲染方式：**

| LAYOUT_ENGINE | 處理流程 | 載入方式 |
|---------------|----------|----------|
| `yoga_pywin32`（預設）| pywin32 + mcp-yogalayout 渲染 | 直接執行下方流程 |
| `pptx_shapes` | python-pptx shapes API 繪製 | `Read {skill_dir}/phases/phase6-render-pptx-shapes.md` |
| `svg_png` | SVG 生成 → cairosvg 轉 PNG | `Read {skill_dir}/phases/phase6-render-svg.md` |

**⚠️ 注意：** 如果 `LAYOUT_ENGINE` 不是 `yoga_pywin32`，請先讀取對應的附錄檔案再執行。

1. 將 diagrams.md 內容**使用 Write 工具**儲存到 `./output/diagrams.md`（即使內容為空也要寫出檔案）

2. （建議）在寫入後立刻做存在性驗證：

```bash
python -c "from pathlib import Path; p=Path('output/diagrams.md'); ok=p.exists() and p.stat().st_size>0; print('output_diagrams_ok',ok); raise SystemExit(0 if ok else 1)"
```

---

### 6.2.C Yoga Layout + pywin32（預設方式）

**執行前請讀取：** `{skill_dir}/reference/render_pywin32.py`

使用 mcp-yogalayout（Rust MCP Server）計算佈局，pywin32 COM API 渲染投影片。

**優點：**
- 自動化佈局計算（Yoga Flexbox 引擎）
- 支援原生 PowerPoint 效果（可編輯）
- 支援原生 Chart 物件（折線圖、長條圖、圓餅圖）
- 輸出完成後自動關閉 PowerPoint
- 未來可擴展 SmartArt 支援

**前置需求：**
- 安裝 pywin32：`pip install pywin32`
- 編譯 mcp-yogalayout：`cd D:\mcp-yogalayout && cargo build --release`

**流程：**
1. 將 one_page.md 轉換為 mcp-yogalayout 格式的 Markdown
2. 透過 MCP 協議呼叫 mcp-yogalayout 計算佈局
3. 讀取 layout.json
4. 使用 pywin32 根據座標渲染

**圖表類型對應：**

| 圖表類型 | 渲染方式 | 模組 |
|---------|---------|------|
| 折線圖 | pywin32 原生 Chart (AddChart2) | `draw_line_chart_pywin32.py` |
| 長條圖 | pywin32 原生 Chart | `draw_line_chart_pywin32.py` |
| 圓餅圖 | pywin32 原生 Chart | `draw_line_chart_pywin32.py` |
| 流程圖 | pywin32 Shapes | `draw_flow_pywin32.py` |
| 前後對比 | pywin32 Shapes | `draw_before_after_pywin32.py` |
| 時間軸 | pywin32 Shapes | `draw_timeline_pywin32.py` |
| 平台對比 | pywin32 Shapes | `draw_platform_compare_pywin32.py` |
| 架構圖 | pywin32 Shapes | `draw_architecture_pywin32.py` |
| 表格 | pywin32 Shapes | `_shapes_pywin32.py` |

**程式碼範例：**

```python
from render_pywin32 import LayoutRenderer

# 建立渲染器
renderer = LayoutRenderer()
renderer.create_presentation()

# 計算佈局（透過 MCP 協議）
layout = renderer.compute_layout_from_markdown(
    markdown_path="workspace/inputs/one_page_yoga.md",
    theme_path="workspace/themes/default.json"
)

# 渲染投影片
content_data = {
    "texts": {"title": "主標題"},
    "charts": {"fig:chart": {"categories": [...], "series": [...]}},
    "flows": {"fig:flow": [{"title": "步驟1"}, {"title": "步驟2"}]}
}
renderer.render_from_layout(layout, content_data)

# 儲存（auto_close=True 會自動關閉 PowerPoint）
renderer.save("./output/final.pptx", auto_close=True)
```

**layout.json 格式（多頁自動分配）：**

MCP yogalayout 會自動將內容分配到最少頁數的投影片中：

```json
{
  "slide_size": { "w_pt": 960, "h_pt": 540 },
  "total_pages": 2,
  "pages": [
    {
      "page_number": 1,
      "used_height_pt": 520,
      "remaining_height_pt": 20,
      "elements": [
        { "id": "title", "kind": "text", "role": "title", "box": { "x": 18, "y": 18, "w": 924, "h": 37 } },
        { "id": "section:成功要素:heading", "kind": "text", "role": "h2", "box": { "x": 18, "y": 70, "w": 924, "h": 24 } },
        { "id": "bullets:0", "kind": "bullets", "role": "body", "box": { "x": 18, "y": 100, "w": 924, "h": 100 } }
      ]
    },
    {
      "page_number": 2,
      "used_height_pt": 400,
      "remaining_height_pt": 140,
      "elements": [
        { "id": "section:平台對比:heading", "kind": "text", "role": "h2", "box": { "x": 18, "y": 18, "w": 924, "h": 24 } },
        { "id": "table:0", "kind": "table", "role": "body", "box": { "x": 18, "y": 50, "w": 924, "h": 200 } }
      ]
    }
  ]
}
```

**MCP 選項：**
- `auto_paginate: true`（預設）：自動將內容分配到多頁
- `density: "comfortable"` 或 `"compact"`：控制間距密度

**Markdown 轉換器：** 使用 `{skill_dir}/scripts/yoga_converter.py` 將 Phase 5 的 one_page.md 轉換為 mcp-yogalayout 格式：
- `#` 標題保持
- `>` 副標題/callout 保持
- `##` 區塊標題保持
- 圖表區塊轉換為 `<fig id="xxx" ratio="16:9" alt="描述" />`

---

## 6.2.D 分析圖表類型（產生動態載入清單）

**在呼叫 Sub Agent 之前，先解析 diagrams.md 確定需要哪些模組：**

| diagrams.md 中的關鍵字 | 需要載入的模組 |
|----------------------|---------------|
| `before_after`、`前後對比` | `draw_before_after_pywin32.py` |
| `flow`、`流程` | `draw_flow_pywin32.py` |
| `timeline`、`時間軸` | `draw_timeline_pywin32.py` |
| `platform_compare`、`平台對比` | `draw_platform_compare_pywin32.py` |
| `architecture`、`架構` | `draw_architecture_pywin32.py` |
| `line_chart`、`折線圖`、`長條圖`、`圓餅圖` | `draw_line_chart_pywin32.py` |

**必須載入的基礎模組（永遠需要）：**
- `render_pywin32.py`（主渲染器）
- `_shapes_pywin32.py`（基礎形狀函數）
- `_colors_pywin32.py`（顏色常數）

**範例：** 如果 diagrams.md 只有 `before_after` 和 `timeline` 類型：
- ✅ 載入：`render_pywin32.py`, `_shapes_pywin32.py`, `_colors_pywin32.py`, `draw_before_after_pywin32.py`, `draw_timeline_pywin32.py`
- ❌ 不載入：`draw_flow_pywin32.py`, `draw_platform_compare_pywin32.py`, `draw_architecture_pywin32.py`, `draw_line_chart_pywin32.py`

---

## 6.3 產生 PPTX（使用 Sub Agent）

**為什麼要用 Sub Agent？**
- render 程式碼通常有數百行，直接在主對話中產生會導致 context 爆掉
- 需要讀取多個檔案（one_page.md, diagrams.md, glossary.md, script.md 等）
- 可能需要多輪迭代修正
- 執行 Python 後的輸出也會佔用大量 context

**Sub Agent 的職責**：
1. 產生渲染程式碼
2. 執行渲染產生 PPTX
3. 驗證圖表完整性和排版
4. 多輪迭代修正直到通過驗證
5. 產生演講稿文字檔

---

### 6.3.1 Task 工具調用方式（pywin32 版本）

**步驟 1：分析 diagrams.md 中的圖表類型**

讀取 `./output/phase5/diagrams.md`，根據 6.2.D 的對應表確定需要的模組。

**步驟 2：產生動態模組清單**

根據分析結果，產生 `required_diagram_modules` 清單（只包含需要的圖表模組）。

**步驟 3：呼叫 Sub Agent**

```python
Task(
  description="產生 PPTX 和演講稿",
  subagent_type="general-purpose",
  prompt=f"""
你是 PPTX 渲染專家，負責使用 pywin32 將 Markdown 報告轉換為專業投影片。

---

## 🚨 步驟 0（強制）：呼叫 MCP 工具計算佈局

**⚠️ 在寫任何 Python 程式碼之前，你必須先完成以下動作：**

1. **呼叫 MCP 工具** `mcp__mcp-yogalayout__layout_compute_slide_layout`
   - 使用 `./output/one_page_yoga.md`（已合併文字+圖表的 Markdown）
   - 設定 `options.auto_paginate: true` 和 `options.density: "compact"`
   - 等待工具回傳 JSON 結果

2. **將 MCP 回傳的完整 JSON 貼出來**
   - 確認回應包含 `pages` 陣列（多頁模式）
   - 確認每個元素都有 `bounding_box`（x, y, w, h）
   - **特別確認 `<fig>` 標籤都有對應的 `kind: figure` 元素**

3. **確認所有預期元素都有座標後，才能繼續**

**🚫 如果你跳過此步驟直接寫程式碼，你的輸出將被拒絕並要求重做。**

---

## 🚨 步驟 1（強制）：圖表完整性清點

讀取 `./output/one_page_yoga.md` 和 `./output/content.json`，列出所有圖表：

| # | 圖表 ID | 圖表類型 | ratio | 在 MCP layout 中的位置 |
|---|---------|---------|-------|----------------------|
| 1 | main:xxx | before_after | 21:9 | page 1, box (x,y,w,h) |
| 2 | appendix:xxx | flow | 21:9 | page 1, box (x,y,w,h) |
| ... | ... | ... | ... | ... |

**🚫 如果有任何圖表在 MCP layout 中找不到對應的 `figure` 元素，你的輸出將被拒絕。**
**🚫 所有圖表都必須渲染，不得遺漏。**

---

## 🚨 步驟 2（強制）：內容完整性確認

讀取 `./output/one_page_yoga.md`，確認：

1. 計算 `<fig>` 標籤數量（應該等於 content.json 中的 total_diagrams）
2. 確認所有章節標題（## 開頭）都會出現在 PPTX 中
3. MCP yogalayout 會自動分頁：
   - 所有內容都會被渲染（禁止刪減）
   - MCP 自動計算最佳分頁位置
   - **目標是盡量塞進一頁（真正的 One Page）**
   - **絕對禁止簡化或摘要內容**

---

## 你的任務（必須按順序執行）

1. ✅ 完成步驟 0：呼叫 MCP 工具並貼出結果
2. ✅ 完成步驟 1：列出所有圖表並確認渲染計畫
3. ✅ 完成步驟 2：確認內容完整性
4. 讀取參考模組並理解 API
5. 使用 MCP 回傳的座標產生渲染程式碼
6. 執行程式碼產生 PPTX 檔案
7. 驗證圖表完整性和排版
8. 產生演講稿文字檔

---

## 輸入檔案

請讀取以下檔案作為輸入：

### 合併後的報告（優先使用）
- `./output/one_page_yoga.md`（已合併文字+圖表，供 MCP yogalayout 使用）
- `./output/content.json`（圖表資訊，包含 diagrams_info 和 total_diagrams）

### 原始報告內容（參考用）
- `./output/phase5/one_page.md`（原始報告）
- `./output/phase5/diagrams.md`（原始圖表規格，供渲染時參考詳細內容）
- `./output/phase5/glossary.md`
- `./output/phase5/script.md`
- `./output/phase5/table.md`（如有）

### 全域設定
- `./output/phase1/config.md`

### 參考資料（根據圖表類型動態產生）

**基礎模組（必須載入）：**
- `{{skill_dir}}/reference/render_pywin32.py`（主渲染器）
- `{{skill_dir}}/reference/modules_pywin32/_shapes_pywin32.py`（基礎形狀）
- `{{skill_dir}}/reference/modules_pywin32/_colors_pywin32.py`（顏色常數）

**圖表模組（根據 6.2.D 分析結果載入）：**
{{required_diagram_modules}}

⚠️ 只載入上述列出的模組，不要載入其他未列出的 draw_*.py 檔案。

---

## ⚠️ 內容完整性要求（絕對禁止刪減）

### A) 主報告 one_page.md

- **必須把 `one_page.md` 完整內容渲染到投影片**
  - 所有 `##` 區塊都必須出現
  - 所有條列項目都必須保留
  - `[[Term]]`、`[C1]` 等標記不得刪除
- **字體大小約束**：
  - 標題：最小 14pt
  - 本文：最小 10pt
  - 小字註解：最小 8pt
- **若內容過多**：分頁呈現，禁止刪減

### B) diagrams.md 的每個圖表

- **每個圖表都必須渲染**，沒有例外
- 圖表類型對應：before_after、platform_compare、timeline、architecture 等
- 主圖放在主報告頁，附錄圖放在獨立頁面

### C) glossary.md 的每個術語

- 所有術語解釋都必須放入術語附錄頁

---

## 📐 排版樣式規範

### D) 文字區塊必須有背景色

**每個章節區塊（標題 + 內容）都必須用顏色方塊包起來：**

```python
# ❌ 錯誤：直接放文字
add_textbox(slide, "標題", x, y, w, h, ...)
add_textbox(slide, "內容", x, y2, w, h2, ...)

# ✅ 正確：先畫背景方塊，再放文字
add_rounded_rect(slide, x, y, w, total_h, line_color=ACCENT_COLOR, fill_color=BG_COLOR)
add_textbox(slide, "標題", x+pad, y+pad, w-2*pad, title_h, ...)
add_textbox(slide, "內容", x+pad, y+title_h, w-2*pad, content_h, ...)
```

**建議的顏色配對：**
| 區塊類型 | 邊框色 (line_color) | 背景色 (fill_color) |
|---------|---------------------|---------------------|
| 成功/正面 | ACCENT_GREEN | #E8F5E9 |
| 問題/警告 | ACCENT_ORANGE | #FFF8E1 |
| 技術/中性 | ACCENT_BLUE | #E3F2FD |
| 行動/重要 | ACCENT_RED | #FFEBEE |
| 引擎/補充 | ACCENT_PURPLE | #F3E5F5 |

### E) 充分利用投影片空間

**空間利用優先級：**
1. 第一頁應盡量容納所有核心內容
2. 如果有空白區域，應該放入更多內容（縮小字體、調整間距）
3. 不允許「第一頁有明顯空白」但「核心內容被拆到第二頁」

**第一頁最小內容：**
- 標題 + 副標題
- 成功要素
- 問題分析
- 技術關鍵點
- Before/After 對比圖
- 預期效益
- 行動建議（至少摘要）

**投影片可用空間：**
- 標題區：y = 8-50 (約 42pt)
- 內容區：y = 50-510 (約 460pt)
- 頁碼區：y = 510-540 (約 30pt)

### F) 區塊間距規範

- 區塊之間：8-12pt 間距
- 區塊內 padding：6-8pt
- 內容密集時可縮減到 4-6pt

### G) 第一頁版面配置參考

**左右雙欄佈局（960x540pt 投影片）：**

```
+------------------------------------------------------------------+
| 標題（y=8, h=24）                                                  |
| 副標題（y=32, h=14）                                               |
+--------------------------------+-----------------------------------+
| 左欄 (x=11, w=450)             | 右欄 (x=475, w=476)               |
|                                |                                   |
| [成功要素] y=50, h=80          | [Before/After 圖]                 |
| [問題分析] y=135, h=70         |   y=50, h=260                     |
| [技術要點] y=210, h=80         |                                   |
| [預期效益] y=295, h=60         +-----------------------------------+
| [行動建議] y=360, h=60         | [關鍵數據摘要]                     |
| [風險] y=425, h=40             |   y=320, h=50                     |
|                                | [引擎差異/補充]                    |
|                                |   y=380, h=80                     |
+--------------------------------+-----------------------------------+
| 頁碼 (y=520)                                                       |
+------------------------------------------------------------------+
```

**如果空間仍不足：**
- 縮小字體（最小 7pt）
- 減少行距（1.0 而非 1.2）
- 合併相似區塊
- 最後才考慮拆頁

---

## 渲染流程

1. **呼叫 MCP 工具計算佈局**（步驟 0 已完成）
   - MCP 會自動分頁，回傳 `pages` 陣列
   - 每頁包含該頁的 `elements` 和座標
2. **遍歷每一頁**：
   - 為每個 `page` 建立一張投影片
   - 使用該頁的 `elements` 座標定位元素
3. 使用 `win32com.client.Dispatch("PowerPoint.Application")` 建立 PowerPoint
4. 設定投影片大小為 16:9（960x540 pt）
5. 使用 MCP 座標定位所有元素（禁止硬編碼）
6. 使用 `modules_pywin32` 中的 draw_* 函數繪製圖表
7. 儲存並關閉

**多頁處理範例：**
```python
layout = json.load(open("layout.json"))
for page in layout["pages"]:
    slide = prs.Slides.Add(page["page_number"], ppLayoutBlank)
    for elem in page["elements"]:
        render_element(slide, elem)
```

---

## 輸出檔案

| 檔案 | 說明 |
|------|------|
| `./output/final.pptx` | 最終 PPTX 檔案 |
| `./output/script.txt` | 演講稿文字檔 |

---

**請從步驟 0 開始執行：呼叫 MCP 工具 `mcp__mcp-yogalayout__compute_slide_layout`**
"""
)
```

---

## 6.4 驗證輸出檔案

Sub Agent 完成後，檢查以下檔案是否存在：

| 檔案 | 說明 |
|------|------|
| `./output/final.pptx` | ⭐ 最終 PPTX 檔案 |
| `./output/script.txt` | 演講稿文字檔 |
| `./output/render_final.py` | 渲染程式碼（用於驗證） |

**如果 Sub Agent 失敗**：
- 讀取 Sub Agent 的錯誤訊息
- 可能需要手動檢查 ./output 目錄的內容
- 必要時可以重新呼叫 Sub Agent

---

## 6.4.1 內容完整性驗證（主 Agent 必做）

**Sub Agent 完成後，主 Agent 必須驗證輸出內容的完整性：**

### A) 驗證 MCP 呼叫

檢查 Sub Agent 是否有呼叫 MCP 工具：
- Sub Agent 的輸出中應該有 `mcp__mcp-yogalayout__compute_slide_layout` 的呼叫記錄
- 如果沒有 → **重新呼叫 Sub Agent，強調必須先執行步驟 0**

### B) 驗證圖表完整性

讀取 `./output/content.json`，取得預期的圖表清單：

```bash
python -c "
import json
from pathlib import Path

# 讀取 content.json
content = json.loads(Path('output/content.json').read_text(encoding='utf-8'))
expected = content.get('diagrams_info', [])
total = content.get('total_diagrams', len(expected))
print(f'預期圖表數量：{total}')
for d in expected:
    print(f'  - {d[\"id\"]} ({d[\"kind\"]})')

# 讀取 render_final.py 檢查實際渲染
render_code = Path('output/render_final.py').read_text(encoding='utf-8')
missing = []
for d in expected:
    fig_id = d['id']
    if fig_id not in render_code:
        missing.append(fig_id)

if missing:
    print(f'⚠️ 遺漏的圖表：{missing}')
    raise SystemExit(1)
else:
    print('✅ 所有圖表都有對應的渲染程式碼')
"
```

如果有遺漏 → **重新呼叫 Sub Agent，提供遺漏清單**

### C) 驗證內容完整性

比較 `./output/phase5/one_page.md` 和 `render_final.py` 的 CONTENT 變數：
- one_page.md 的所有 `##` 標題都必須出現
- 如果內容被簡化或摘要 → **重新呼叫 Sub Agent，強調禁止刪減**

### D) 驗證排版樣式

檢查 `./output/render_final.py` 確認：
- **背景色**：每個章節區塊都有 `add_rounded_rect` 或 `add_rect` 作為背景
- **空間利用**：第一頁的 y 座標使用範圍應接近 50-510（不應有大片空白）
- **第一頁內容**：至少包含成功要素、問題、技術、效益、行動建議

如果排版不符合規範：
- 列出具體問題（如「左側文字區塊沒有背景色」）
- 重新呼叫 Sub Agent，提供排版修正指示

### E) 驗證失敗的處理

如果上述任一驗證失敗：

```python
Task(
  description="修正渲染問題",
  subagent_type="general-purpose",
  prompt=f"""
你之前的輸出有以下問題：

{具體列出遺漏的項目}

請修正以下問題：
1. ...
2. ...

**必須從步驟 0 重新開始：呼叫 MCP 工具**
"""
)
```

---

## 6.5 Checkpoint 驗證（強制；失敗即中止）

完成所有 Write 與執行後，必須用 Bash 工具驗證輸出檔案存在且非空：

```bash
python -c "
from pathlib import Path

# 必須存在的檔案
required = [
    'output/one_page_yoga.md',   # 合併後的 Markdown
    'output/content.json',        # 圖表資訊
    'output/diagrams.md',         # 圖表規格（複製）
    'output/final.pptx',          # 最終輸出
    'output/script.txt'           # 演講稿
]

missing = [f for f in required if not Path(f).exists() or Path(f).stat().st_size==0]
print('missing_or_empty', missing)
raise SystemExit(1 if missing else 0)
"
```

若驗證失敗，代表輸出未落盤或被鎖住，必須停止流程並修正。

---

## 6.6 完成

告知使用者：

```
✅ 報告產生完成！

輸出檔案：
📊 ./output/final.pptx（投影片，含主報告 + 技術附錄 + 術語解釋）
📝 ./output/script.txt（演講稿獨立檔案）
📚 ./output/citation_map.md（來源對照表）
📖 ./output/glossary.md（術語詞彙表）

投影片結構：
- 第 1 頁：主報告（含術語上標標記）
- 第 2 頁：附錄 - 術語解釋（適合非技術背景讀者）

建議：
1. 開啟 PPTX 確認排版
2. 簡報時可開啟「簡報者檢視畫面」查看備註欄的演講稿
3. 如需調整，可以直接編輯 PPTX
4. 如被問「這數字哪來的？」，可查閱 citation_map.md
5. 如聽眾對術語有疑問，可切到附錄頁說明
```
