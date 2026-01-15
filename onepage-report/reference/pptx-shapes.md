# PPTX Shapes 繪製規範

使用 python-pptx 內建的 shapes API 直接在投影片上繪製圖表。

## 優點

- 產生的圖表可直接在 PowerPoint 中編輯
- 不需要 cairosvg 依賴
- 避免 emoji 無法渲染的問題
- 更好的跨平台相容性

---

## ⭐ 完整範例參考

**最重要**：所有 draw 函數的完整實作都在 `render_example.py` 中。

```
Read {skill_dir}/reference/render_example.py
```

該檔案包含經過驗證的完整函數：

| 函數名稱 | 用途 | 行數 |
|----------|------|------|
| `draw_before_after_with_vertical_flow()` | 詳細版前後對比圖（垂直內部流程） | 262-526 |
| `draw_flow()` | 橫向流程圖（支援時間標籤） | 532-598 |
| `draw_architecture()` | 分層架構圖（支援高亮和元件） | 600-656 |
| `draw_platform_compare()` | 上下平台對比圖 | 659-740 |
| `draw_glossary_card()` | 單一術語卡片 | 746-779 |
| `draw_glossary_page()` | 術語頁面（4x4 格局） | 782-809 |

**使用方式**：產生 render_this.py 時，直接從 render_example.py 複製完整函數實作。

---

## 顏色定義

```python
from pptx.dml.color import RGBColor

# 標準顏色
COLOR_RED = RGBColor(244, 67, 54)      # #F44336 - 改善前/問題/負面
COLOR_GREEN = RGBColor(76, 175, 80)    # #4CAF50 - 改善後/成功/正面
COLOR_BLUE = RGBColor(33, 150, 243)    # #2196F3 - 流程/節點/中性
COLOR_GRAY_BG = RGBColor(245, 245, 245)  # #F5F5F5 - 區塊背景
COLOR_GRAY_BORDER = RGBColor(189, 189, 189)  # #BDBDBD - 邊框
COLOR_TEXT = RGBColor(51, 51, 51)      # #333333 - 文字
COLOR_WHITE = RGBColor(255, 255, 255)  # #FFFFFF - 白色文字
```

---

## 圖表類型與實作對應

| 圖表類型 | Shapes 實作方式 |
|----------|----------------|
| `before_after` | 左右兩個圓角矩形 + 中間箭頭 + 內部文字框 |
| `platform_compare` | 上下兩個圓角矩形 + 內部流程節點 |
| `flow` | 橫向圓角矩形序列 + 連接箭頭 |
| `timeline` | 水平線 + 階段區塊 + 時間標註 |
| `architecture` | 分層矩形 + 連接線 + 標籤文字 |

---

## 繪製函數範例

### 前後對比圖

```python
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN

def draw_before_after(slide, left, top, width, height, before_title, before_items, after_title, after_items):
    """
    繪製前後對比圖

    Args:
        slide: 投影片物件
        left, top: 左上角位置（吋）
        width, height: 寬高（吋）
        before_title: 左側標題（如「改善前」）
        before_items: 左側項目列表
        after_title: 右側標題（如「改善後」）
        after_items: 右側項目列表
    """
    box_width = (width - 0.4) / 2  # 中間留 0.4 吋

    # 左側區塊（改善前）
    before_box = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(left), Inches(top),
        Inches(box_width), Inches(height)
    )
    before_box.fill.solid()
    before_box.fill.fore_color.rgb = COLOR_GRAY_BG
    before_box.line.color.rgb = COLOR_RED
    before_box.line.width = Pt(2)

    # 左側標題
    before_title_box = slide.shapes.add_textbox(
        Inches(left + 0.1), Inches(top + 0.1),
        Inches(box_width - 0.2), Inches(0.3)
    )
    tf = before_title_box.text_frame
    p = tf.paragraphs[0]
    p.text = before_title
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_RED

    # 左側內容
    before_content = slide.shapes.add_textbox(
        Inches(left + 0.1), Inches(top + 0.45),
        Inches(box_width - 0.2), Inches(height - 0.55)
    )
    tf = before_content.text_frame
    tf.word_wrap = True
    for i, item in enumerate(before_items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"• {item}"
        p.font.size = Pt(10)
        p.font.color.rgb = COLOR_TEXT

    # 右側區塊（改善後）
    after_box = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(left + box_width + 0.4), Inches(top),
        Inches(box_width), Inches(height)
    )
    after_box.fill.solid()
    after_box.fill.fore_color.rgb = COLOR_GRAY_BG
    after_box.line.color.rgb = COLOR_GREEN
    after_box.line.width = Pt(2)

    # 右側標題和內容（類似左側）
    # ...

    # 中間箭頭
    arrow = slide.shapes.add_shape(
        MSO_SHAPE.RIGHT_ARROW,
        Inches(left + box_width + 0.1), Inches(top + height/2 - 0.15),
        Inches(0.2), Inches(0.3)
    )
    arrow.fill.solid()
    arrow.fill.fore_color.rgb = COLOR_BLUE
    arrow.line.fill.background()
```

