# -*- coding: utf-8 -*-
"""
橫向流程圖繪製（pywin32 版本）

繪製橫向節點流程圖，支援：
- 節點標題和說明
- 箭頭標籤
- 自動間距計算
- 節點高亮
- 自適應縱向佈局（節點過多時）
"""

from ._colors_pywin32 import (
    COLOR_BLUE, COLOR_GREEN, COLOR_RED, COLOR_ORANGE,
    COLOR_WHITE, COLOR_TEXT, COLOR_GRAY, COLOR_GRAY_LIGHT,
    FONT_NAME, hex_to_bgr, get_text_color
)
from ._shapes_pywin32 import (
    add_rounded_rect, add_textbox, add_right_arrow, add_down_arrow,
    add_arrow_line, add_label
)


# =============================================================================
# 配置
# =============================================================================

FLOW_LAYOUT_CONFIG = {
    "max_horizontal_nodes": 6,      # 超過此數量切換縱向
    "min_node_width": 60,           # 最小節點寬度（pt）
    "node_height": 50,              # 節點高度（pt）
    "arrow_size": 12,               # 箭頭大小（pt）
    "gap": 8,                       # 節點間距（pt）
    "char_width_avg": 7,            # 平均字元寬度（pt）- 中文
}


# =============================================================================
# 輔助函數
# =============================================================================

def calculate_text_width(text: str) -> float:
    """
    估算文字寬度（中文=2, 英文=1）

    Args:
        text: 文字內容

    Returns:
        估算寬度（以半形字元為單位）
    """
    width = 0
    for char in text:
        if ord(char) > 127:
            width += 2  # 中文/全形
        else:
            width += 1  # 英文/半形
    return width


def estimate_node_min_width(node: dict) -> float:
    """
    估算節點所需的最小寬度

    Args:
        node: 節點字典，包含 title 和 desc

    Returns:
        估算寬度（pt）
    """
    title = node.get("title", "")
    desc = node.get("desc", "")

    title_width = calculate_text_width(title) * FLOW_LAYOUT_CONFIG["char_width_avg"]
    desc_width = calculate_text_width(desc) * FLOW_LAYOUT_CONFIG["char_width_avg"]

    return max(title_width, desc_width) + 16  # 加上內邊距


def should_use_vertical_flow(nodes: list, available_width: float) -> tuple:
    """
    判斷是否應該使用縱向流程圖

    Args:
        nodes: 節點列表
        available_width: 可用寬度（pt）

    Returns:
        tuple: (是否使用縱向, 原因)
    """
    node_count = len(nodes)
    config = FLOW_LAYOUT_CONFIG

    # 條件 1：節點數量過多
    if node_count > config["max_horizontal_nodes"]:
        return True, f"節點數量 {node_count} > {config['max_horizontal_nodes']}"

    # 條件 2：計算後的節點寬度太小
    gap_total = config["gap"] * (node_count - 1) + config["arrow_size"] * (node_count - 1)
    node_width = (available_width - gap_total) / node_count

    if node_width < config["min_node_width"]:
        return True, f"節點寬度 {node_width:.1f} < {config['min_node_width']}"

    # 條件 3：文字估算寬度超過節點寬度
    for node in nodes:
        min_width = estimate_node_min_width(node)
        if min_width > node_width:
            return True, f"文字寬度 {min_width:.1f} > 節點寬度 {node_width:.1f}"

    return False, "可使用橫向"


# =============================================================================
# 橫向流程圖
# =============================================================================

