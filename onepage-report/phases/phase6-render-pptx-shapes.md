# Phase 6 附錄：PPTX Shapes 渲染方式（python-pptx）

> **使用條件：** 當 `LAYOUT_ENGINE = pptx_shapes` 時載入此檔案
> **執行前請讀取：** `{skill_dir}/reference/pptx-shapes.md`

---

## PPTX Shapes 方式說明

使用 python-pptx 內建的 shapes API 直接在投影片上繪製圖表。

**優點：**
- 產生的圖表可直接在 PowerPoint 中編輯
- 不需要 cairosvg 依賴
- 避免 emoji 無法渲染的問題

**前置需求：**
- 安裝 python-pptx：`pip install python-pptx`

---

## 產生 render_this.py 程式碼（Sub Agent 內部執行）

**步驟 1：讀取參考資料**

執行前必須讀取以下檔案：

```
Read {skill_dir}/scripts/pptx_reference.py    # API 參考
Read {skill_dir}/reference/pptx-shapes.md     # 圖表繪製函數規範
Read {skill_dir}/reference/render_example.py  # ⭐⭐ 最重要：完整的 draw 函數實作範例
Read {skill_dir}/test_shapes_full.py          # 完整佈局範例
```

⚠️ **最重要**：`render_example.py` 是經過驗證的完整範例，包含：

**圖表繪製函數（必須複製完整實作）：**
- `draw_before_after_with_vertical_flow()` - 詳細版前後對比圖，帶有垂直內部流程節點
- `draw_flow()` - 橫向流程圖，支援節點標題、說明、時間標籤
- `draw_architecture()` - 分層架構圖，支援高亮層級和元件
- `draw_platform_compare()` - 上下平台對比圖，支援內部項目和總結
- `draw_glossary_card()` / `draw_glossary_page()` - 術語卡片（4x4 格局）

**輔助函數：**
- `add_background()` - 加入米色背景
- `add_main_title()` - 加入主標題和副標題
- `add_content_box()` - 加入圓角矩形內容方塊
- `add_section_title()` - 加入區塊標題
- `add_table()` - 加入表格
- `set_cell_text()` - 設定表格儲存格文字

**排版審查函數：**
- `reset_element_tracker()` / `set_current_slide()` / `track_element()` - 元素追蹤
- `check_overlaps()` / `layout_review()` - 重疊檢測

**請優先從 render_example.py 複製 draw 函數的完整實作**，確保圖表繪製正確。

---

**步驟 2：根據 one_page.md 內容產生程式碼**

使用 **Write 工具**產生 `./output/render_this.py`，程式碼結構如下：

```python
# -*- coding: utf-8 -*-
"""
由 onepage-report skill 自動產生
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# 顏色定義（MTK 風格）
BG_COLOR = RGBColor(255, 249, 230)
WHITE = RGBColor(255, 255, 255)
DARK_GRAY = RGBColor(51, 51, 51)
ACCENT_BLUE = RGBColor(70, 130, 180)
ACCENT_ORANGE = RGBColor(230, 126, 34)
ACCENT_GREEN = RGBColor(39, 174, 96)
ACCENT_PURPLE = RGBColor(142, 68, 173)
ACCENT_RED = RGBColor(192, 0, 0)

# ===== 輔助函數（從 pptx_reference.py 複製完整函數） =====
def set_cell_text(cell, text, font_size=10, bold=True, color=DARK_GRAY):
    cell.text = text
    for paragraph in cell.text_frame.paragraphs:
        paragraph.font.size = Pt(font_size)
        paragraph.font.bold = bold
        paragraph.font.color.rgb = color
        paragraph.font.name = "Microsoft JhengHei"

def add_content_box(slide, left, top, width, height, title, content_lines, title_color=ACCENT_BLUE):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = WHITE
    shape.line.color.rgb = RGBColor(220, 220, 220)
    shape.line.width = Pt(1)

    title_box = slide.shapes.add_textbox(left + Inches(0.08), top + Inches(0.03), width - Inches(0.16), Inches(0.3))
    tf = title_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = title_color
    p.font.name = "Microsoft JhengHei"

    content_box = slide.shapes.add_textbox(left + Inches(0.08), top + Inches(0.28), width - Inches(0.16), height - Inches(0.32))
    tf = content_box.text_frame
    tf.word_wrap = True
    for i, line in enumerate(content_lines):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = line
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = DARK_GRAY
        p.font.name = "Microsoft JhengHei"
        p.space_after = Pt(1)

# ===== 圖表繪製函數（從 test_shapes_full.py 複製完整函數） =====

# 圖表顏色
COLOR_RED = RGBColor(244, 67, 54)       # 改善前/問題
COLOR_GREEN = RGBColor(76, 175, 80)     # 改善後/成功
COLOR_BLUE = RGBColor(33, 150, 243)     # 流程/節點
COLOR_ORANGE = RGBColor(255, 152, 0)    # 警告/風險
COLOR_PURPLE = RGBColor(156, 39, 176)   # 硬體/底層
COLOR_GRAY_BG = RGBColor(245, 245, 245) # 區塊背景
COLOR_ACCENT = RGBColor(0, 121, 107)    # 強調色 Teal

def draw_before_after(slide, left, top, width, height, before_title, before_items, after_title, after_items):
    """繪製前後對比圖 - 從 test_shapes_full.py 複製完整實作"""
    # ... 複製 test_shapes_full.py 中的完整函數 ...
    pass

def draw_flow(slide, left, top, width, height, nodes):
    """繪製橫向流程圖 - 從 test_shapes_full.py 複製完整實作"""
    # ... 複製 test_shapes_full.py 中的完整函數 ...
    pass

def draw_architecture(slide, left, top, width, height, layers):
    """繪製分層架構圖 - 從 test_shapes_full.py 複製完整實作"""
    # ... 複製 test_shapes_full.py 中的完整函數 ...
    pass

# ===== 主函數 =====
def create_pptx():
    # 1. 建立簡報
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # 2. 加入空白投影片
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # 3. 加入背景
    background = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    background.fill.solid()
    background.fill.fore_color.rgb = BG_COLOR
    background.line.fill.background()

    # 4. 根據 one_page.md 產生內容
    # 5. 根據 diagrams.md 繪製圖表
    # 6. 儲存
    prs.save('one_page.pptx')
    print("已生成：one_page.pptx")

if __name__ == "__main__":
    create_pptx()
```