---

### 流程圖

```python
def draw_flow(slide, left, top, width, height, nodes):
    """
    繪製橫向流程圖

    Args:
        slide: 投影片物件
        left, top: 左上角位置（吋）
        width, height: 寬高（吋）
        nodes: 節點列表，每個元素是 {"title": "...", "desc": "..."} 或純字串
    """
    node_count = len(nodes)
    gap = 0.15  # 節點間距（箭頭空間）
    arrow_width = 0.12
    node_width = (width - gap * (node_count - 1)) / node_count

    for i, node in enumerate(nodes):
        x = left + i * (node_width + gap)

        # 解析節點內容
        if isinstance(node, dict):
            title = node.get("title", "")
            desc = node.get("desc", "")
        else:
            title = str(node)
            desc = ""

        # 節點矩形
        shape = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(x), Inches(top),
            Inches(node_width), Inches(height)
        )
        shape.fill.solid()
        shape.fill.fore_color.rgb = COLOR_BLUE
        shape.line.fill.background()

        # 節點文字
        tf = shape.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = COLOR_WHITE
        p.alignment = PP_ALIGN.CENTER

        if desc:
            p2 = tf.add_paragraph()
            p2.text = desc
            p2.font.size = Pt(8)
            p2.font.color.rgb = COLOR_WHITE
            p2.alignment = PP_ALIGN.CENTER

        # 箭頭（最後一個不加）
        if i < node_count - 1:
            arrow = slide.shapes.add_shape(
                MSO_SHAPE.RIGHT_ARROW,
                Inches(x + node_width + 0.02), Inches(top + height/2 - 0.08),
                Inches(arrow_width), Inches(0.16)
            )
            arrow.fill.solid()
            arrow.fill.fore_color.rgb = RGBColor(150, 150, 150)
            arrow.line.fill.background()
```

---

### 平台對比圖

```python
def draw_platform_compare(slide, left, top, width, height, platform_a, platform_b):
    """
    繪製上下平台對比圖

    Args:
        platform_a: {"name": "PC", "color": COLOR_BLUE, "items": [...]}
        platform_b: {"name": "手機", "color": COLOR_GREEN, "items": [...]}
    """
    box_height = (height - 0.3) / 2  # 中間留 0.3 吋

    for i, platform in enumerate([platform_a, platform_b]):
        y = top if i == 0 else top + box_height + 0.3
        color = platform.get("color", COLOR_BLUE)

        # 平台區塊
        box = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(left), Inches(y),
            Inches(width), Inches(box_height)
        )
        box.fill.solid()
        box.fill.fore_color.rgb = COLOR_GRAY_BG
        box.line.color.rgb = color
        box.line.width = Pt(2)

        # 平台標題和內容
        # ...
```

---

### 時間軸圖

```python
def draw_timeline(slide, left, top, width, height, stages):
    """
    繪製時間軸圖

    Args:
        stages: 階段列表，每個元素是 {"name": "...", "time": "...ms", "color": COLOR_*}
    """
    line_y = top + height * 0.6
    stage_count = len(stages)
    stage_width = width / stage_count

    # 水平主軸線
    line = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(left), Inches(line_y),
        Inches(width), Inches(0.03)
    )
    line.fill.solid()
    line.fill.fore_color.rgb = RGBColor(100, 100, 100)
    line.line.fill.background()

    for i, stage in enumerate(stages):
        x = left + i * stage_width
        color = stage.get("color", COLOR_BLUE)

        # 階段區塊
        box = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(x + 0.05), Inches(top),
            Inches(stage_width - 0.1), Inches(height * 0.5)
        )
        box.fill.solid()
        box.fill.fore_color.rgb = color
        # ...
```

---

## diagrams.md 格式（pptx_shapes 專用）

