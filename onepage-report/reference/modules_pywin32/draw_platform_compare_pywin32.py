# -*- coding: utf-8 -*-
"""
平台對比圖繪製（pywin32 版本）

上下兩個平台並排，各有內部流程，用虛線標示差異。
"""

from ._colors_pywin32 import (
    COLOR_BLUE, COLOR_ORANGE, COLOR_GREEN, COLOR_GRAY, COLOR_GRAY_BG,
    COLOR_TEXT, COLOR_WHITE, FONT_NAME, hex_to_bgr
)
from ._shapes_pywin32 import (
    add_rounded_rect, add_textbox, add_arrow_line, add_label, add_panel
)
from .draw_flow_pywin32 import draw_flow


def draw_platform_compare(slide, left, top, width, height,
                          platform1_title, platform1_nodes,
                          platform2_title, platform2_nodes,
                          differences=None, summary=None):
    """
    繪製平台對比圖（上下並排）

    Args:
        slide: pywin32 Slide 物件
        left, top: 左上角位置（pt）
        width, height: 寬高（pt）
        platform1_title: 上方平台標題
        platform1_nodes: 上方平台流程節點
        platform2_title: 下方平台標題
        platform2_nodes: 下方平台流程節點
        differences: 差異列表（可選）
            [{"desc": "說明", "index1": 1, "index2": 1}, ...]
        summary: 總結列表（可選）

    Returns:
        dict: 建立的形狀
    """
    shapes = {}

    # 計算尺寸
    panel_gap = 20
    panel_height = (height - panel_gap) / 2

    # 上方平台
    add_panel(slide, left, top, width, panel_height,
             platform1_title, COLOR_BLUE, COLOR_GRAY_BG, header_height=22)

    flow_top1 = top + 26
    flow_height = panel_height - 34
    shapes["platform1_flow"] = draw_flow(
        slide, left + 8, flow_top1, width - 16, flow_height,
        platform1_nodes
    )

    # 下方平台
    platform2_top = top + panel_height + panel_gap
    add_panel(slide, left, platform2_top, width, panel_height,
             platform2_title, COLOR_BLUE, COLOR_GRAY_BG, header_height=22)

    flow_top2 = platform2_top + 26
    shapes["platform2_flow"] = draw_flow(
        slide, left + 8, flow_top2, width - 16, flow_height,
        platform2_nodes
    )

    # 差異標註（用虛線連接）
    if differences:
        mid_y = top + panel_height + panel_gap / 2
        for i, diff in enumerate(differences):
            # 在中間間隙區域顯示差異說明
            desc = diff.get("desc", "")
            if desc:
                add_label(slide, desc,
                         left + width / 2 - 80, mid_y - 6, 160, 12,
                         font_size=7, color=COLOR_ORANGE, align=2)

    return shapes
