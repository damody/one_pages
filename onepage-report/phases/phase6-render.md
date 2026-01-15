# Phase 6：渲染輸出

## 6.0 入口檢查

**IF `RESUME_FROM` = 6：**
1. 從 `./output/phase5/` 讀取以下檔案作為輸入：
   - `one_page.md` → 主報告內容
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
mkdir -p ./output
```

---

## 6.2 儲存 diagrams.md 並產生圖表

根據 `DIAGRAM_METHOD` 設定決定圖表產生方式：

| DIAGRAM_METHOD | 處理流程 | 參考檔案 |
|----------------|----------|----------|
| `svg_png` | 使用 Task subagent 生成 SVG → cairosvg 轉 PNG → 嵌入 PPTX | `Read {skill_dir}/reference/svg-generation.md` |
| `pptx_shapes` | 在 render_this.py 中直接使用 python-pptx shapes API 繪製 | `Read {skill_dir}/reference/pptx-shapes.md` |

1. 將 diagrams.md 內容儲存到 `./output/diagrams.md`

---

### 6.2.A 方式一：SVG/PNG（當 DIAGRAM_METHOD = svg_png）

**執行前請讀取：** `{skill_dir}/reference/svg-generation.md`

使用 **Task 工具調用 subagent** 生成 SVG 圖表。

對於 diagrams.md 中的**每個圖表區塊**，使用 Task 工具調用 subagent 生成 SVG：

```
Task(
  description="生成{區塊名稱} SVG",
  subagent_type="general-purpose",
  prompt="""
你是 SVG 圖表生成專家。請根據以下指示生成 SVG 圖表。

{從 reference/svg-generation.md 讀取的規格}

## 圖表內容
{從 diagrams.md 讀取的「SVG 生成指示」內容}

## 輸出
使用 Write 工具將完整 SVG 代碼寫入：./output/{output_filename}.svg
不要用 markdown 包裝，直接輸出純 SVG 代碼。
"""
)
```

**輸出檔案命名：**

| 區塊名稱 | 輸出檔案 |
|----------|----------|
| 主圖 | `./output/main_diagram.svg` |
| 附錄圖 1 | `./output/appendix_diagram_1.svg` |
| 附錄圖 2 | `./output/appendix_diagram_2.svg` |

**執行順序：** 可以**並行**執行多個 Task 來加速生成

---

### 6.2.5 SVG 轉 PNG（透明背景）

在嵌入 PPTX 之前，將所有 SVG 轉換為透明背景的 PNG：

```python
import os
import cairosvg

def convert_svg_to_png(svg_path, png_path=None, scale=2):
    if png_path is None:
        png_path = svg_path.rsplit('.', 1)[0] + '.png'
    cairosvg.svg2png(
        url=svg_path,
        write_to=png_path,
        scale=scale,
        background_color=None  # 保持透明背景
    )
    return png_path

# 轉換所有 SVG 檔案
svg_files = [f for f in os.listdir('.') if f.endswith('.svg')]
for svg_file in svg_files:
    convert_svg_to_png(svg_file)