def draw_flow(slide, left, top, width, height, nodes,
              arrow_labels=None, default_color=None):
    """
    繪製橫向流程圖

    Args:
        slide: pywin32 Slide 物件
        left, top: 左上角位置（pt）
        width, height: 寬高（pt）
        nodes: 節點列表，每個節點為字典：
            {
                "title": "節點標題",
                "desc": "節點說明",
                "color": 顏色（BGR，可選）,
                "highlight": 是否高亮（可選）
            }
            或直接為字串（作為標題）
        arrow_labels: 箭頭標籤列表（長度應為 len(nodes) - 1）
        default_color: 預設節點顏色（BGR）

    Returns:
        list: 建立的節點形狀列表
    """
    if not nodes:
        return []

    if default_color is None:
        default_color = COLOR_BLUE

    node_count = len(nodes)
    config = FLOW_LAYOUT_CONFIG

    # 計算尺寸
    arrow_width = config["arrow_size"]
    gap = config["gap"]
    node_height = min(height, config["node_height"])

    # 計算節點寬度
    total_arrow_space = (arrow_width + gap * 2) * (node_count - 1)
    node_width = (width - total_arrow_space) / node_count

    # 建立節點
    shapes = []
    for i, node in enumerate(nodes):
        # 解析節點資料
        if isinstance(node, str):
            node = {"title": node}

        title = node.get("title", "")
        desc = node.get("desc", "")
        color = node.get("color", default_color)
        highlight = node.get("highlight", False)

        # 計算位置
        x = left + i * (node_width + arrow_width + gap * 2)
        y = top + (height - node_height) / 2

        # 繪製節點
        if highlight:
            # 高亮節點：虛線邊框
            shape = add_rounded_rect(slide, x, y, node_width, node_height,
                                     line_color=color, fill_color=COLOR_WHITE,
                                     weight=2, dash=2)
        else:
            shape = add_rounded_rect(slide, x, y, node_width, node_height,
                                     line_color=None, fill_color=color)

        shapes.append(shape)

        # 文字顏色
        text_color = get_text_color(color) if not highlight else color

        # 標題
        title_height = node_height / 2 if desc else node_height
        add_textbox(slide, title, x + 4, y + 4,
                   node_width - 8, title_height - 4,
                   font_size=9, bold=True, color=text_color, align=2)

        # 說明
        if desc:
            add_textbox(slide, desc, x + 4, y + node_height / 2,
                       node_width - 8, node_height / 2 - 4,
                       font_size=8, bold=False, color=text_color, align=2)

        # 箭頭（除了最後一個節點）
        if i < node_count - 1:
            arrow_x = x + node_width + gap
            arrow_y = y + node_height / 2 - arrow_width / 2
            add_right_arrow(slide, arrow_x, arrow_y, arrow_width, arrow_width,
                           COLOR_GRAY)

            # 箭頭標籤
            if arrow_labels and i < len(arrow_labels) and arrow_labels[i]:
                add_label(slide, arrow_labels[i],
                         arrow_x - 10, arrow_y - 14,
                         arrow_width + 20, 12,
                         font_size=7, color=COLOR_GRAY, align=2)

    return shapes


# =============================================================================
# 縱向流程圖
# =============================================================================

