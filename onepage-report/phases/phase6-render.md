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
   - `technical_appendix.md` → 技術附錄
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

## 6.3 產生 PPTX（使用 Sub Agent）

**為什麼要用 Sub Agent？**
- render_this.py 通常有 500-1000 行程式碼，直接在主對話中產生會導致 context 爆掉
- 需要讀取多個檔案（one_page.md, diagrams.md, glossary.md, script.md, technical_appendix.md 等）
- 可能需要多輪迭代修正（layout review, diagram completeness check）
- 執行 Python 後的輸出也會佔用大量 context

**Sub Agent 的職責**：
1. 產生 render_this.py（包含完整的圖表繪製函數）
2. 執行 render_this.py 產生 PPTX
3. 驗證圖表完整性和排版
4. 多輪迭代修正直到通過驗證
5. 產生演講稿文字檔

---

## 6.3.1 Task 工具調用方式

```python
Task(
  description="產生 PPTX 和演講稿",
  subagent_type="general-purpose",
  prompt=f"""
你是 PPTX 渲染專家，負責將 Markdown 報告轉換為專業投影片。

## 你的任務

1. 產生 render_this.py Python 程式碼
2. 執行程式碼產生 PPTX 檔案
3. 驗證圖表完整性和排版
4. 產生演講稿文字檔

## 輸入檔案

請讀取以下檔案作為輸入：

### 報告內容
- `./output/phase5/one_page.md`（如不存在則讀取 phase3/one_page.md）
- `./output/phase5/diagrams.md`
- `./output/phase5/glossary.md`
- `./output/phase5/script.md`
- `./output/phase5/technical_appendix.md`
- `./output/phase5/table.md`（如有）

### 全域設定
- `./output/phase1/config.md`（讀取 DETAIL_LEVEL, DIAGRAM_METHOD, LAYOUT_REVIEW_ROUNDS）

### 參考資料（從 skill 目錄讀取）
- `{{skill_dir}}/scripts/pptx_reference.py`（python-pptx API 參考）
- `{{skill_dir}}/reference/pptx-shapes.md`（圖表繪製規範）
- `{{skill_dir}}/reference/render_example.py`（⭐ 最重要：完整的 draw 函數實作範例）
- `{{skill_dir}}/test_shapes_full.py`（完整佈局範例）

## ⚠️ 內容完整性要求（絕對禁止刪減）

- **one_page.md 的每一段文字都必須出現在投影片中**
- **glossary.md 的每一個術語解釋都必須放入附錄**
- **technical_appendix.md 的每個章節都必須產生對應投影片**（如 DETAIL_LEVEL != TECHNICAL）
- 不能因為版面不夠就省略內容
- 如果內容太多，應該調小字體（最小 8pt）或分多頁，而不是刪減
- 表格的每一行每一列都必須完整呈現

## 佈局決策原則

- 圖表與相關說明要放在一起
- 根據內容量決定佈局（不要固定）
- 證據多 → 可能需要左右分欄
- 圖表複雜 → 給圖更多空間
- 字體大小根據內容量調整（但不小於 8pt）
- **有表格時**：表格放在投影片下方或右側

---

## 步驟 1：產生 render_this.py

### 1.1 讀取參考資料

**必須讀取**（按順序）：
1. `{{skill_dir}}/scripts/pptx_reference.py` - API 參考
2. `{{skill_dir}}/reference/pptx-shapes.md` - 圖表繪製函數規範
3. `{{skill_dir}}/reference/render_example.py` - ⭐⭐ 最重要：完整的 draw 函數實作範例
4. `{{skill_dir}}/test_shapes_full.py` - 完整佈局範例

⚠️ **最重要**：`render_example.py` 是經過驗證的完整範例，包含：

**圖表繪製函數（必須複製完整實作）：**
- `draw_before_after_with_vertical_flow()` - 詳細版前後對比圖，帶有垂直內部流程節點
- `draw_platform_compare_with_flow()` - 平台對比圖，帶有內部流程
- `draw_flow_detailed()` - 詳細流程圖，支援自訂節點顏色和箭頭標籤
- `draw_architecture()` - 系統架構圖
- `draw_comparison_table()` - 技術總結表（⭐ 技術附錄用）
- `draw_platform_compare()` - 引擎差異對比（⭐ 技術附錄用）
- `add_bullet_list()` - 項目列表（⭐ 技術附錄用）

**關鍵輔助函數（必須複製）：**
- `add_background()` - 統一背景
- `add_markdown_text()` - 支援粗體/斜體的文字渲染
- `create_hyperlink()` - 術語超連結
- `add_citation_box()` - 來源引用標註

### 1.2 產生程式碼結構

```python
# render_this.py 結構範例
from pptx import Presentation
from pptx.util import Inches, Pt
# ... 其他 import

