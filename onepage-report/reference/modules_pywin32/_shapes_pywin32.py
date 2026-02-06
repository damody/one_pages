# -*- coding: utf-8 -*-
"""
pywin32 基本形狀繪製函數

此模組提供 pywin32 COM API 的形狀繪製包裝函數，
對應 python-pptx 的 shapes 模組功能。

MsoAutoShapeType 常用值：
- 1: msoShapeRectangle 矩形
- 5: msoShapeRoundedRectangle 圓角矩形
- 33: msoShapeRightArrow 向右箭頭
- 36: msoShapeDownArrow 向下箭頭
- 6: msoShapeOval 橢圓

單位：pywin32 使用 pt (points)，1 inch = 72 pt
"""

from ._colors_pywin32 import (
    COLOR_TEXT, COLOR_WHITE, COLOR_GRAY_LIGHT,
    FONT_NAME, get_text_color
)


# =============================================================================
# 線條與填充設定
# =============================================================================

def set_line(shape, color=None, weight=1.25, dash=None, visible=True):
    """
    設定形狀邊框

    Args:
        shape: pywin32 Shape 物件
        color: 線條顏色（BGR 格式），None 表示不設定
        weight: 線條粗細（pt）
        dash: 虛線樣式（0=實線, 1=方形點, 2=圓形點, 3=短虛線, 4=虛線）
        visible: 是否顯示邊框
    """
    if not visible:
        shape.Line.Visible = False
        return

    if color is not None:
        shape.Line.ForeColor.RGB = color
    shape.Line.Weight = weight
    if dash is not None:
        shape.Line.DashStyle = dash


def set_fill(shape, color=None):
    """
    設定形狀填充

    Args:
        shape: pywin32 Shape 物件
        color: 填充顏色（BGR 格式），None 表示透明
    """
    if color is None:
        shape.Fill.Visible = False
    else:
        shape.Fill.ForeColor.RGB = color
        shape.Fill.Solid()


# =============================================================================
# 基本形狀
# =============================================================================

def add_rect(slide, left, top, width, height,
             line_color=None, fill_color=None, weight=1.25, dash=None):
    """
    新增矩形

    Args:
        slide: pywin32 Slide 物件
        left, top: 左上角位置（pt）
        width, height: 寬高（pt）
        line_color: 邊框顏色（BGR）
        fill_color: 填充顏色（BGR），None 為透明
        weight: 邊框粗細（pt）
        dash: 虛線樣式

    Returns:
        Shape 物件
    """
    # msoShapeRectangle = 1
    shape = slide.Shapes.AddShape(1, left, top, width, height)
    set_line(shape, line_color, weight, dash, visible=(line_color is not None))
    set_fill(shape, fill_color)
    return shape


def add_rounded_rect(slide, left, top, width, height,
                     line_color=None, fill_color=None, weight=1.25, dash=None,
                     corner_radius=0.1):
    """
    新增圓角矩形

    Args:
        slide: pywin32 Slide 物件
        left, top: 左上角位置（pt）
        width, height: 寬高（pt）
        line_color: 邊框顏色（BGR）
        fill_color: 填充顏色（BGR），None 為透明
        weight: 邊框粗細（pt）
        dash: 虛線樣式
        corner_radius: 圓角半徑比例 (0.0-1.0)

    Returns:
        Shape 物件
    """
    # msoShapeRoundedRectangle = 5
    shape = slide.Shapes.AddShape(5, left, top, width, height)
    set_line(shape, line_color, weight, dash, visible=(line_color is not None))
    set_fill(shape, fill_color)
    # 設定圓角程度（0.0 = 直角, 1.0 = 最圓）
    try:
        shape.Adjustments.Item[1] = corner_radius
    except:
        pass  # 某些形狀可能不支援調整
    return shape


def add_oval(slide, left, top, width, height,
             line_color=None, fill_color=None, weight=1.25):
    """
    新增橢圓/圓形

    Args:
        slide: pywin32 Slide 物件
        left, top: 左上角位置（pt）
        width, height: 寬高（pt，相等時為圓形）
        line_color: 邊框顏色（BGR）
        fill_color: 填充顏色（BGR）

    Returns:
        Shape 物件
    """
    # msoShapeOval = 6
    shape = slide.Shapes.AddShape(6, left, top, width, height)
    set_line(shape, line_color, weight, visible=(line_color is not None))
    set_fill(shape, fill_color)
    return shape