```

---

### 6.2.B 方式二：PPTX Shapes（當 DIAGRAM_METHOD = pptx_shapes）

**執行前請讀取：** `{skill_dir}/reference/pptx-shapes.md`

使用 python-pptx 內建的 shapes API 直接在投影片上繪製圖表。

優點：
- 產生的圖表可直接在 PowerPoint 中編輯
- 不需要 cairosvg 依賴
- 避免 emoji 無法渲染的問題

---

## 6.3 產生 PPTX

這是最關鍵的步驟。

### 執行前準備

1. 讀取 `{skill_dir}/scripts/pptx_reference.py` 了解 python-pptx API 用法

2. 根據 one_page.md 的內容，動態產生 Python 程式碼

### ⚠️ 內容完整性要求（絕對禁止刪減）

- **one_page.md 的每一段文字都必須出現在投影片中**
- **glossary.md 的每一個術語解釋都必須放入附錄**
- 不能因為版面不夠就省略內容
- 如果內容太多，應該調小字體（最小 8pt）或分多頁，而不是刪減
- 表格的每一行每一列都必須完整呈現

### 佈局決策原則

- 圖表與相關說明要放在一起
- 根據內容量決定佈局（不要固定）
- 證據多 → 可能需要左右分欄
- 圖表複雜 → 給圖更多空間
- 字體大小根據內容量調整（但不小於 8pt）
- **有表格時**：表格放在投影片下方或右側

### 產生程式碼

將產生的程式碼儲存到 `./output/render_this.py`

---

### 6.3.0 產生 render_this.py 程式碼（必須執行）

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

def draw_metric_cards(slide, left, top, width, height, metrics):
    """繪製指標卡片 - 從 test_shapes_full.py 複製完整實作"""
    # ... 複製 test_shapes_full.py 中的完整函數 ...
    pass

def draw_comparison_table(slide, left, top, width, height, headers, rows):
    """繪製對比表格 - 從 test_shapes_full.py 複製完整實作"""
    # ... 複製 test_shapes_full.py 中的完整函數 ...
    pass

def draw_icon_list(slide, left, top, width, item_height, items):
    """繪製帶圖標的列表 - 從 test_shapes_full.py 複製完整實作"""
    # ... 複製 test_shapes_full.py 中的完整函數 ...
    pass

# ===== 文字方塊輔助函數（從 test_shapes_full.py 複製） =====

def add_section_title(slide, left, top, width, text, color=COLOR_BLUE):
    """加入區塊標題 - 從 test_shapes_full.py 複製完整實作"""
    pass

def add_bullet_list(slide, left, top, width, height, items, font_size=10):
    """加入項目列表 - 從 test_shapes_full.py 複製完整實作"""
    pass

# ===== 術語卡片函數（從 test_shapes_full.py 複製，用於附錄頁）=====

def draw_glossary_card_with_diagram(slide, left, top, width, height, term, desc, diagram_type, diagram_params):
    """繪製帶示意圖的術語卡片 - 從 test_shapes_full.py 複製完整實作"""
    pass

def draw_glossary_page_with_diagrams(slide, title, terms):
    """繪製一頁 6 格有圖片的術語卡片 - 從 test_shapes_full.py 複製完整實作"""
    pass

def draw_glossary_page_text_only(slide, title, terms):
    """繪製一頁 16 格純文字術語卡片 - 從 test_shapes_full.py 複製完整實作"""
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

    # 4. 加入標題（從 one_page.md 的 # 標題）
    # 5. 加入副標題（從 one_page.md 的 > 引言）
    # 6. 根據 one_page.md 的各個 ## 區塊，呼叫 add_content_box()
    # 7. 加入表格（若有 table.md）

    # 8. 根據 diagrams.md 繪製圖表
    #    解析 diagrams.md 中每個圖表的類型和參數，呼叫對應的繪製函數
    #    範例：
    #    draw_before_after(slide, left=0.3, top=2.5, width=6.0, height=2.5,
    #        before_title="改善前", before_items=["問題1", "問題2"],
    #        after_title="改善後", after_items=["解決1", "解決2"])
    #
    #    draw_flow(slide, left=0.5, top=5.0, width=12.0, height=0.8,
    #        nodes=[{"title": "步驟1", "desc": "說明"}, {"title": "步驟2", "desc": "說明"}])

    # 9. 儲存
    prs.save('one_page.pptx')
    print("已生成：one_page.pptx")

if __name__ == "__main__":
    create_pptx()
```

**步驟 3：內容對應規則**

| one_page.md 區塊 | render_this.py 對應 |
|------------------|---------------------|
| `# 主標題` | `add_textbox()` 標題區，字體 Pt(26) |
| `> 副標題引言` | `add_textbox()` 副標題區，字體 Pt(11) |
| `## 區塊標題` + 內容 | `add_content_box()` 圓角矩形區塊 |
| 表格 | `add_table()` |
| `[[術語]]` 標記 | 使用 `parse_text_with_terms()` 加入超連結 |

**步驟 4：區塊顏色分配**

根據區塊語意選擇顏色：

| 區塊類型 | 顏色變數 |
|----------|----------|
| 技術背景、成功判定 | ACCENT_BLUE |
| 問題、POC 設計 | ACCENT_ORANGE |
| 效益、解決方案 | ACCENT_GREEN |
| 架構、技術細節 | ACCENT_PURPLE |
| 行動、決策 | ACCENT_RED |

**步驟 5：使用 Write 工具寫出檔案**

```
Write(
  file_path="./output/render_this.py",
  content="... 完整 Python 程式碼 ..."
)
```