# ===== 設定區 =====
DETAIL_LEVEL = "{從 config.md 讀取}"
DIAGRAM_METHOD = "{從 config.md 讀取}"

# ===== 從 render_example.py 複製完整的繪圖函數 =====
def add_background(slide, prs):
    # 完整實作...

def draw_before_after_with_vertical_flow(...):
    # 完整實作...

def draw_flow_detailed(...):
    # 完整實作...

def draw_comparison_table(...):  # ⭐ 技術附錄用
    # 完整實作...

def draw_platform_compare(...):  # ⭐ 技術附錄用
    # 完整實作...

def add_bullet_list(...):  # ⭐ 技術附錄用
    # 完整實作...

# ... 其他繪圖函數

# ===== 主程式 =====
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

# 投影片 1：主報告
slide1 = prs.slides.add_slide(prs.slide_layouts[6])
add_background(slide1, prs)
# ... 根據 one_page.md 產生內容

# ⭐ 技術附錄投影片（如 DETAIL_LEVEL != TECHNICAL）
if DETAIL_LEVEL in ["BALANCED", "EXECUTIVE"]:
    # 讀取 technical_appendix.md
    # 解析章節結構
    # 為每個章節產生投影片
    for chapter in chapters:
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        # 根據章節類型使用對應繪圖函數

# 附錄圖投影片
# ...

# 術語解釋投影片
# ...

prs.save('./output/final.pptx')
print("✅ PPTX 產生完成")
```

### 1.3 技術附錄投影片產生邏輯

```python
# 讀取 technical_appendix.md
technical_appendix_path = "./output/phase5/technical_appendix.md"
if not os.path.exists(technical_appendix_path):
    technical_appendix_path = "./output/phase3/technical_appendix.md"

if os.path.exists(technical_appendix_path):
    with open(technical_appendix_path, 'r', encoding='utf-8') as f:
        tech_content = f.read()

    # 檢查是否有實質內容
    if "# 無技術附錄" not in tech_content and DETAIL_LEVEL != "TECHNICAL":
        # 解析章節（## 開頭）
        chapters = parse_chapters(tech_content)

        for chapter in chapters:
            slide = prs.slides.add_slide(prs.slide_layouts[6])
            add_background(slide, prs)

            # 標題
            title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(12.5), Inches(0.5))
            p = title_box.text_frame.paragraphs[0]
            p.text = f"技術附錄：{{chapter['title']}}"

            # 根據內容類型選擇繪圖函數
            if "執行緒" in chapter['content'] and "函數" in chapter['content']:
                # 左側：流程圖
                flow_nodes = extract_flow_nodes(chapter['content'])
                draw_flow_detailed(slide, left=0.3, top=0.6, width=5.0, height=6.0,
                                 nodes=flow_nodes, direction="vertical")

                # 右側：文字列表
                thread_list = extract_thread_list(chapter['content'])
                add_bullet_list(slide, left=5.5, top=0.6, width=7.5, height=6.0,
                              items=thread_list, font_size=10)

            elif "|" in chapter['content'] and "階段" in chapter['content']:
                # 技術總結表
                table_data = extract_table_data(chapter['content'])
                draw_comparison_table(slide, left=0.5, top=1.0, width=12.0, height=5.5,
                                    data=table_data)

            elif "Unity" in chapter['content'] and "Unreal" in chapter['content']:
                # 引擎差異分析
                comparison_data = extract_comparison_data(chapter['content'])
                draw_platform_compare(slide, left=0.5, top=1.0, width=12.0, height=5.5,
                                    data=comparison_data)

            # 底部：Citation 來源
            citation_ids = extract_citation_ids(chapter['content'])
            if citation_ids:
                citation_box = slide.shapes.add_textbox(Inches(0.5), Inches(6.8), Inches(12.0), Inches(0.3))
                p = citation_box.text_frame.paragraphs[0]
                p.text = f"來源：{{', '.join([f'materials.md [{{cid}}]' for cid in citation_ids])}}"
                p.font.size = Pt(8)
