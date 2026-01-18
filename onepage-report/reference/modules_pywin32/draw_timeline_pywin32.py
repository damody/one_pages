# -*- coding: utf-8 -*-
"""
時間軸圖繪製（pywin32 版本）

繪製水平時間軸，每個階段有時間和說明。
"""

from ._colors_pywin32 import (
    COLOR_PINK, COLOR_GREEN, COLOR_GRAY, COLOR_GRAY_BG, COLOR_GRAY_LIGHT,
    COLOR_RED, COLOR_TEXT, COLOR_WHITE, FONT_NAME, hex_to_bgr
)
from ._shapes_pywin32 import (
    add_rounded_rect, add_textbox, add_arrow_line, add_label, add_oval
)


def draw_timeline(slide, left, top, width, height, events, title=None):
    """
    繪製時間軸圖

    Args:
        slide: pywin32 Slide 物件
        left, top: 左上角位置（pt）
        width, height: 寬高（pt）
        events: 事件列表，每個事件：
            {
                "name": "事件名稱",
                "time": "T=0",
                "desc": "說明",
                "color": BGR (可選，預設灰色),
                "highlight": bool (可選，是否為瓶頸),
                "duration": "2ms" (可選，到下一節點的時間)
            }
        title: 圖表標題（可選）

    Returns:
        dict: 建立的形狀
    """
    shapes = {}

    # 標題
    title_height = 0
    if title:
        add_textbox(slide, title,
                   left, top, width, 24,
                   font_size=12, bold=True, color=COLOR_TEXT)
        title_height = 28

    # 時間軸區域
    timeline_top = top + title_height
    timeline_height = height - title_height

    # 計算節點間距
    n_events = len(events)
    if n_events == 0:
        return shapes

    # 左右留邊距
    margin_x = 50
    usable_width = width - 2 * margin_x

    if n_events == 1:
        spacing = 0
    else:
        spacing = usable_width / (n_events - 1)

    # 時間軸線 Y 位置（垂直置中偏上）
    axis_y = timeline_top + timeline_height * 0.45

    # 畫時間軸主線
    add_arrow_line(slide,
                  left + margin_x - 20, axis_y,
                  left + width - margin_x + 20, axis_y,
                  COLOR_GRAY, weight=2)

    # 繪製每個事件節點
    node_radius = 6
    for i, event in enumerate(events):
        x = left + margin_x + i * spacing

        # 節點顏色
        color = event.get("color", COLOR_GRAY)
        if i == 0:
            color = COLOR_PINK  # 起點
        elif i == n_events - 1:
            color = COLOR_GREEN  # 終點

        if event.get("highlight"):
            color = COLOR_RED  # 瓶頸

        # 畫節點圓圈
        add_oval(slide,
                x - node_radius, axis_y - node_radius,
                node_radius * 2, node_radius * 2,
                line_color=color, fill_color=COLOR_WHITE, weight=2)

        # 事件名稱（節點上方）
        name = event.get("name", "")
        add_textbox(slide, name,
                   x - 40, axis_y - 38, 80, 16,
                   font_size=8, bold=True, color=color, align=2)

        # 時間標註
        time_str = event.get("time", "")
        if time_str:
            add_textbox(slide, time_str,
                       x - 25, axis_y - 23, 50, 12,
                       font_size=7, color=COLOR_GRAY, align=2)

        # 說明（節點下方）
        desc = event.get("desc", "")
        if desc:
            add_textbox(slide, desc,
                       x - 45, axis_y + 12, 90, 30,
                       font_size=7, color=COLOR_TEXT, align=2)

        # 區段時間標籤（除了最後一個節點）
        if i < n_events - 1:
            next_x = left + margin_x + (i + 1) * spacing
            mid_x = (x + next_x) / 2

            duration = event.get("duration", "")
            if duration:
                label_color = COLOR_RED if event.get("highlight") else COLOR_GRAY
                add_label(slide, duration,
                         mid_x - 25, axis_y - 10, 50, 12,
                         font_size=7, color=label_color, align=2)

    return shapes