⚠️ **重要**：必須用 Write 工具實際寫出檔案，不能只是在回覆中顯示程式碼。

**步驟 6：解析 diagrams.md 並產生繪圖呼叫**

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

**圖表類型對應函數（從 test_shapes_full.py）：**

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

### 6.3.0.1 diagrams.md 完整繪製規則（強制）

⚠️ **這是強制規則，必須遵守**

#### 1. 必須繪製每個圖表

diagrams.md 中的每個 `## ` 開頭的圖表都必須繪製，不能省略任何一個。

```
檢查清單：
□ 主圖（第 1 頁主報告內的圖表）
□ 附錄圖 1、2、3...（每個需要獨立的附錄頁面）
□ 術語解釋頁
```

#### 2. 必須解析「SVG 生成指示」的詳細內容

當 diagrams.md 的「SVG 生成指示」區塊包含以下內容時，**必須**相應處理：

| 指示內容 | 必須處理方式 |
|----------|-------------|
| 「內部流程」「橫向節點」 | 使用 `draw_before_after_with_flow()` 或 `draw_flow_detailed()`，不能只用項目列表 |
| 「箭頭上標文字」 | 傳入 `arrow_labels` 參數 |
| 「問題標示」「紅色虛線框」 | 設定節點的 `highlight: True` |
| 「底部表格」「對比表格」 | 傳入 `bottom_table` 參數或另外呼叫 `draw_comparison_table()` |
| 「四層架構」「分層」 | 使用 `draw_architecture()` |
| 「上下對比」「平台對比」 | 使用 `draw_platform_compare()` |

#### 3. 判斷使用簡單版還是詳細版函數

**使用 `draw_before_after()`（簡單版）的條件：**
- diagrams.md 的「SVG 生成指示」只列出項目點（bullet points）
- 沒有提到「內部流程」「節點」「箭頭上標」等關鍵字

**使用 `draw_before_after_with_flow()`（詳細版）的條件：**
- diagrams.md 的「SVG 生成指示」提到「內部流程」「橫向節點」
- 列出多個有順序的步驟（如 1. 2. 3. 4.）
- 提到箭頭上的文字、時間標籤、問題標示等

#### 4. 附錄頁面產生規則

```python
# 投影片結構
slide_1 = 主報告（one_page.md 內容 + 主圖）
slide_2 = 附錄圖 1（如 diagrams.md 有「附錄圖 1」）
slide_3 = 附錄圖 2（如 diagrams.md 有「附錄圖 2」）
...
slide_N = 術語解釋（glossary.md 內容）
```

**禁止**：將附錄圖省略或只用文字描述替代。

#### 5. 參數轉換範例

**diagrams.md 定義**（before_after 有內部流程）：
```markdown
## 主圖：前後對比

### SVG 生成指示
左側「改善前」內部流程：
1. 觸控輸入 [時間點：T=0]
2. Frame Queue [問題：堆積 2-3 幀] ⚠️ 問題點
3. GPU 畫圖
4. 螢幕顯示
箭頭上標：讀取輸入 → 等前面畫完 → 送去顯示

底部表格：
| 指標 | 改善前 | 改善後 |
...
```

**對應 render_this.py 程式碼**：
```python
draw_before_after_with_flow(
    slide=slide,
    left=0.3, top=1.5, width=12.7, height=3.5,
    before_title="改善前：畫面堆積導致延遲",
    before_flow_nodes=[
        {"title": "觸控輸入", "desc": "T=0", "color": COLOR_BLUE},
        {"title": "Frame Queue", "desc": "堆積 2-3 幀", "color": COLOR_RED, "highlight": True},
        {"title": "GPU 畫圖", "desc": "等前面畫完", "color": COLOR_BLUE},
        {"title": "螢幕顯示", "desc": "過時畫面", "color": COLOR_BLUE}
    ],
    before_arrow_labels=["讀取輸入", "等前面畫完", "送去顯示"],
    after_title="改善後：精準同步即時反應",
    after_flow_nodes=[
        {"title": "GPU 信號", "desc": "準備好了", "color": COLOR_GREEN},
        {"title": "觸控輸入", "desc": "最佳時機", "color": COLOR_GREEN},
        {"title": "GPU 畫圖", "desc": "立即畫", "color": COLOR_GREEN},
        {"title": "螢幕顯示", "desc": "最新畫面", "color": COLOR_GREEN}
    ],
    after_arrow_labels=["同步信號", "馬上讀取", "直接顯示"],
    center_arrow_label="導入 SDK",
    bottom_table={
        "headers": ["指標", "改善前", "改善後", "說明"],
        "rows": [
            ["Frame Queue 堆積", "2-3 幀", "0-1 幀", "排隊減少"],
            ["輸入-顯示同步", "不精準", "精準對齊", "玩家感覺更即時"]
        ]
    }
)
```