```

### 1.4 使用 Write 工具寫入檔案

將產生的完整程式碼寫入 `./output/render_this.py`

---

## 步驟 2：執行 render_this.py

使用 Bash 工具執行：

```bash
cd ./output && python render_this.py
```

**預期輸出**：
- `./output/final.pptx` 檔案產生
- 終端輸出「✅ PPTX 產生完成」

**錯誤處理**：
- 如果出現 Python 錯誤，讀取錯誤訊息，修正 render_this.py，重新執行
- 常見錯誤：Import 錯誤、路徑錯誤、API 呼叫錯誤

---

## 步驟 3：驗證圖表完整性（必須執行）

**觸發條件**：`LAYOUT_REVIEW_ROUNDS > 0`（從 config.md 讀取）

### 3.1 驗證項目

| 檢查項目 | 說明 |
|---------|------|
| diagrams.md 圖表數量 | diagrams.md 有幾個圖表，render_this.py 就要有幾個 draw_* 呼叫 |
| 內部流程節點 | diagrams.md 描述的內部流程節點是否都有繪製 |
| 箭頭標籤 | diagrams.md 描述的箭頭標籤是否有繪製 |
| **technical_appendix.md 章節** | 每個章節是否都有對應投影片 |
| **技術附錄表格** | technical_appendix.md 的表格是否有繪製 |
| **技術附錄流程圖** | technical_appendix.md 的執行緒/函數列表是否有繪製流程圖 |

### 3.2 驗證步驟

1. 讀取 `./output/phase5/diagrams.md` 和 `./output/phase5/technical_appendix.md`
2. 解析所有圖表區塊和技術附錄章節
3. 讀取 `./output/render_this.py`，檢查是否有對應的 draw_* 函數呼叫
4. 產生驗證報告

### 3.3 自動修正

IF 發現問題：
1. 修改 render_this.py，補上缺少的圖表繪製呼叫
2. 重新執行 `python render_this.py`
3. 回到驗證步驟

**強制通過條件**：圖表完整性驗證**必須通過**才能完成 Phase 6

---

## 步驟 4：產生演講稿文字檔

讀取 `./output/phase5/script.md`（如不存在則讀取 phase3/script.md），將內容寫入 `./output/script.txt`：

```bash
# 使用 Write 工具
./output/script.txt 內容：
{{script.md 的完整內容}}
```

---

## 輸出檔案

完成後，應該產生以下檔案：

| 檔案 | 說明 |
|------|------|
| `./output/render_this.py` | Python 程式碼 |
| `./output/final.pptx` | 最終 PPTX 檔案 |
| `./output/script.txt` | 演講稿文字檔 |

---

## 成功判定

當以下條件全部滿足時，回報「✅ Phase 6 完成」：

1. ✅ final.pptx 檔案存在
2. ✅ 圖表完整性驗證通過（diagrams.md + technical_appendix.md）
3. ✅ script.txt 檔案存在
4. ✅ 無 Python 執行錯誤

請開始執行。
"""
)
```