當使用 pptx_shapes 時，diagrams.md 改用結構化參數格式：

```markdown
## 主圖表

- **類型**：before_after
- **說明**：Frame Queue 堆積問題與解決方案
- **位置**：left=0.3, top=2.5, width=6.0, height=2.5

### Shapes 參數

```json
{
  "before_title": "改善前：Frame Queue 堆積",
  "before_items": [
    "GPU 不知道遊戲目標幀率",
    "BufferQueue 堆積 2-3 幀"
  ],
  "after_title": "改善後：SDK 同步機制",
  "after_items": [
    "SDK 通知目標幀率",
    "延遲降低 81%"
  ]
}
```
```

---

## 使用範例

```python
# 主投影片上的前後對比圖
draw_before_after(
    slide=main_slide,
    left=0.3, top=2.5, width=6.0, height=2.5,
    before_title="改善前：Frame Queue 堆積",
    before_items=[
        "GPU 不知道遊戲目標幀率",
        "BufferQueue 堆積 2-3 幀",
        "延遲累積達 50-80ms"
    ],
    after_title="改善後：SDK 同步機制",
    after_items=[
        "SDK 通知目標幀率",
        "GPU 同步渲染節奏",
        "延遲降低 81%"
    ]
)

# 附錄的流程圖
draw_flow(
    slide=appendix_slide,
    left=0.5, top=1.5, width=12.0, height=0.8,
    nodes=[
        {"title": "觸控輸入", "desc": "5ms"},
        {"title": "遊戲處理", "desc": "16ms"},
        {"title": "GPU 渲染", "desc": "8ms"},
        {"title": "顯示輸出", "desc": "8ms"}
    ]
)
```

---

## 進階圖表函數（詳細版）

當 diagrams.md 的「SVG 生成指示」包含「內部流程」「橫向節點」「箭頭上標文字」等關鍵字時，必須使用以下進階函數。

### 詳細版前後對比圖（帶內部流程）

```python
def draw_before_after_with_flow(
    slide, left, top, width, height,
    before_title, before_flow_nodes, before_arrow_labels,
    after_title, after_flow_nodes, after_arrow_labels,
    center_arrow_label="導入方案", bottom_table=None
):
    """
    繪製帶內部流程圖的前後對比

    Args:
        before_flow_nodes: 左側內部流程節點列表，每個節點是 {
            "title": "節點標題",
            "desc": "說明文字",
            "time": "時間標籤（可選）",
            "color": 顏色,
            "highlight": True/False（是否用紅色虛線標示問題點）
        }
        before_arrow_labels: 左側箭頭上的文字標籤列表
        bottom_table: 底部對比表格 {
            "headers": ["指標", "改善前", "改善後", "說明"],
            "rows": [["堆積", "2-3幀", "0-1幀", "減少"], ...]
        }
    """
```

**Shapes 參數格式（詳細版）：**

```json
{
  "type": "before_after_with_flow",
  "before_title": "改善前：畫面堆積導致延遲",
  "before_flow_nodes": [
    {"title": "觸控輸入", "desc": "T=0", "color": "COLOR_BLUE"},
    {"title": "Frame Queue", "desc": "堆積 2-3 幀", "color": "COLOR_RED", "highlight": true},
    {"title": "GPU 畫圖", "desc": "等前面畫完", "color": "COLOR_BLUE"},
    {"title": "螢幕顯示", "desc": "過時畫面", "color": "COLOR_BLUE"}
  ],
  "before_arrow_labels": ["讀取輸入", "等前面畫完", "送去顯示"],
  "after_title": "改善後：精準同步即時反應",
  "after_flow_nodes": [
    {"title": "GPU 信號", "desc": "準備好了", "color": "COLOR_GREEN"},
    {"title": "觸控輸入", "desc": "最佳時機", "color": "COLOR_GREEN"},
    {"title": "GPU 畫圖", "desc": "立即畫", "color": "COLOR_GREEN"},
    {"title": "螢幕顯示", "desc": "最新畫面", "color": "COLOR_GREEN"}
  ],
  "after_arrow_labels": ["同步信號", "馬上讀取", "直接顯示"],
  "center_arrow_label": "導入 SDK",
  "bottom_table": {
    "headers": ["指標", "改善前", "改善後", "說明"],
    "rows": [
      ["Frame Queue 堆積", "2-3 幀", "0-1 幀", "排隊減少"],
      ["輸入-顯示同步", "不精準", "精準對齊", "玩家感覺更即時"]
    ]
  }
}
```

