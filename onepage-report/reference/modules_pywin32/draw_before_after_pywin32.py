# -*- coding: utf-8 -*-
"""
前後對比圖繪製（pywin32 版本）

繪製改善前/後對比圖，支援：
- 簡單版：左右項目列表
- 詳細版：左右各帶內部流程節點
- 底部對比表格
"""

from ._colors_pywin32 import (
    COLOR_RED, COLOR_GREEN, COLOR_BLUE, COLOR_ORANGE,
    COLOR_WHITE, COLOR_TEXT, COLOR_GRAY, COLOR_GRAY_BG, COLOR_GRAY_LIGHT,
    FONT_NAME, hex_to_bgr, get_text_color
)
from ._shapes_pywin32 import (
    add_rounded_rect, add_textbox, add_right_arrow, add_down_arrow,
    add_arrow_line, add_label, add_rect, add_panel
)
from .draw_flow_pywin32 import draw_flow, draw_flow_vertical, should_use_vertical_flow


# =============================================================================
# 簡單版前後對比圖
# =============================================================================

def draw_before_after(slide, left, top, width, height,
                      before_title, before_items,
                      after_title, after_items,
                      center_label=None):
    """
    繪製簡單版前後對比圖（項目列表）

    Args:
        slide: pywin32 Slide 物件
        left, top: 左上角位置（pt）
        width, height: 寬高（pt）
        before_title: 改善前標題
        before_items: 改善前項目列表
        after_title: 改善後標題
        after_items: 改善後項目列表
        center_label: 中間箭頭標籤

    Returns:
        tuple: (左側面板, 右側面板)
    """
    # 計算尺寸
    box_width = (width - 30) / 2  # 中間留 30pt 給箭頭
    center_x = left + width / 2

    # 左側區塊（改善前）- 紅色
    left_panel = add_rounded_rect(slide, left, top, box_width, height,
                                  line_color=COLOR_RED, fill_color=COLOR_GRAY_BG,
                                  weight=2)

    # 左側標題
    add_textbox(slide, before_title,
               left + 8, top + 8, box_width - 16, 20,
               font_size=11, bold=True, color=COLOR_RED)

    # 左側內容
    content_lines = [f"• {item}" for item in before_items]
    content_text = "\n".join(content_lines)
    add_textbox(slide, content_text,
               left + 8, top + 32, box_width - 16, height - 40,
               font_size=8, color=COLOR_TEXT)

    # 右側區塊（改善後）- 綠色
    right_left = left + box_width + 30
    right_panel = add_rounded_rect(slide, right_left, top, box_width, height,
                                   line_color=COLOR_GREEN, fill_color=COLOR_GRAY_BG,
                                   weight=2)

    # 右側標題
    add_textbox(slide, after_title,
               right_left + 8, top + 8, box_width - 16, 20,
               font_size=11, bold=True, color=COLOR_GREEN)

    # 右側內容
    content_lines = [f"• {item}" for item in after_items]
    content_text = "\n".join(content_lines)
    add_textbox(slide, content_text,
               right_left + 8, top + 32, box_width - 16, height - 40,
               font_size=8, color=COLOR_TEXT)

    # 中間箭頭
    arrow_y = top + height / 2 - 10
    add_right_arrow(slide, center_x - 10, arrow_y, 20, 20, COLOR_BLUE)

    # 中間標籤
    if center_label:
        add_label(slide, center_label,
                 center_x - 40, arrow_y + 24, 80, 16,
                 font_size=8, color=COLOR_BLUE, bold=True, align=2)

    return left_panel, right_panel


# =============================================================================
# 詳細版前後對比圖（帶內部流程）
# =============================================================================