**注意**：
- `{{skill_dir}}` 會在實際呼叫時被替換為 skill 目錄的絕對路徑
- Sub Agent 有完整的工具存取權限（Read, Write, Bash, Glob, Grep）
- Sub Agent 會在獨立的 context 中執行，不會影響主對話的 token 使用

---

### 6.3.0 產生 render_this.py 程式碼（Sub Agent 內部執行）

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
    """繪製帶示意圖的術語卡片 - 從 test_shapes_full.py 複製完整實作

    參數：
    - diagram_type: 'flow' / 'before_after' / 'timeline' / 'icon'
    - diagram_params: 字典，包含該類型圖表需要的參數
      - flow: {"nodes": [...]}
      - before_after: {"before_text": "...", "after_text": "..."}
      - timeline: {"stages": [...]}
      - icon: {"icon_type": "...", "label": "..."}
    """
    pass

def draw_glossary_page_with_diagrams(slide, title, terms):
    """繪製一頁 6 格有圖片的術語卡片（2 列 x 3 欄）- 從 test_shapes_full.py 複製完整實作

    參數：
    - terms: 列表，每個元素包含 {"term": "...", "desc": "...", "diagram_type": "...", "diagram_params": {...}}
    - 最多 6 個術語，超過會被截斷
    """
    pass

def draw_glossary_page_text_only(slide, title, terms):
    """繪製一頁 16 格純文字術語卡片（4 列 x 4 欄）- 從 test_shapes_full.py 複製完整實作

    參數：
    - terms: 列表，每個元素包含 {"term": "...", "desc": "..."}
    - 最多 16 個術語，超過會被截斷
    """
    pass

# ===== 迷你圖表函數（用於術語卡片內的示意圖）=====

def draw_mini_flow(slide, left, top, width, height, nodes):
    """繪製迷你流程圖 - 從 test_shapes_full.py 複製完整實作"""
    pass

def draw_mini_before_after(slide, left, top, width, height, before_text, after_text):
    """繪製迷你前後對比圖 - 從 test_shapes_full.py 複製完整實作"""
    pass

def draw_mini_timeline(slide, left, top, width, height, stages):
    """繪製迷你時間軸 - 從 test_shapes_full.py 複製完整實作"""
    pass

def draw_mini_icon(slide, left, top, width, height, icon_type, label):
    """繪製迷你圖標 - 從 test_shapes_full.py 複製完整實作"""
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

### 6.3.0.2 流程圖自適應佈局規則（混合方案）

⚠️ **重要：render_this.py 必須包含自適應判斷邏輯**

當繪製橫向流程圖時，必須先判斷是否需要自動切換為縱向：

#### 判斷條件（任一成立即切換縱向）

1. 節點數量 > 6
2. 計算後的節點寬度 < 0.8 英吋
3. 文字估算寬度超過節點寬度

#### 必須包含的函數

在產生 render_this.py 時，確保包含以下函數（從 render_example.py 複製）：

- `FLOW_LAYOUT_CONFIG` - 佈局配置參數
- `calculate_text_width()` - 計算文字寬度（中文=2，英文=1）
- `estimate_node_min_width()` - 估算節點最小寬度
- `should_use_vertical_flow()` - 判斷是否切換縱向
- `draw_flow_vertical()` - 縱向流程圖
- `draw_flow_adaptive()` - 自適應包裝函數（推薦使用）

#### 調用方式

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

此邏輯會自動判斷並選擇最佳佈局方式，避免文字被壓縮成垂直排列。

#### 前後對比圖的自適應邏輯

當使用 `draw_before_after_with_flow()` 時，左右兩側的內部流程也應判斷：

```python
# 判斷左右兩側是否需要縱向
before_vertical, _ = should_use_vertical_flow(before_flow_nodes, box_width - 0.2, min_node_width=0.7)
after_vertical, _ = should_use_vertical_flow(after_flow_nodes, box_width - 0.2, min_node_width=0.7)

if before_vertical or after_vertical:
    # 任一側需要縱向，則使用 draw_before_after_with_vertical_flow()
    # 保持視覺一致性
    pass
```