# =============================================================================
# 箭頭
# =============================================================================

def add_arrow_line(slide, x1, y1, x2, y2,
                   line_color=None, weight=1.25, dash=None,
                   start_arrow=False, end_arrow=True):
    """
    新增箭頭線

    Args:
        slide: pywin32 Slide 物件
        x1, y1: 起點（pt）
        x2, y2: 終點（pt）
        line_color: 線條顏色（BGR）
        weight: 線條粗細（pt）
        dash: 虛線樣式
        start_arrow: 起點是否有箭頭
        end_arrow: 終點是否有箭頭

    Returns:
        Shape 物件
    """
    line = slide.Shapes.AddLine(x1, y1, x2, y2)
    set_line(line, line_color, weight, dash)

    # msoArrowheadTriangle = 3
    if end_arrow:
        line.Line.EndArrowheadStyle = 3
    if start_arrow:
        line.Line.BeginArrowheadStyle = 3

    return line


_ARROW_SHAPES = {"right": 33, "left": 34, "up": 35, "down": 36}


def add_arrow(slide, left, top, width, height, fill_color, direction="right"):
    """
    新增箭頭形狀

    Args:
        slide: pywin32 Slide 物件
        left, top: 左上角位置（pt）
        width, height: 寬高（pt）
        fill_color: 填充顏色（BGR）
        direction: 方向（right/left/up/down）

    Returns:
        Shape 物件
    """
    shape = slide.Shapes.AddShape(_ARROW_SHAPES[direction], left, top, width, height)
    set_fill(shape, fill_color)
    shape.Line.Visible = False
    return shape


def add_right_arrow(slide, left, top, width, height, fill_color):
    return add_arrow(slide, left, top, width, height, fill_color, "right")


def add_down_arrow(slide, left, top, width, height, fill_color):
    return add_arrow(slide, left, top, width, height, fill_color, "down")


def add_left_arrow(slide, left, top, width, height, fill_color):
    return add_arrow(slide, left, top, width, height, fill_color, "left")


def add_up_arrow(slide, left, top, width, height, fill_color):
    return add_arrow(slide, left, top, width, height, fill_color, "up")


# =============================================================================
# 文字框
# =============================================================================

def add_textbox(slide, text, left, top, width, height,
                font_size=12, bold=False, italic=False,
                color=None, font_name=None,
                align=1, valign=1,
                margin_left=6, margin_right=6,
                margin_top=3, margin_bottom=3):
    """
    新增文字框

    Args:
        slide: pywin32 Slide 物件
        text: 文字內容
        left, top: 左上角位置（pt）
        width, height: 寬高（pt）
        font_size: 字體大小
        bold: 是否粗體
        italic: 是否斜體
        color: 文字顏色（BGR），None 使用預設深灰
        font_name: 字體名稱，None 使用微軟正黑體
        align: 水平對齊（1=左, 2=中, 3=右）
        valign: 垂直對齊（1=上, 2=中, 3=下）
        margin_*: 內邊距（pt）

    Returns:
        Shape 物件
    """
    # msoTextOrientationHorizontal = 1
    box = slide.Shapes.AddTextbox(1, left, top, width, height)
    tf = box.TextFrame

    # 文字內容
    tf.TextRange.Text = text

    # 字體設定
    tf.TextRange.Font.Size = font_size
    tf.TextRange.Font.Bold = -1 if bold else 0
    tf.TextRange.Font.Italic = -1 if italic else 0
    tf.TextRange.Font.Color.RGB = color if color is not None else COLOR_TEXT
    tf.TextRange.Font.Name = font_name if font_name is not None else FONT_NAME

    # 對齊
    tf.TextRange.ParagraphFormat.Alignment = align

    # 內邊距
    tf.MarginLeft = margin_left
    tf.MarginRight = margin_right
    tf.MarginTop = margin_top
    tf.MarginBottom = margin_bottom

    # 自動換行
    tf.WordWrap = -1  # True

    return box


