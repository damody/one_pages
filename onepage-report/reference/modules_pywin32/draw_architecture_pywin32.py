# -*- coding: utf-8 -*-
"""
架構圖繪製（pywin32 版本）

分層架構圖，由上到下顯示各層及其模組。
"""

from ._colors_pywin32 import (
    COLOR_BLUE, COLOR_ORANGE, COLOR_GREEN, COLOR_GRAY, COLOR_GRAY_BG,
    COLOR_GRAY_LIGHT, COLOR_TEXT, COLOR_WHITE, FONT_NAME, hex_to_bgr
)
from ._shapes_pywin32 import (
    add_rounded_rect, add_textbox, add_arrow_line, add_label, add_rect
)


def draw_architecture(slide, left, top, width, height, layers, title=None):
    """
    繪製分層架構圖

    Args:
        slide: pywin32 Slide 物件
        left, top: 左上角位置（pt）
        width, height: 寬高（pt）
        layers: 層級列表，由上到下：
            [
                {
                    "name": "應用層",
                    "color": BGR (可選，預設淺灰),
                    "modules": [
                        {"name": "模組1", "highlight": False},
                        {"name": "模組2", "highlight": True}
                    ]
                },
                ...
            ]
        title: 圖表標題（可選）

    Returns:
        dict: 建立的形狀
    """
    shapes = {}

    # 標題
    title_height = 0
    if title:
        add_textbox(slide, title,
                   left, top, width, 20,
                   font_size=11, bold=True, color=COLOR_TEXT)
        title_height = 24

    # 計算每層高度
    content_top = top + title_height
    content_height = height - title_height

    n_layers = len(layers)
    if n_layers == 0:
        return shapes

    layer_gap = 8
    layer_height = (content_height - (n_layers - 1) * layer_gap) / n_layers

    for i, layer in enumerate(layers):
        layer_top = content_top + i * (layer_height + layer_gap)

        # 層級背景顏色
        layer_color = layer.get("color", COLOR_GRAY_BG)

        # 層級背景
        add_rounded_rect(slide, left, layer_top, width, layer_height,
                        line_color=COLOR_GRAY_LIGHT, fill_color=layer_color,
                        corner_radius=0.1)

        # 層級名稱
        add_textbox(slide, layer.get("name", ""),
                   left + 5, layer_top + 2, width - 10, 14,
                   font_size=9, bold=True, color=COLOR_TEXT)

        # 模組
        modules = layer.get("modules", [])
        if modules:
            n_modules = len(modules)
            module_area_width = width - 16
            module_width = min(90, (module_area_width / n_modules) - 8)
            module_height = layer_height - 22

            start_x = left + 8
            module_spacing = module_area_width / n_modules

            for j, module in enumerate(modules):
                module_x = start_x + j * module_spacing + (module_spacing - module_width) / 2
                module_y = layer_top + 18

                # 高亮模組用橙色邊框
                if module.get("highlight"):
                    line_color = COLOR_ORANGE
                    line_weight = 2
                else:
                    line_color = COLOR_GRAY
                    line_weight = 1

                add_rounded_rect(slide, module_x, module_y,
                                module_width, module_height,
                                line_color=line_color, fill_color=COLOR_WHITE,
                                weight=line_weight, corner_radius=0.15)

                # 模組名稱
                add_textbox(slide, module.get("name", ""),
                           module_x + 3, module_y + 2,
                           module_width - 6, module_height - 4,
                           font_size=8, color=COLOR_TEXT, align=2)

        # 層級之間的箭頭
        if i < n_layers - 1:
            arrow_y = layer_top + layer_height + layer_gap / 2
            add_textbox(slide, "↓",
                       left + width / 2 - 8, arrow_y - 6, 16, 12,
                       font_size=10, color=COLOR_GRAY, align=2)

    return shapes