---

### 6.3.0.3 圖表數量自動檢查（強制執行）

⚠️ **在產生 render_this.py 之前，必須執行此檢查**

**目的**：確保 render_this.py 會產生正確數量的投影片，並為每個圖表呼叫對應的繪圖函數。

#### 步驟 1：解析 diagrams.md 計算圖表總數

```python
# 偽代碼範例
diagrams_md_content = read_file("./output/phase5/diagrams.md")

# 計算主圖數量（通常為 1）
main_diagram_count = count_headings(diagrams_md_content, pattern="## 主圖")

# 計算附錄圖數量
appendix_diagram_count = count_headings(diagrams_md_content, pattern="## 附錄圖")

total_diagram_count = main_diagram_count + appendix_diagram_count

# 投影片總數 = 1（主報告+主圖）+ 附錄圖數量 + 術語表頁數
# 術語表頁數：
#   - 如果 glossary.md 有 10 個以上術語，且前 6 個適合配圖 → 2 頁（6 格有圖 + 16 格純文字）
#   - 否則 → 1 頁（16 格純文字）
glossary_page_count = 2 if (len(glossary_terms) >= 10 and can_add_diagrams) else 1
expected_slide_count = 1 + appendix_diagram_count + glossary_page_count
```

#### 步驟 2：提取每個圖表的資訊

對每個圖表提取以下資訊：

| 資訊項目 | 說明 | 範例 |
|---------|------|------|
| 名稱 | 圖表標題 | "主圖：導入 SDK 同步機制前後的延遲差異" |
| 類型 | 圖表類型 | before_after / flow / platform_compare / architecture |
| 位置 | 在哪一頁 | 主圖在第 1 頁，附錄圖 1 在第 2 頁，依此類推 |

#### 步驟 3：產生 render_this.py 時的檢查清單

在產生 render_this.py 時，確保：

```
✓ 第 1 頁：主報告（包含主圖的繪製呼叫）
✓ 第 2 頁：附錄圖 1（如有）
✓ 第 3 頁：附錄圖 2（如有）
✓ 第 N 頁：附錄圖 N-1（如有）
✓ 最後 1-2 頁：術語詞彙表（格式見下方說明）
```

**術語表格式選項**：

| 條件 | 格式 | 說明 |
|------|------|------|
| glossary.md 有 10+ 術語，且前 6 個適合配圖 | **雙頁版本** | 第 N 頁：6 格有圖（2x3），第 N+1 頁：16 格純文字（4x4）|
| glossary.md 少於 10 個術語，或不適合配圖 | **單頁版本** | 第 N 頁：16 格純文字（4x4）|

**範例 1**：如果 diagrams.md 定義了 1 個主圖和 3 個附錄圖，且 glossary.md 有 14 個術語（雙頁術語表）：

```python
# 第 1 頁：主報告 + 主圖
slide1 = prs.slides.add_slide(...)
# ... 主報告內容 ...
draw_before_after_with_vertical_flow(...)  # 主圖

# 第 2 頁：附錄圖 1
slide2 = prs.slides.add_slide(...)
draw_flow(...)  # 附錄圖 1

# 第 3 頁：附錄圖 2
slide3 = prs.slides.add_slide(...)
draw_platform_compare(...)  # 附錄圖 2

# 第 4 頁：附錄圖 3
slide4 = prs.slides.add_slide(...)
draw_architecture(...)  # 附錄圖 3

# 第 5 頁：核心術語詞彙表（6 格有圖版本）
slide5 = prs.slides.add_slide(...)
core_glossary_terms = [
    {
        "term": "術語名稱",
        "desc": "白話解釋",
        "diagram_type": "flow",  # 可選：flow / before_after / timeline / icon
        "diagram_params": {...}
    },
    # ... 共 6 個核心術語
]
draw_glossary_page_with_diagrams(slide5, "核心術語詞彙表", core_glossary_terms)

# 第 6 頁：完整術語詞彙表（16 格純文字版本）
slide6 = prs.slides.add_slide(...)
all_glossary_terms = [
    {"term": "術語名稱", "desc": "白話解釋"},
    # ... 全部術語（可包含第 5 頁的 6 個）
]
draw_glossary_page_text_only(slide6, "完整術語詞彙表", all_glossary_terms)
```