---

## 6.3.1 Sub Agent 驗證步驟（必須執行）

在執行 render_this.py 之前，必須呼叫 Task tool 讓獨立的 sub agent 檢查程式碼是否完整包含所有內容。

```
Task(
  subagent_type="general-purpose",
  prompt="""
你是程式碼審查員，請驗證以下 Python 程式碼是否完整包含 markdown 的所有內容。

## 審查任務
逐一比對 markdown 和 Python 程式碼，確保沒有遺漏任何內容。

## 輸入 1：one_page.md 內容
{貼上完整 one_page.md}

## 輸入 2：glossary.md 內容
{貼上完整 glossary.md}

## 輸入 3：render_this.py 內容
{貼上完整 render_this.py}

## 審查清單（每項都要檢查）
1. one_page.md 的標題是否出現在 Python 中？
2. one_page.md 的每一個段落是否都有對應的文字？
3. one_page.md 的每一個重點是否都有出現？
4. one_page.md 的表格是否完整（每行每列）？
5. glossary.md 的每一個術語是否都在附錄中？
6. 數字是否正確（沒有抄錯或遺漏）？

## 輸出格式
- ✅ 內容完整：所有內容都已包含
- ❌ 有遺漏：列出遺漏的內容
"""
)
```

**如果 Sub Agent 發現遺漏：**
1. 根據指出的遺漏修改 render_this.py
2. 再次呼叫 Sub Agent 驗證
3. 重複直到 ✅ 內容完整

---

## 6.3.2 執行產生 PPTX

驗證通過後，執行 Python：

```bash
cd ./output && python render_this.py
```

---

## 6.3.3 產生附錄投影片

### 投影片結構

```
投影片 1：主報告（one_page.md 內容 + 主圖）
投影片 2：附錄 - 流程圖詳解（如有附錄圖）
投影片 3：附錄 - 術語解釋（glossary.md 內容）
```

### 附錄圖表佈局

| 附錄圖數量 | 佈局 | 每頁圖數 |
|-----------|------|---------|
| 1-2 張 | 上下排列 | 1-2 |
| 3-4 張 | 2x2 網格 | 4 |
| 5+ 張 | 分多頁，每頁 2x2 | 4 |

### 術語超連結

- 主投影片中的 `[[術語]]` 標記會轉換為藍色底線文字
- 點擊可跳轉到附錄投影片（術語解釋頁）
- 附錄投影片顯示所有術語的白話解釋

---

## 6.3.5 排版審查（Layout Review）

**觸發條件**：`LAYOUT_REVIEW_ROUNDS > 0`

在生成 PPTX 後，執行排版審查以確保所有元素不會重疊。

### 審查流程

```
FOR round = 1 TO LAYOUT_REVIEW_ROUNDS:
    1. 收集投影片上所有元素的邊界框 (bounding box)
    2. 對每對元素計算是否重疊
    3. 若有重疊：
       a. 記錄重疊元素對
       b. 決定修正策略
       c. 執行修正（調整位置、縮減內容或字體）
    4. 若無重疊：提前結束審查，輸出「排版審查通過」
```

### 修正策略優先順序

| 優先順序 | 策略 | 說明 |
|----------|------|------|
| 1 | 調整位置 | 將下方元素往下移 |
| 2 | 縮減間距 | 減少元素內部的 padding 和 line spacing |
| 3 | 縮減內容 | 減少列表項目數量或縮短文字 |
| 4 | 縮小字體 | 降低字體大小（最小 7pt） |

---

## 6.3.5.1 圖表完整性驗證（Diagram Completeness Check）

**觸發條件**：`LAYOUT_REVIEW_ROUNDS > 0`（與排版審查同時執行）

**目的**：確保 diagrams.md 中描述的所有圖表都被正確繪製，不能被簡化或刪減。

### 驗證項目