---

**步驟 3：內容對應規則**

| one_page.md 區塊 | render_this.py 對應 |
|------------------|---------------------|
| `# 主標題` | `add_textbox()` 標題區，字體 Pt(26) |
| `> 副標題引言` | `add_textbox()` 副標題區，字體 Pt(11) |
| `## 區塊標題` + 內容 | `add_content_box()` 圓角矩形區塊 |
| 表格 | `add_table()` |
| `[[術語]]` 標記 | 使用 `parse_text_with_terms()` 加入超連結 |

---

**步驟 4：區塊顏色分配**

根據區塊語意選擇顏色：

| 區塊類型 | 顏色變數 |
|----------|----------|
| 技術背景、成功判定 | ACCENT_BLUE |
| 問題、POC 設計 | ACCENT_ORANGE |
| 效益、解決方案 | ACCENT_GREEN |
| 架構、技術細節 | ACCENT_PURPLE |
| 行動、決策 | ACCENT_RED |

---

**步驟 5：解析 diagrams.md 並產生繪圖呼叫**

diagrams.md 格式範例（pptx_shapes 模式）：

```markdown
## 主圖表

- **類型**：before_after
- **位置**：left=0.3, top=2.5, width=6.0, height=2.5

### Shapes 參數

```json
{
  "before_title": "改善前",
  "before_items": ["問題1", "問題2"],
  "after_title": "改善後",
  "after_items": ["解決1", "解決2"]
}
```
```

對應產生的 Python 程式碼：

```python
draw_before_after(
    slide=slide,
    left=0.3, top=2.5, width=6.0, height=2.5,
    before_title="改善前",
    before_items=["問題1", "問題2"],
    after_title="改善後",
    after_items=["解決1", "解決2"]
)
```

**圖表類型對應函數：**

| diagrams.md 類型 | 呼叫函數 | 用途 |
|------------------|----------|------|
| `before_after`（簡單版） | `draw_before_after()` | 前後對比圖（項目列表） |
| `before_after`（有內部流程） | `draw_before_after_with_flow()` | 前後對比圖（內部流程節點） |
| `flow`（簡單版） | `draw_flow()` | 橫向流程圖 |
| `flow`（詳細版） | `draw_flow_detailed()` | 橫向流程圖（支援箭頭標籤、高亮） |
| `platform_compare` | `draw_platform_compare()` | 平台對比圖（上下兩個流程） |
| `architecture` | `draw_architecture()` | 分層架構圖 |
| `metric_cards` | `draw_metric_cards()` | 指標卡片（數字 + 說明）|
| `comparison_table` | `draw_comparison_table()` | 對比表格 |
| `icon_list` | `draw_icon_list()` | 帶圖標的列表（check/cross/warn）|
| `glossary_with_diagrams` | `draw_glossary_page_with_diagrams()` | 術語頁（6 格有圖）|
| `glossary_text_only` | `draw_glossary_page_text_only()` | 術語頁（16 格純文字）|

---

## diagrams.md 完整繪製規則（強制）

⚠️ **這是強制規則，必須遵守**

### 1. 必須繪製每個圖表

diagrams.md 中的每個 `## ` 開頭的圖表都必須繪製，不能省略任何一個。

```
檢查清單：
□ 主圖（第 1 頁主報告內的圖表）
□ 附錄圖 1、2、3...（每個需要獨立的附錄頁面）
□ 術語解釋頁
```

### 2. 必須解析「SVG 生成指示」的詳細內容

當 diagrams.md 的「SVG 生成指示」區塊包含以下內容時，**必須**相應處理：