**範例 2**：如果只有 8 個術語（單頁術語表）：

```python
# ... 附錄圖 ...

# 最後一頁：術語詞彙表（16 格純文字版本）
slide_last = prs.slides.add_slide(...)
draw_glossary_page_text_only(slide_last, "術語詞彙表", all_glossary_terms)
```

#### 步驟 4：產生附錄投影片的程式碼模板

對於每個附錄圖，產生對應的程式碼：

```python
# =========================================================================
# 第 {N} 頁：{圖表名稱}
# =========================================================================
slide{N} = prs.slides.add_slide(prs.slide_layouts[6])
set_current_slide({N-1})
add_background(slide{N}, prs)

# 標題
title_box = slide{N}.shapes.add_textbox(Inches(0.3), Inches(0.1), Inches(12.7), Inches(0.35))
tf = title_box.text_frame
p = tf.paragraphs[0]
p.text = "{圖表標題}"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = COLOR_TEXT
p.font.name = FONT_NAME
track_element("{圖表名稱} 標題", 0.3, 0.1, 12.7, 0.35, "text")

# 繪製圖表（根據類型調用對應函數）
{繪圖函數呼叫}
track_element("{圖表名稱} 圖表", ...)
```

#### 步驟 5：圖表類型對應函數表

根據 diagrams.md 中的「類型」欄位，調用對應的繪圖函數：

| diagrams.md 類型 | 呼叫函數 | 參數來源 |
|-----------------|---------|---------|
| `before_after`（垂直流程）| `draw_before_after_with_vertical_flow()` | 解析「SVG 生成指示」的節點列表 |
| `flow` | `draw_flow()` | 解析「SVG 生成指示」的節點序列 |
| `platform_compare` | `draw_platform_compare()` | 解析兩個平台的資訊 |
| `architecture` | `draw_architecture()` | 解析分層架構資訊 |

#### 步驟 6：錯誤處理

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

---

## 6.4 等待 Sub Agent 完成

Sub Agent 會自動執行以下任務：

1. ✅ 產生 render_this.py
2. ✅ 執行 render_this.py 產生 PPTX
3. ✅ 驗證圖表完整性（diagrams.md + technical_appendix.md）
4. ✅ 多輪迭代修正直到通過驗證
5. ✅ 產生演講稿文字檔（./output/script.txt）

**等待 Sub Agent 回傳結果**：
- Sub Agent 會回報「✅ Phase 6 完成」
- 或回報錯誤訊息（如果無法產生 PPTX）

---

## 6.5 驗證輸出檔案

Sub Agent 完成後，檢查以下檔案是否存在：

| 檔案 | 說明 |
|------|------|
| `./output/render_this.py` | Python 程式碼 |
| `./output/final.pptx` | ⭐ 最終 PPTX 檔案 |
| `./output/script.txt` | 演講稿文字檔 |

**如果 Sub Agent 失敗**：
- 讀取 Sub Agent 的錯誤訊息
- 可能需要手動檢查 ./output 目錄的內容
- 必要時可以重新呼叫 Sub Agent

---

## 6.6 完成

告知使用者：

```
✅ 報告產生完成！

輸出檔案：
📊 ./output/final.pptx（投影片，含主報告 + 技術附錄 + 術語解釋）
📝 ./output/script.txt（演講稿獨立檔案）
🐍 ./output/render_this.py（產生 PPTX 的 Python 程式碼）
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