| 檢查項目 | 說明 | 錯誤處理 |
|----------|------|----------|
| 圖表數量 | diagrams.md 中有幾個 `## ` 區塊，render_this.py 就要有幾個圖表繪製呼叫 | 補畫缺少的圖表 |
| 圖表類型 | 每個圖表的類型（before_after, flow, architecture 等）是否正確 | 修正為正確類型 |
| 內部流程節點 | 如果 diagrams.md 描述了內部流程節點，是否都有繪製 | 使用詳細版函數重繪 |
| 箭頭標籤 | 如果 diagrams.md 描述了箭頭上的文字，是否有繪製 | 補上箭頭標籤 |
| 附錄圖 | diagrams.md 的附錄圖是否都有對應的投影片 | 建立缺少的附錄頁 |

### 驗證步驟

```
1. **解析 diagrams.md**
   - 讀取 `./output/phase5/diagrams.md`（或 phase3/diagrams.md）
   - 識別所有 `## ` 開頭的圖表區塊
   - 提取每個圖表的：
     - 圖表名稱（主圖 / 附錄圖 N）
     - 類型（before_after / platform_compare / flow / architecture）
     - 是否有「內部流程」描述（關鍵字：步驟、節點、流程、→）
     - 是否有「箭頭上標文字」（關鍵字：箭頭上、連接、標註）
     - 是否有「底部表格」（關鍵字：底部、對比表、總結表）

2. **解析 render_this.py**
   - 讀取 `./output/render_this.py`
   - 識別所有 `draw_*` 函數呼叫
   - 提取每個繪製呼叫的：
     - 函數名稱（draw_before_after / draw_before_after_with_flow / draw_flow / draw_architecture 等）
     - 參數內容

3. **比對驗證**

   FOR each diagram in diagrams.md:
       a. 檢查 render_this.py 是否有對應的繪製呼叫
       b. 如果 diagrams.md 有「內部流程」描述：
          - 檢查是否使用詳細版函數（如 draw_before_after_with_flow 而非 draw_before_after）
          - 檢查參數中是否有流程節點陣列
       c. 如果 diagrams.md 有「箭頭標籤」描述：
          - 檢查是否有 arrow_labels 參數

       IF 發現問題：
           → 記錄問題類型和位置
           → 產生修正建議
```

### 輸出驗證報告

```markdown
## 圖表完整性驗證報告

### diagrams.md 定義的圖表
| # | 名稱 | 類型 | 有內部流程 | 有箭頭標籤 |
|---|------|------|-----------|-----------|
| 1 | 主圖 | before_after | ✓ | ✓ |
| 2 | 附錄圖 1 | architecture | - | - |
| 3 | 附錄圖 2 | platform_compare | ✓ | ✓ |

### render_this.py 繪製的圖表
| # | 函數呼叫 | 對應 diagrams.md |
|---|----------|-----------------|
| 1 | draw_before_after() | 主圖 |

### 問題清單
| 問題 | 說明 | 修正方式 |
|------|------|----------|
| 缺少附錄圖 1 | architecture 圖未繪製 | 新增 draw_architecture() 呼叫 |
| 缺少附錄圖 2 | platform_compare 圖未繪製 | 新增 draw_platform_compare() 呼叫 |
| 主圖過於簡化 | 使用 draw_before_after() 但 diagrams.md 有內部流程 | 改用 draw_before_after_with_flow() |
```

### 自動修正

IF 有問題：
1. 修改 render_this.py：
   - 補上缺少的圖表繪製呼叫
   - 將簡化版函數改為詳細版
   - 補上缺少的參數（流程節點、箭頭標籤等）
2. 重新執行 `python render_this.py`
3. 回到步驟 1 重新驗證

### 強制通過條件

圖表完整性驗證**必須通過**才能完成 Phase 6，不允許跳過或忽略。

---

## 6.3.6 內容溢出審查（Content Overflow Review）

**觸發條件**：`LAYOUT_REVIEW_ROUNDS > 0`

在重疊審查通過後，檢查每個 content_box 的文字內容是否超出方塊範圍。

### 審查流程

```
FOR each content_box in render_this.py:
    1. 取得該區塊參數：
       - box_width, box_height（英吋）
       - font_size（pt）
       - content_lines（字串陣列）

    2. 計算「每行可容納字數」：
       chars_per_line = (box_width - 0.12) * 72 / font_size * 0.7
       （0.7 為中文字體寬度修正係數）

    3. 計算「實際行數」：
       FOR each line in content_lines:
           IF len(line) == 0: actual_lines += 0.5
           ELSE: actual_lines += ceil(len(line) / chars_per_line)

    4. 計算「可用行數」：
       available_height = box_height - 0.32  # 減去標題和 padding
       line_height = (font_size + 1) / 72    # pt 轉英吋，含 space_after
       available_lines = available_height / line_height

    5. 若 actual_lines > available_lines：
       → 標記為「溢出區塊」
       → 先執行「合併短行」流程
       → 若仍溢出，再執行「內容精簡」流程