def add_label(slide, text, left, top, width, height,
              font_size=11, color=None, bold=False, align=1):
    """
    新增標籤文字（簡化版 textbox）

    Args:
        slide: pywin32 Slide 物件
        text: 文字內容
        left, top: 左上角位置（pt）
        width, height: 寬高（pt）
        font_size: 字體大小
        color: 文字顏色（BGR）
        bold: 是否粗體
        align: 對齊方式

    Returns:
        Shape 物件
    """
    return add_textbox(slide, text, left, top, width, height,
                       font_size=font_size, bold=bold, color=color, align=align)


# =============================================================================
# 複合形狀
# =============================================================================

def add_panel(slide, left, top, width, height,
              title, border_color, fill_color=None,
              header_height=28, title_size=14):
    """
    新增面板（標題+內容區）

    Args:
        slide: pywin32 Slide 物件
        left, top: 左上角位置（pt）
        width, height: 寬高（pt）
        title: 標題文字
        border_color: 邊框顏色（BGR）
        fill_color: 填充顏色（BGR）
        header_height: 標題區高度（pt）
        title_size: 標題字體大小

    Returns:
        Shape 物件（面板矩形）
    """
    panel = add_rect(slide, left, top, width, height,
                     border_color, fill_color, weight=1.5)
    add_textbox(slide, title, left + 6, top + 4,
                width - 12, header_height - 8,
                font_size=title_size, bold=True, color=border_color, align=1)
    return panel


def add_content_box(slide, left, top, width, height,
                    title, body_lines,
                    line_color=None, fill_color=None,
                    title_size=12, body_size=10, dash=None):
    """
    新增內容方塊（標題+內容）

    Args:
        slide: pywin32 Slide 物件
        left, top: 左上角位置（pt）
        width, height: 寬高（pt）
        title: 標題文字
        body_lines: 內容行列表
        line_color: 邊框顏色（BGR）
        fill_color: 填充顏色（BGR）
        title_size: 標題字體大小
        body_size: 內容字體大小
        dash: 虛線樣式

    Returns:
        Shape 物件（矩形）
    """
    rect = add_rect(slide, left, top, width, height,
                    line_color, fill_color, weight=1.25, dash=dash)

    # 標題
    add_textbox(slide, title, left + 6, top + 4,
                width - 12, 18,
                font_size=title_size, bold=True, color=line_color, align=1)

    # 內容
    body_text = "\n".join(body_lines) if body_lines else ""
    add_textbox(slide, body_text, left + 6, top + 24,
                width - 12, height - 28,
                font_size=body_size, bold=False, color=COLOR_TEXT, align=1)

    return rect


# =============================================================================
# 背景
# =============================================================================

def add_background(slide, slide_width, slide_height, bg_color):
    """
    新增投影片背景

    Args:
        slide: pywin32 Slide 物件
        slide_width: 投影片寬度（pt）
        slide_height: 投影片高度（pt）
        bg_color: 背景顏色（BGR）

    Returns:
        Shape 物件
    """
    bg = add_rect(slide, 0, 0, slide_width, slide_height)
    set_fill(bg, bg_color)
    bg.Line.Visible = False
    return bg


def add_slide_title(slide, text, left=30, top=10, width=900, height=30,
                    font_size=18, bold=True):
    """
    新增投影片標題

    Args:
        slide: pywin32 Slide 物件
        text: 標題文字
        left, top: 位置（pt）
        width, height: 尺寸（pt）
        font_size: 字體大小
        bold: 是否粗體

    Returns:
        Shape 物件
    """
    return add_textbox(slide, text, left, top, width, height,
                       font_size=font_size, bold=bold, color=COLOR_TEXT, align=1)


# =============================================================================
# 單位轉換（相容 python-pptx 風格）
# =============================================================================

def inches_to_pt(inches):
    """將英吋轉換為 pt"""
    return inches * 72


def pt_to_inches(pt):
    """將 pt 轉換為英吋"""
    return pt / 72


def cm_to_pt(cm):
    """將公分轉換為 pt"""
    return cm * 28.3465


def pt_to_cm(pt):
    """將 pt 轉換為公分"""
    return pt / 28.3465


# =============================================================================
# 測試
# =============================================================================

if __name__ == "__main__":
    print("pywin32 形狀模組測試")
    print(f"1 inch = {inches_to_pt(1)} pt")
    print(f"72 pt = {pt_to_inches(72)} inch")
    print(f"1 cm = {cm_to_pt(1)} pt")
