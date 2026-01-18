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

## 6.2 儲存 diagrams.md 並產生圖表

**預設渲染方式：** `LAYOUT_ENGINE = yoga_pywin32`

| 設定值 | 處理流程 | 載入方式 |
|--------|----------|----------|
| `yoga_pywin32`（預設）| pywin32 + mcp-yogalayout 渲染 | 直接執行下方流程 |
| `pptx_shapes` | python-pptx shapes API 繪製 | `Read {skill_dir}/phases/phase6-render-pptx-shapes.md` |
| `svg_png` | SVG 生成 → cairosvg 轉 PNG | `Read {skill_dir}/phases/phase6-render-svg.md` |

**⚠️ 注意：** 如果 `DIAGRAM_METHOD` 或 `LAYOUT_ENGINE` 不是 `yoga_pywin32`，請先讀取對應的附錄檔案再執行。

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

**layout.json 格式：**

```json
{
  "slide": { "w_pt": 960, "h_pt": 540 },
  "elements": [
    {
      "id": "title",
      "kind": "text",
      "role": "title",
      "bounding_box": { "x": 24, "y": 24, "w": 912, "h": 44 }
    },
    {
      "id": "fig:flow",
      "kind": "figure",
      "role": "body",
      "ratio": "16:9",
      "alt": "Pipeline 流程圖",
      "bounding_box": { "x": 24, "y": 300, "w": 400, "h": 200 }
    }
  ]
}
```

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

## 你的任務

1. 讀取參考模組並理解 API
2. 產生渲染程式碼
3. 執行程式碼產生 PPTX 檔案
4. 驗證圖表完整性和排版
5. 產生演講稿文字檔

## 輸入檔案

請讀取以下檔案作為輸入：

### 報告內容
- `./output/phase5/one_page.md`（包含所有技術細節）
- `./output/phase5/diagrams.md`
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

## ⚠️ 內容完整性要求（絕對禁止刪減）

### A) 主報告 one_page.md（最常漏）

- **必須把 `one_page.md` 完整內容渲染到投影片**
  - **使用 Yoga Layout 自動排版**：根據內容量自動計算最適字體大小
  - **字體大小約束**：
    - 標題：最小 14pt
    - 本文：最小 10pt
    - 小字註解/說明：最小 8pt
  - **若內容過多需分頁**：續頁也必須使用結構化元件呈現，**禁止純文字逐行顯示（文字牆）**
- **`#` 主標題必須來自 `one_page.md` 第 1 行**
- `[[Term]]`、`[C1]` 這類標記不得因清理文字而被刪掉

### B) 其他文件（同樣必須全收）

- **glossary.md 的每一個術語解釋都必須放入附錄**
- table.md：表格每一行每一列都必須完整呈現
- 不能因為版面不夠就省略內容；內容太多就縮小字（最小 8pt）或分多頁

### C) Windows 常見錯誤：pptx 被鎖住

- 若出現 `PermissionError`：代表 PowerPoint 正在開啟檔案
- 解法：先存成 `final_tmp.pptx`，或提示使用者先關閉 PowerPoint

## 渲染流程

1. 使用 `win32com.client.Dispatch("PowerPoint.Application")` 建立 PowerPoint
2. 設定投影片大小為 16:9（960x540 pt）
3. 使用 `modules_pywin32` 中的 draw_* 函數繪製圖表
4. 使用 `save(path, auto_close=True)` 儲存並自動關閉

## 輸出檔案

完成後，應該產生以下檔案：

| 檔案 | 說明 |
|------|------|
| `./output/final.pptx` | 最終 PPTX 檔案 |
| `./output/script.txt` | 演講稿文字檔 |

請開始執行。
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

**如果 Sub Agent 失敗**：
- 讀取 Sub Agent 的錯誤訊息
- 可能需要手動檢查 ./output 目錄的內容
- 必要時可以重新呼叫 Sub Agent

---

## 6.5 Checkpoint 驗證（強制；失敗即中止）

完成所有 Write 與執行後，必須用 Bash 工具驗證輸出檔案存在且非空：

```bash
python -c "from pathlib import Path; files=['output/diagrams.md','output/final.pptx','output/script.txt']; missing=[f for f in files if not Path(f).exists() or Path(f).stat().st_size==0]; print('missing_or_empty',missing); raise SystemExit(1 if missing else 0)"
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
