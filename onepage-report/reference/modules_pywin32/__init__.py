# -*- coding: utf-8 -*-
"""
pywin32 模組套件：用於 Phase 6 Render (pywin32 版本)

此套件包含：
- _colors_pywin32: 顏色常數與轉換函數（BGR 格式）
- _shapes_pywin32: 基本形狀繪製函數
- _mcp_client: MCP Client 與 mcp-yogalayout 通訊
- draw_flow_pywin32: 流程圖繪製
- draw_before_after_pywin32: 前後對比圖繪製
- draw_line_chart_pywin32: 折線圖繪製
- draw_timeline_pywin32: 時間軸圖繪製
- draw_platform_compare_pywin32: 平台對比圖繪製
- draw_architecture_pywin32: 架構圖繪製
"""

from ._colors_pywin32 import *
from ._shapes_pywin32 import *
from .draw_flow_pywin32 import (
    draw_flow, draw_flow_vertical, draw_flow_adaptive, draw_flow_detailed,
    should_use_vertical_flow
)
from .draw_before_after_pywin32 import (
    draw_before_after, draw_before_after_with_flow,
    draw_before_after_with_vertical_flow
)
from .draw_line_chart_pywin32 import (
    draw_line_chart, draw_bar_chart, draw_pie_chart, draw_area_chart,
    draw_simple_line_chart, draw_comparison_line_chart
)
from .draw_timeline_pywin32 import draw_timeline
from .draw_platform_compare_pywin32 import draw_platform_compare
from .draw_architecture_pywin32 import draw_architecture
