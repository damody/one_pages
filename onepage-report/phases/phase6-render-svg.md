# Phase 6 附錄：SVG/PNG 渲染方式

> **使用條件：** 當 `LAYOUT_ENGINE = svg_png` 時載入此檔案
> **執行前請讀取：** `{skill_dir}/reference/svg-generation.md`

---

## SVG 圖表生成

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

## SVG 轉 PNG（透明背景）

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

## 嵌入 PPTX

將產生的 PNG 檔案嵌入投影片：

```python
from pptx import Presentation
from pptx.util import Inches

prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[6])

# 嵌入 PNG 圖片
slide.shapes.add_picture(
    './output/main_diagram.png',
    left=Inches(0.5),
    top=Inches(1.5),
    width=Inches(12.0)
)

prs.save('./output/final.pptx')
```

---

## 注意事項

- SVG 中的 emoji 可能無法正確轉換，建議使用文字替代
- cairosvg 需要安裝：`pip install cairosvg`
- 在 Windows 上可能需要額外安裝 GTK+ runtime