def draw_before_after_with_flow(slide, left, top, width, height,
                                before_title, before_flow_nodes,
                                after_title, after_flow_nodes,
                                before_arrow_labels=None,
                                after_arrow_labels=None,
                                center_arrow_label=None,
                                bottom_table=None):
    """
    繪製詳細版前後對比圖（帶內部流程節點）

    Args:
        slide: pywin32 Slide 物件
        left, top: 左上角位置（pt）
        width, height: 寬高（pt）
        before_title: 改善前標題
        before_flow_nodes: 改善前流程節點列表，每個節點：
            {"title": "標題", "desc": "說明", "color": BGR, "highlight": bool}
        after_title: 改善後標題
        after_flow_nodes: 改善後流程節點列表
        before_arrow_labels: 改善前箭頭標籤列表
        after_arrow_labels: 改善後箭頭標籤列表
        center_arrow_label: 中間箭頭標籤
        bottom_table: 底部對比表格，格式：
            {"headers": [...], "rows": [[...], [...]]}

    Returns:
        dict: 包含建立的形狀
    """
    shapes = {}

    # 計算尺寸
    panel_gap = 40  # 中間間距
    box_width = (width - panel_gap) / 2

    # 預留底部表格空間
    content_height = height
    if bottom_table:
        table_height = 60 + len(bottom_table.get("rows", [])) * 20
        content_height = height - table_height - 10

    # 根據可用空間動態調整 header 和 padding
    if content_height < 80:
        header_height = 16  # 極小空間使用更小的 header
        padding = 8
    else:
        header_height = 24
        padding = 16
    flow_height = max(20, content_height - header_height - padding)  # 最小 20pt

    # --- 左側面板（改善前）---
    left_panel = add_rounded_rect(slide, left, top, box_width, content_height,
                                  line_color=COLOR_RED, fill_color=COLOR_WHITE,
                                  weight=2)
    shapes["left_panel"] = left_panel

    # 左側標題
    add_textbox(slide, before_title,
               left + 8, top + 4, box_width - 16, header_height,
               font_size=11, bold=True, color=COLOR_RED)

    # 判斷使用橫向還是縱向流程
    flow_left = left + 8
    flow_top = top + header_height + 8
    flow_width = box_width - 16

    before_vertical, _ = should_use_vertical_flow(before_flow_nodes, flow_width)
    after_vertical, _ = should_use_vertical_flow(after_flow_nodes, flow_width)

    # 保持一致性：如果任一側需要縱向，則兩側都用縱向
    use_vertical = before_vertical or after_vertical

    # 左側流程
    if use_vertical:
        shapes["before_flow"] = draw_flow_vertical(
            slide, flow_left, flow_top, flow_width, flow_height,
            before_flow_nodes, before_arrow_labels, COLOR_RED
        )
    else:
        shapes["before_flow"] = draw_flow(
            slide, flow_left, flow_top, flow_width, flow_height,
            before_flow_nodes, before_arrow_labels, COLOR_RED
        )

    # --- 右側面板（改善後）---
    right_left = left + box_width + panel_gap
    right_panel = add_rounded_rect(slide, right_left, top, box_width, content_height,
                                   line_color=COLOR_GREEN, fill_color=COLOR_WHITE,
                                   weight=2)
    shapes["right_panel"] = right_panel

    # 右側標題
    add_textbox(slide, after_title,
               right_left + 8, top + 4, box_width - 16, header_height,
               font_size=11, bold=True, color=COLOR_GREEN)

    # 右側流程
    flow_left_r = right_left + 8
    if use_vertical:
        shapes["after_flow"] = draw_flow_vertical(
            slide, flow_left_r, flow_top, flow_width, flow_height,
            after_flow_nodes, after_arrow_labels, COLOR_GREEN
        )
    else:
        shapes["after_flow"] = draw_flow(
            slide, flow_left_r, flow_top, flow_width, flow_height,
            after_flow_nodes, after_arrow_labels, COLOR_GREEN
        )

    # --- 中間箭頭 ---
    center_x = left + box_width + panel_gap / 2
    arrow_y = top + content_height / 2 - 12

    # 虛線連接箭頭
    add_arrow_line(slide,
                  left + box_width, arrow_y + 12,
                  right_left, arrow_y + 12,
                  COLOR_BLUE, weight=1.5, dash=3)

    # 箭頭標籤
    if center_arrow_label:
        add_label(slide, center_arrow_label,
                 center_x - 35, arrow_y - 8, 70, 16,
                 font_size=8, color=COLOR_BLUE, bold=True, align=2)

    # --- 底部對比表格 ---
    if bottom_table:
        table_top = top + content_height + 10
        table_height = height - content_height - 10
        _draw_comparison_table(slide, left, table_top, width, table_height,
                              bottom_table)

    return shapes


# =============================================================================
# 對比表格
# =============================================================================

