"""
PPTX 圖表繪製模組集合

每個圖表都是獨立檔案，只需讀取需要的模組：

├── _colors.py                          # 顏色常數與字體定義
├── _tracking.py                        # 元素追蹤與排版審查
├── helpers.py                          # 輔助函數
│
├── draw_before_after.py                # 前後對比圖
├── draw_architecture.py                # 分層架構圖
├── draw_metric_cards.py                # 指標卡片
├── draw_comparison_table.py            # 對比表格
├── draw_icon_list.py                   # 圖標列表
│
├── draw_flow.py                        # 橫向流程圖
├── draw_flow_detailed.py               # 詳細版流程圖
├── draw_before_after_with_flow.py      # 帶流程的前後對比
├── draw_platform_compare.py            # 平台對比圖
│
├── draw_line_chart.py                  # 折線圖
├── draw_bar_chart.py                   # 長條圖
├── draw_pie_chart.py                   # 圓餅圖
│
├── draw_gantt_chart.py                 # 甘特圖
├── draw_architecture_enhanced.py       # 增強版架構圖
├── draw_matrix_chart.py                # 矩陣圖
│
├── draw_mini_flow.py                   # 迷你流程圖
├── draw_mini_before_after.py           # 迷你前後對比
├── draw_mini_layers.py                 # 迷你分層圖
├── draw_mini_timeline.py               # 迷你時間軸
├── draw_mini_icon.py                   # 迷你圖標
│
├── draw_glossary_card_with_diagram.py  # 帶圖術語卡片
├── draw_glossary_card_text_only.py     # 純文字術語卡片
├── draw_glossary_page_with_diagrams.py # 術語頁面(有圖)
└── draw_glossary_page_text_only.py     # 術語頁面(純文字)

使用範例：
    from modules.draw_before_after import draw_before_after
    from modules.draw_line_chart import draw_line_chart
"""

# 顏色常數
from ._colors import (
    COLOR_RED, COLOR_GREEN, COLOR_BLUE, COLOR_ORANGE, COLOR_PURPLE,
    COLOR_GRAY_BG, COLOR_GRAY_DARK, COLOR_TEXT, COLOR_WHITE, COLOR_ACCENT,
    BG_COLOR, ACCENT_BLUE, ACCENT_ORANGE, ACCENT_GREEN, ACCENT_PURPLE, ACCENT_RED,
    FONT_NAME, FLOW_LAYOUT_CONFIG
)

# 追蹤系統
from ._tracking import (
    reset_element_tracker, set_current_slide, track_element,
    boxes_overlap, calculate_overlap_area, check_overlaps, layout_review
)

# 輔助函數
from .helpers import add_section_title, add_bullet_list, add_content_box

# 基礎圖表
from .draw_before_after import draw_before_after
from .draw_architecture import draw_architecture
from .draw_metric_cards import draw_metric_cards
from .draw_comparison_table import draw_comparison_table
from .draw_icon_list import draw_icon_list

# 流程圖
from .draw_flow import draw_flow
from .draw_flow_detailed import draw_flow_detailed
from .draw_before_after_with_flow import draw_before_after_with_flow
from .draw_platform_compare import draw_platform_compare

# 原生圖表
from .draw_line_chart import draw_line_chart
from .draw_bar_chart import draw_bar_chart
from .draw_pie_chart import draw_pie_chart

# 進階圖表
from .draw_gantt_chart import draw_gantt_chart
from .draw_architecture_enhanced import draw_architecture_enhanced
from .draw_matrix_chart import draw_matrix_chart

# 迷你圖表
from .draw_mini_flow import draw_mini_flow
from .draw_mini_before_after import draw_mini_before_after
from .draw_mini_layers import draw_mini_layers
from .draw_mini_timeline import draw_mini_timeline
from .draw_mini_icon import draw_mini_icon

# 術語卡片
from .draw_glossary_card_with_diagram import draw_glossary_card_with_diagram
from .draw_glossary_card_text_only import draw_glossary_card_text_only
from .draw_glossary_page_with_diagrams import draw_glossary_page_with_diagrams
from .draw_glossary_page_text_only import draw_glossary_page_text_only