```

### 「合併短行」流程（優先執行）

先檢查是否有太短的行浪費右邊空間，嘗試合併：

```
FOR each line in content_lines:
    IF len(line) < chars_per_line * 0.7:  # 行長度不到 70%
        → 檢查與下一行合併後是否 <= chars_per_line
        → 若不超過，用逗號或頓號連接
        → 合併後若仍 < chars_per_line * 0.7，繼續嘗試合併下一行
```

**合併範例：**

| 合併前 | 合併後 |
|--------|--------|
| `"• BufferQueue 緩衝延遲"` | `"• BufferQueue 緩衝延遲，遊戲畫好圖要交給 Android 處理，中間等待約 1-2 幀"` |
| `"  遊戲畫好圖要交給 Android 處理"` | |
| `"  中間等待約 1-2 幀"` | |

**合併原則：**
1. 同一個 bullet point 內的子句優先合併
2. 用逗號「，」連接語意連貫的句子
3. 合併後長度不超過 `chars_per_line`
4. 空行（用於視覺分隔）保留不合併

---

### 「內容精簡」流程（合併後仍溢出時執行）

當合併短行後仍溢出時，將白話文轉換為術語，減少文字量：

| 原文範例 | 精簡後 |
|----------|--------|
| 「FPSGO（聯發科的幀率控制工具）無法感知引擎內部」 | 「[[FPSGO]] 無法感知引擎內部」 |
| 「玩家按下螢幕到螢幕顏色改變的時間」 | 「[[Click-to-Photon]] 延遲」 |
| 「幀與幀之間的時間差異變小，代表偶爾卡一下的情況減少」 | 「[[1% Low]] 改善」 |
| 「把資料先存在離處理器很近的小容量高速記憶體中」 | 「[[cache]] 機制」 |

### 精簡優先順序

1. **優先精簡括號內的解釋**
   - 括號內的文字通常是補充說明，可以移到術語解釋

2. **優先精簡重複出現的概念**
   - 同一區塊出現多次的概念，只需第一次保留白話，後續用術語

3. **優先精簡非核心的說明**
   - 保留：結論、數字、關鍵論點
   - 精簡：背景解釋、類比說明

### 每行字數參考表

| 文字方塊寬度 | 字體大小 | 每行可容納中文字數 |
|-------------|----------|-------------------|
| 4.0 英吋 | 9pt | 約 28-30 字 |
| 4.0 英吋 | 8pt | 約 32-34 字 |
| 4.0 英吋 | 7pt | 約 36-38 字 |

### 精簡後重新驗證

精簡後需重新執行 6.3.1 Sub Agent 驗證，確保：
1. 所有內容仍然完整（只是換了表達方式）
2. 新增的 `[[術語]]` 標記都有對應的 glossary.md 條目

---

## 6.4 輸出演講稿

將最終版 script.md 儲存到 `./output/speaker_script.md`

**注意**：演講稿會同時存在兩處：
1. PPTX 投影片的備註欄（方便簡報時直接看）
2. `./output/speaker_script.md` 獨立檔案（方便編輯或列印）

---

## 6.5 輸出其他檔案

- `./output/citation_map.md`：來源對照表（含 web search 補充說明）
- `./output/glossary.md`：術語詞彙表

---

## 6.6 完成

告知使用者：

```
報告產生完成！

輸出檔案：
📊 ./output/one_page.pptx（投影片，含主報告 + 附錄術語解釋）
📝 ./output/speaker_script.md（演講稿獨立檔案）
🖼️ ./output/*.svg（原始圖表）
🖼️ ./output/*.png（透明背景圖表，嵌入 PPTX 用）
📚 ./output/citation_map.md（來源對照表，含 web search 補充說明）
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