def draw_flow_vertical(slide, left, top, width, height, nodes,
                       arrow_labels=None, default_color=None):
    """
    繪製縱向流程圖

    Args:
        slide: pywin32 Slide 物件
        left, top: 左上角位置（pt）
        width, height: 寬高（pt）
        nodes: 節點列表（同 draw_flow）
        arrow_labels: 箭頭標籤列表
        default_color: 預設節點顏色（BGR）

    Returns:
        list: 建立的節點形狀列表
    """
    if not nodes:
        return []

    if default_color is None:
        default_color = COLOR_BLUE

    node_count = len(nodes)
    config = FLOW_LAYOUT_CONFIG

    # 計算尺寸
    arrow_height = config["arrow_size"]
    gap = config["gap"]
    node_width = width * 0.8  # 使用 80% 寬度
    node_left = left + (width - node_width) / 2

    # 計算節點高度
    total_arrow_space = (arrow_height + gap * 2) * (node_count - 1)
    node_height = (height - total_arrow_space) / node_count
    node_height = min(node_height, config["node_height"])

    # 建立節點
    shapes = []
    for i, node in enumerate(nodes):
        # 解析節點資料
        if isinstance(node, str):
            node = {"title": node}

        title = node.get("title", "")
        desc = node.get("desc", "")
        color = node.get("color", default_color)
        highlight = node.get("highlight", False)

        # 計算位置
        y = top + i * (node_height + arrow_height + gap * 2)

        # 繪製節點
        if highlight:
            shape = add_rounded_rect(slide, node_left, y, node_width, node_height,
                                     line_color=color, fill_color=COLOR_WHITE,
                                     weight=2, dash=2)
        else:
            shape = add_rounded_rect(slide, node_left, y, node_width, node_height,
                                     line_color=None, fill_color=color)

        shapes.append(shape)

        # 文字顏色
        text_color = get_text_color(color) if not highlight else color

        # 標題和說明（左右排列）
        if desc:
            add_textbox(slide, title, node_left + 4, y + 4,
                       node_width * 0.45, node_height - 8,
                       font_size=9, bold=True, color=text_color, align=1)
            add_textbox(slide, desc, node_left + node_width * 0.5, y + 4,
                       node_width * 0.45, node_height - 8,
                       font_size=8, bold=False, color=text_color, align=1)
        else:
            add_textbox(slide, title, node_left + 4, y + (node_height - 16) / 2,
                       node_width - 8, 16,
                       font_size=9, bold=True, color=text_color, align=2)

        # 箭頭（除了最後一個節點）
        if i < node_count - 1:
            arrow_x = node_left + node_width / 2 - arrow_height / 2
            arrow_y = y + node_height + gap
            add_down_arrow(slide, arrow_x, arrow_y, arrow_height, arrow_height,
                          COLOR_GRAY)

            # 箭頭標籤
            if arrow_labels and i < len(arrow_labels) and arrow_labels[i]:
                add_label(slide, arrow_labels[i],
                         node_left + node_width / 2 + arrow_height,
                         arrow_y, node_width / 2 - arrow_height, 12,
                         font_size=7, color=COLOR_GRAY, align=1)

    return shapes


# =============================================================================
# 自適應流程圖
# =============================================================================

def draw_flow_adaptive(slide, left, top, width, height, nodes,
                       arrow_labels=None, default_color=None):
    """
    自適應流程圖：自動選擇橫向或縱向

    Args:
        slide: pywin32 Slide 物件
        left, top: 左上角位置（pt）
        width, height: 寬高（pt）
        nodes: 節點列表
        arrow_labels: 箭頭標籤列表
        default_color: 預設節點顏色

    Returns:
        list: 建立的節點形狀列表
    """
    should_vertical, reason = should_use_vertical_flow(nodes, width)

    if should_vertical:
        return draw_flow_vertical(slide, left, top, width, height, nodes,
                                  arrow_labels, default_color)
    else:
        return draw_flow(slide, left, top, width, height, nodes,
                        arrow_labels, default_color)


# =============================================================================
# 詳細版流程圖（支援更多自定義）
# =============================================================================

def draw_flow_detailed(slide, left, top, width, height, nodes,
                       arrow_labels=None, direction="horizontal",
                       show_time_labels=False, bottom_summary=None):
    """
    詳細版流程圖

    Args:
        slide: pywin32 Slide 物件
        left, top: 左上角位置（pt）
        width, height: 寬高（pt）
        nodes: 節點列表，每個節點為字典：
            {
                "title": "標題",
                "desc": "說明",
                "time": "時間標籤（可選）",
                "color": 顏色（BGR，可選）,
                "highlight": 是否高亮（可選）,
                "meta": "元資料（可選）"
            }
        arrow_labels: 箭頭標籤列表
        direction: "horizontal" 或 "vertical"
        show_time_labels: 是否顯示時間標籤
        bottom_summary: 底部摘要文字

    Returns:
        list: 建立的形狀列表
    """
    shapes = []

    # 預留底部摘要空間
    content_height = height
    if bottom_summary:
        content_height = height - 24

    # 繪製流程圖
    if direction == "vertical":
        shapes = draw_flow_vertical(slide, left, top, width, content_height,
                                    nodes, arrow_labels)
    else:
        shapes = draw_flow(slide, left, top, width, content_height,
                          nodes, arrow_labels)

    # 底部摘要
    if bottom_summary:
        add_textbox(slide, bottom_summary,
                   left, top + content_height + 4,
                   width, 20,
                   font_size=10, color=COLOR_TEXT, align=1)

    return shapes