def _draw_comparison_table(slide, left, top, width, height, table_data):
    """
    繪製對比表格

    Args:
        slide: pywin32 Slide 物件
        left, top: 左上角位置（pt）
        width, height: 寬高（pt）
        table_data: {"headers": [...], "rows": [[...], [...]]}
    """
    headers = table_data.get("headers", [])
    rows = table_data.get("rows", [])

    if not headers or not rows:
        return

    col_count = len(headers)
    row_count = len(rows) + 1  # +1 for header

    col_width = width / col_count
    row_height = height / row_count

    # 表頭
    for i, header in enumerate(headers):
        x = left + i * col_width
        add_rect(slide, x, top, col_width, row_height,
                line_color=COLOR_GRAY_LIGHT, fill_color=COLOR_GRAY_BG)
        add_textbox(slide, header,
                   x + 4, top + 2, col_width - 8, row_height - 4,
                   font_size=8, bold=True, color=COLOR_TEXT, align=2)

    # 資料列
    for row_idx, row in enumerate(rows):
        y = top + (row_idx + 1) * row_height
        for col_idx, cell in enumerate(row):
            x = left + col_idx * col_width

            # 決定背景色
            fill_color = COLOR_WHITE

            add_rect(slide, x, y, col_width, row_height,
                    line_color=COLOR_GRAY_LIGHT, fill_color=fill_color)
            add_textbox(slide, str(cell),
                       x + 4, y + 2, col_width - 8, row_height - 4,
                       font_size=7, color=COLOR_TEXT, align=2)


# =============================================================================
# 帶垂直流程的前後對比（from generate_diagrams1_pptx.py）
# =============================================================================

def draw_before_after_with_vertical_flow(slide, left, top, width, height,
                                         before_title, before_flow_nodes,
                                         after_title, after_flow_nodes,
                                         before_arrow_labels=None,
                                         after_arrow_labels=None,
                                         center_arrow_label=None,
                                         bottom_table=None,
                                         palette=None):
    """
    繪製帶垂直內部流程的前後對比圖（強制縱向）

    這是 draw_before_after_with_flow 的變體，強制使用縱向流程。

    Args:
        （同 draw_before_after_with_flow）
        palette: 調色板字典（可選）

    Returns:
        dict: 包含建立的形狀
    """
    # 設定預設調色板
    if palette is None:
        palette = {
            "danger": {"stroke": COLOR_RED, "fill": COLOR_GRAY_BG},
            "ok": {"stroke": COLOR_GREEN, "fill": COLOR_GRAY_BG},
        }

    shapes = {}

    # 計算尺寸
    panel_gap = 40
    box_width = (width - panel_gap) / 2

    # 預留底部表格空間
    content_height = height
    if bottom_table:
        table_height = 60 + len(bottom_table.get("rows", [])) * 20
        content_height = height - table_height - 10

    header_height = 28
    flow_height = content_height - header_height - 16

    # --- 左側面板（改善前）---
    add_panel(slide, left, top, box_width, content_height,
             before_title,
             palette["danger"]["stroke"],
             palette["danger"]["fill"],
             header_height)

    # 左側流程
    flow_left = left + 16
    flow_top = top + header_height + 8
    flow_width = box_width - 32

    shapes["before_flow"] = draw_flow_vertical(
        slide, flow_left, flow_top, flow_width, flow_height,
        before_flow_nodes, before_arrow_labels
    )

    # --- 右側面板（改善後）---
    right_left = left + box_width + panel_gap
    add_panel(slide, right_left, top, box_width, content_height,
             after_title,
             palette["ok"]["stroke"],
             palette["ok"]["fill"],
             header_height)

    # 右側流程
    flow_left_r = right_left + 16

    shapes["after_flow"] = draw_flow_vertical(
        slide, flow_left_r, flow_top, flow_width, flow_height,
        after_flow_nodes, after_arrow_labels
    )

    # --- 中間箭頭 ---
    center_x = left + box_width + panel_gap / 2
    arrow_y = top + content_height / 2

    add_arrow_line(slide,
                  left + box_width + 10, arrow_y,
                  right_left - 10, arrow_y,
                  COLOR_BLUE, weight=1.5, dash=2)

    if center_arrow_label:
        add_label(slide, center_arrow_label,
                 center_x - 50, arrow_y - 20, 100, 16,
                 font_size=10, color=COLOR_BLUE, bold=True, align=2)

    # --- 底部對比表格 ---
    if bottom_table:
        table_top = top + content_height + 10
        table_height = height - content_height - 10
        _draw_comparison_table(slide, left, table_top, width, table_height,
                              bottom_table)

    return shapes