---

### 詳細版流程圖（支援箭頭標籤）

```python
def draw_flow_detailed(slide, left, top, width, height, nodes, arrow_labels=None, show_highlight=True):
    """
    繪製詳細版橫向流程圖

    Args:
        nodes: 節點列表，每個元素是 {
            "title": "節點標題",
            "desc": "說明文字",
            "time": "時間標籤（可選，會用淺黃色顯示）",
            "color": 顏色,
            "highlight": True/False（是否用紅色虛線框標示）
        }
        arrow_labels: 箭頭上的文字標籤列表（長度 = len(nodes)-1）
        show_highlight: 是否顯示高亮標記
    """
```

**Shapes 參數格式：**

```json
{
  "type": "flow_detailed",
  "nodes": [
    {"title": "觸控輸入", "desc": "5ms", "color": "COLOR_BLUE"},
    {"title": "Frame Queue", "desc": "等待中", "time": "+16~33ms", "highlight": true},
    {"title": "GPU 渲染", "desc": "8ms", "color": "COLOR_GREEN"},
    {"title": "顯示輸出", "desc": "即時", "color": "COLOR_ACCENT"}
  ],
  "arrow_labels": ["讀取", "排隊", "送出"]
}
```

---

### 平台對比圖（上下兩個流程）

```python
def draw_platform_compare(slide, left, top, width, height, platform_a, platform_b, differences=None):
    """
    繪製上下平台對比圖，每個平台內部有完整流程

    Args:
        platform_a: 上方平台 {
            "name": "PC 平台",
            "title": "AMD Anti-Lag 2 流程",
            "color": COLOR_BLUE,
            "flow_nodes": [...],
            "arrow_labels": [...],
            "summary": "效果：CS2 延遲降低 37%"
        }
        platform_b: 下方平台（同上格式）
        differences: 差異標註列表 [
            {"item": "輸入方式", "a": "滑鼠", "b": "觸控"},
            {"item": "同步方式", "a": "遊戲引擎內建", "b": "MAGT 框架"}
        ]
    """
```

**Shapes 參數格式：**

```json
{
  "type": "platform_compare",
  "platform_a": {
    "name": "PC 平台",
    "title": "AMD Anti-Lag 2 流程（已驗證有效）",
    "color": "COLOR_BLUE",
    "flow_nodes": [
      {"title": "滑鼠/鍵盤", "desc": "USB 1000Hz"},
      {"title": "遊戲引擎 SDK", "desc": "同步機制"},
      {"title": "獨立顯卡", "desc": "專門畫圖"},
      {"title": "螢幕", "desc": "直接輸出"}
    ],
    "arrow_labels": ["輸入", "同步", "輸出"],
    "summary": "效果：CS2 延遲降低 37%"
  },
  "platform_b": {
    "name": "手機平台",
    "title": "MTK Anti-Lag SDK 流程（提案）",
    "color": "COLOR_GREEN",
    "flow_nodes": [
      {"title": "觸控螢幕", "desc": "手指點擊"},
      {"title": "MAGT / SDK", "desc": "同步機制"},
      {"title": "SoC 整合 GPU", "desc": "省電考量"},
      {"title": "BufferQueue", "desc": "多一層"},
      {"title": "螢幕", "desc": "目標 5%+"}
    ],
    "arrow_labels": ["讀取", "同步", "渲染", "送出"],
    "summary": "目標：延遲降低 5%+"
  },
  "differences": [
    {"item": "輸入方式", "a": "滑鼠鍵盤", "b": "觸控螢幕"},
    {"item": "同步方式", "a": "遊戲引擎內建", "b": "MAGT 框架擴展"},
    {"item": "顯示路徑", "a": "GPU 直出", "b": "經過 BufferQueue"}
  ]
}
```

---

## 何時使用簡單版 vs 詳細版

| 情況 | 使用函數 |
|------|---------|
| diagrams.md 只列出項目點 | `draw_before_after()` |
| diagrams.md 有「內部流程」「橫向節點」 | `draw_before_after_with_flow()` |
| diagrams.md 只列出步驟名稱 | `draw_flow()` |
| diagrams.md 有「箭頭上標」「時間標籤」「問題標示」 | `draw_flow_detailed()` |
| diagrams.md 有「上下對比」「平台對比」 | `draw_platform_compare()` |