| 指示內容 | 必須處理方式 |
|----------|-------------|
| 「內部流程」「橫向節點」 | 使用 `draw_before_after_with_flow()` 或 `draw_flow_detailed()`，不能只用項目列表 |
| 「箭頭上標文字」 | 傳入 `arrow_labels` 參數 |
| 「問題標示」「紅色虛線框」 | 設定節點的 `highlight: True` |
| 「底部表格」「對比表格」 | 傳入 `bottom_table` 參數或另外呼叫 `draw_comparison_table()` |
| 「四層架構」「分層」 | 使用 `draw_architecture()` |
| 「上下對比」「平台對比」 | 使用 `draw_platform_compare()` |

### 3. 判斷使用簡單版還是詳細版函數

**使用 `draw_before_after()`（簡單版）的條件：**
- diagrams.md 的「SVG 生成指示」只列出項目點（bullet points）
- 沒有提到「內部流程」「節點」「箭頭上標」等關鍵字

**使用 `draw_before_after_with_flow()`（詳細版）的條件：**
- diagrams.md 的「SVG 生成指示」提到「內部流程」「橫向節點」
- 列出多個有順序的步驟（如 1. 2. 3. 4.）
- 提到箭頭上的文字、時間標籤、問題標示等

### 4. 附錄頁面產生規則

```python
# 投影片結構
slide_1 = 主報告（one_page.md 內容 + 主圖）
slide_2 = 附錄圖 1（如 diagrams.md 有「附錄圖 1」）
slide_3 = 附錄圖 2（如 diagrams.md 有「附錄圖 2」）
...
slide_N = 術語解釋（glossary.md 內容）
```

**禁止**：將附錄圖省略或只用文字描述替代。

---

## 流程圖自適應佈局規則（混合方案）

⚠️ **重要：render_this.py 必須包含自適應判斷邏輯**

當繪製橫向流程圖時，必須先判斷是否需要自動切換為縱向：

### 判斷條件（任一成立即切換縱向）

1. 節點數量 > 6
2. 計算後的節點寬度 < 0.8 英吋
3. 文字估算寬度超過節點寬度

### 必須包含的函數

在產生 render_this.py 時，確保包含以下函數（從 render_example.py 複製）：

- `FLOW_LAYOUT_CONFIG` - 佈局配置參數
- `calculate_text_width()` - 計算文字寬度（中文=2，英文=1）
- `estimate_node_min_width()` - 估算節點最小寬度
- `should_use_vertical_flow()` - 判斷是否切換縱向
- `draw_flow_vertical()` - 縱向流程圖
- `draw_flow_adaptive()` - 自適應包裝函數（推薦使用）

### 調用方式

```python
# 方式 1：直接使用自適應版本（推薦）
draw_flow_adaptive(
    slide, left, top, width, height,
    nodes=parsed_nodes,
    arrow_labels=parsed_arrow_labels
)

# 方式 2：手動判斷後調用
should_vertical, reason = should_use_vertical_flow(nodes, width)
if should_vertical:
    print(f"[自動切換縱向] {reason}")
    draw_flow_vertical(slide, left, top, width, height, nodes)
else:
    draw_flow(slide, left, top, width, height, nodes)
```

---

## 圖表數量自動檢查（強制執行）

⚠️ **在產生 render_this.py 之前，必須執行此檢查**

**目的**：確保 render_this.py 會產生正確數量的投影片，並為每個圖表呼叫對應的繪圖函數。

### 步驟 1：解析 diagrams.md 計算圖表總數

```python
# 偽代碼範例
diagrams_md_content = read_file("./output/phase5/diagrams.md")

# 計算主圖數量（通常為 1）
main_diagram_count = count_headings(diagrams_md_content, pattern="## 主圖")

# 計算附錄圖數量
appendix_diagram_count = count_headings(diagrams_md_content, pattern="## 附錄圖")

total_diagram_count = main_diagram_count + appendix_diagram_count

# 投影片總數 = 1（主報告+主圖）+ 附錄圖數量 + 術語表頁數
expected_slide_count = 1 + appendix_diagram_count + glossary_page_count
```

### 步驟 2：提取每個圖表的資訊

對每個圖表提取以下資訊：

| 資訊項目 | 說明 | 範例 |
|---------|------|------|
| 名稱 | 圖表標題 | "主圖：導入 SDK 同步機制前後的延遲差異" |
| 類型 | 圖表類型 | before_after / flow / platform_compare / architecture |
| 位置 | 在哪一頁 | 主圖在第 1 頁，附錄圖 1 在第 2 頁，依此類推 |

### 步驟 3：錯誤處理

如果產生的 render_this.py 不符合預期：

```
IF 投影片數量 != expected_slide_count:
    ERROR: "render_this.py 應該產生 {expected_slide_count} 頁投影片，但實際只有 {actual_slide_count} 頁"
    STOP

IF 缺少附錄圖的繪製呼叫:
    ERROR: "diagrams.md 定義了附錄圖 {X}，但 render_this.py 沒有對應的繪製程式碼"
    列出缺少的圖表名稱
    STOP
```
