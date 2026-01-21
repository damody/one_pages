# -*- coding: utf-8 -*-
"""
Phase 6 Renderer using pywin32 + mcp-yogalayout

此模組提供主渲染器類別 LayoutRenderer，用於：
1. 透過 MCP 協議呼叫 mcp-yogalayout 計算投影片佈局
2. 根據 layout.json 使用 pywin32 渲染投影片
3. 支援文字、表格、圖表、圖片等元素

使用方式：
    renderer = LayoutRenderer()
    renderer.create_presentation()
    layout = renderer.compute_layout_from_markdown("slide.md")
    renderer.render_from_layout(layout, content_data)
    renderer.save("output.pptx")
    renderer.close()
"""

import os
import json
import re
from typing import Dict, Any, List, Optional

# pywin32 COM API
try:
    import win32com.client as win32
except ImportError:
    print("警告：pywin32 未安裝，請執行 pip install pywin32")
    win32 = None

# 本地模組
from modules_pywin32._colors_pywin32 import (
    COLOR_TEXT, COLOR_WHITE, COLOR_GRAY_BG, COLOR_GRAY_LIGHT, COLOR_GRAY,
    COLOR_RED, COLOR_GREEN, COLOR_BLUE, COLOR_ORANGE,
    BG_COLOR, ACCENT_BLUE, ACCENT_ORANGE, ACCENT_GREEN, ACCENT_PURPLE, ACCENT_RED,
    FONT_NAME, hex_to_bgr, get_text_color
)
from modules_pywin32._shapes_pywin32 import (
    add_background, add_slide_title, add_textbox, add_label,
    add_rect, add_rounded_rect, add_panel, add_content_box,
    add_arrow_line, add_right_arrow
)
from modules_pywin32._mcp_client import YogaLayoutClient, MCPError
from modules_pywin32.draw_flow_pywin32 import (
    draw_flow, draw_flow_vertical, draw_flow_adaptive
)
from modules_pywin32.draw_before_after_pywin32 import (
    draw_before_after, draw_before_after_with_flow
)
from modules_pywin32.draw_line_chart_pywin32 import (
    draw_line_chart, draw_bar_chart, draw_pie_chart
)


# =============================================================================
# 配置
# =============================================================================

# 16:9 投影片尺寸（pt）
SLIDE_WIDTH_PT = 960
SLIDE_HEIGHT_PT = 540

# 角色對應樣式
ROLE_STYLES = {
    "title": {"size": 20, "bold": True, "color": COLOR_TEXT},
    "subtitle": {"size": 14, "bold": True, "color": hex_to_bgr("#666666")},
    "h2": {"size": 10, "bold": True, "color": ACCENT_BLUE},
    "body": {"size": 8, "bold": False, "color": COLOR_TEXT},
    "caption": {"size": 10, "bold": False, "color": hex_to_bgr("#888888")},
    "mono": {"size": 10, "bold": False, "color": COLOR_TEXT, "font": "Consolas"},
}

# 區塊顏色對應
SECTION_COLORS = {
    "技術": ACCENT_BLUE,
    "成功": ACCENT_BLUE,
    "問題": ACCENT_ORANGE,
    "POC": ACCENT_ORANGE,
    "效益": ACCENT_GREEN,
    "解決": ACCENT_GREEN,
    "架構": ACCENT_PURPLE,
    "行動": ACCENT_RED,
    "決策": ACCENT_RED,
}


# =============================================================================
# 主渲染器
# =============================================================================

class LayoutRenderer:
    """
    Phase 6 主渲染器：整合 mcp-yogalayout 與 pywin32

    流程：
    1. create_presentation() - 建立空白簡報
    2. compute_layout_from_markdown() - 呼叫 MCP 計算佈局
    3. render_from_layout() - 根據 layout.json 渲染
    4. save() - 儲存 PPTX
    5. close() - 關閉 PowerPoint
    """

    def __init__(self, visible: bool = True):
        """
        初始化渲染器

        Args:
            visible: 是否顯示 PowerPoint 視窗
        """
        if win32 is None:
            raise RuntimeError("pywin32 未安裝")

        self.ppt = win32.Dispatch("PowerPoint.Application")
        self.ppt.Visible = visible
        self.prs = None
        self.mcp_client = None
        self._current_slide_index = 0

    def create_presentation(self):
        """
        建立新的空白簡報

        Returns:
            Presentation 物件
        """
        self.prs = self.ppt.Presentations.Add()
        return self.prs

    def open_presentation(self, path: str):
        """
        開啟現有簡報

        Args:
            path: PPTX 檔案路徑

        Returns:
            Presentation 物件
        """
        self.prs = self.ppt.Presentations.Open(os.path.abspath(path))
        return self.prs

    def compute_layout_from_markdown(
        self,
        markdown_path: str,
        theme_path: str = "workspace/themes/default.json",
        output_dir: str = "workspace/out",
        template: str = "auto",
        density: str = "comfortable"
    ) -> Dict[str, Any]:
        """
        透過 MCP 呼叫 mcp-yogalayout 計算佈局

        Args:
            markdown_path: Markdown 檔案路徑（相對於 workspace）
            theme_path: 主題 JSON 路徑
            output_dir: 輸出目錄
            template: 模板選擇
            density: 密度設定

        Returns:
            dict: layout.json 內容
        """
        if self.mcp_client is None:
            self.mcp_client = YogaLayoutClient()
            self.mcp_client.start()

        return self.mcp_client.compute_layout(
            markdown_path=markdown_path,
            theme_path=theme_path,
            output_dir=output_dir,
            template=template,
            density=density
        )

    def render_from_layout(
        self,
        layout_data: Dict[str, Any],
        content_data: Optional[Dict[str, Any]] = None
    ):
        """
        根據 layout.json 渲染投影片

        Args:
            layout_data: layout.json 內容
            content_data: 原始內容資料（用於取得文字內容）

        Returns:
            Slide 物件
        """
        if self.prs is None:
            raise RuntimeError("請先呼叫 create_presentation()")

        if content_data is None:
            content_data = {}

        # 建立新投影片
        # ppLayoutBlank = 12
        slide = self.prs.Slides.Add(self.prs.Slides.Count + 1, 12)
        self._current_slide_index += 1

        # 取得投影片尺寸
        slide_size = layout_data.get("slide", {})
        width_pt = slide_size.get("w_pt", SLIDE_WIDTH_PT)
        height_pt = slide_size.get("h_pt", SLIDE_HEIGHT_PT)

        # 加入背景
        add_background(slide, width_pt, height_pt, BG_COLOR)

        # 渲染每個元素
        elements = layout_data.get("elements", [])
        for elem in elements:
            self._render_element(slide, elem, content_data)

        return slide

    def _render_element(
        self,
        slide,
        elem: Dict[str, Any],
        content_data: Dict[str, Any]
    ):
        """
        渲染單一元素

        Args:
            slide: pywin32 Slide 物件
            elem: 元素資料
            content_data: 內容資料
        """
        # 取得邊界框
        box = elem.get("bounding_box", {})
        x = box.get("x", 0)
        y = box.get("y", 0)
        w = box.get("w", 100)
        h = box.get("h", 50)

        # 取得元素類型和角色
        kind = elem.get("kind", "text")
        role = elem.get("role", "body")
        elem_id = elem.get("id", "")

        # 根據類型渲染
        if kind == "text":
            self._render_text(slide, x, y, w, h, role, elem_id, content_data)
        elif kind == "bullets":
            self._render_bullets(slide, x, y, w, h, elem_id, content_data)
        elif kind == "table":
            self._render_table(slide, x, y, w, h, elem_id, content_data)
        elif kind == "figure":
            self._render_figure(slide, x, y, w, h, elem, content_data)
        elif kind == "callout":
            self._render_callout(slide, x, y, w, h, elem_id, content_data)

    def _render_text(
        self,
        slide, x, y, w, h,
        role: str,
        elem_id: str,
        content_data: Dict
    ):
        """渲染文字元素"""
        # 取得內容
        text = self._get_content_text(elem_id, content_data)
        if not text:
            text = elem_id  # 使用 ID 作為預設文字

        # 取得樣式
        style = ROLE_STYLES.get(role, ROLE_STYLES["body"])

        add_textbox(
            slide, text, x, y, w, h,
            font_size=style["size"],
            bold=style["bold"],
            color=style["color"],
            font_name=style.get("font", FONT_NAME),
            align=1 if role in ["body", "caption"] else 2
        )

    def _render_bullets(
        self,
        slide, x, y, w, h,
        elem_id: str,
        content_data: Dict
    ):
        """渲染項目符號列表"""
        # 取得項目
        items = self._get_content_items(elem_id, content_data)
        if not items:
            items = [elem_id]

        # 組合文字
        text = "\n".join([f"• {item}" for item in items])

        # 加入圓角矩形背景
        add_rounded_rect(slide, x, y, w, h,
                        line_color=COLOR_GRAY_LIGHT, fill_color=COLOR_WHITE)

        # 加入文字
        add_textbox(slide, text, x + 8, y + 8, w - 16, h - 16,
                   font_size=10, color=COLOR_TEXT)

    def _render_table(
        self,
        slide, x, y, w, h,
        elem_id: str,
        content_data: Dict
    ):
        """渲染表格"""
        # 取得表格資料
        table_data = self._get_content_table(elem_id, content_data)
        if not table_data:
            # 使用預設資料
            table_data = {
                "headers": ["欄位"],
                "rows": [[elem_id]]
            }

        headers = table_data.get("headers", [])
        rows = table_data.get("rows", [])

        if not headers:
            return

        col_count = len(headers)
        row_count = len(rows) + 1  # +1 for header
        col_width = w / col_count
        row_height = h / row_count

        # 表頭
        for i, header in enumerate(headers):
            cell_x = x + i * col_width
            add_rect(slide, cell_x, y, col_width, row_height,
                    line_color=COLOR_GRAY_LIGHT, fill_color=COLOR_GRAY_BG)
            add_textbox(slide, header, cell_x + 4, y + 2,
                       col_width - 8, row_height - 4,
                       font_size=9, bold=True, color=COLOR_TEXT, align=2)

        # 資料列
        for row_idx, row in enumerate(rows):
            row_y = y + (row_idx + 1) * row_height
            for col_idx, cell in enumerate(row):
                cell_x = x + col_idx * col_width
                add_rect(slide, cell_x, row_y, col_width, row_height,
                        line_color=COLOR_GRAY_LIGHT, fill_color=COLOR_WHITE)
                add_textbox(slide, str(cell), cell_x + 4, row_y + 2,
                           col_width - 8, row_height - 4,
                           font_size=8, color=COLOR_TEXT, align=2)

    def _render_figure(
        self,
        slide, x, y, w, h,
        elem: Dict,
        content_data: Dict
    ):
        """渲染圖表/圖片佔位"""
        elem_id = elem.get("id", "")
        alt = elem.get("alt", "")
        ratio = elem.get("ratio", "16:9")

        # 優先從 diagrams_content 取得類型
        # 處理 id 前綴：layout.json 用 "fig:main:xxx"，content.json 用 "main:xxx"
        diagrams_content = content_data.get("diagrams_content", {})
        diagram_type = None
        lookup_id = elem_id.replace("fig:", "") if elem_id.startswith("fig:") else elem_id
        if lookup_id in diagrams_content:
            diagram_type = diagrams_content[lookup_id].get("type")

        # 根據類型決定渲染方式
        if diagram_type == "before_after":
            self._render_comparison(slide, x, y, w, h, elem_id, content_data)
        elif diagram_type == "flow":
            self._render_flow_diagram(slide, x, y, w, h, elem_id, content_data)
        elif diagram_type == "platform_compare":
            self._render_comparison(slide, x, y, w, h, elem_id, content_data)
        elif diagram_type == "timeline":
            self._render_flow_diagram(slide, x, y, w, h, elem_id, content_data)
        elif diagram_type in ("comparison", "architecture"):
            self._render_comparison(slide, x, y, w, h, elem_id, content_data)
        else:
            # 回退到 alt 描述判斷
            alt_lower = alt.lower()
            if "折線" in alt or "趨勢" in alt or "line" in alt_lower:
                self._render_line_chart(slide, x, y, w, h, elem_id, content_data)
            elif "長條" in alt or "bar" in alt_lower or "column" in alt_lower:
                self._render_bar_chart(slide, x, y, w, h, elem_id, content_data)
            elif "圓餅" in alt or "pie" in alt_lower:
                self._render_pie_chart(slide, x, y, w, h, elem_id, content_data)
            elif "流程" in alt or "flow" in alt_lower:
                self._render_flow_diagram(slide, x, y, w, h, elem_id, content_data)
            elif "對比" in alt or "compare" in alt_lower or "before" in alt_lower:
                self._render_comparison(slide, x, y, w, h, elem_id, content_data)
            else:
                # 預設：繪製佔位框
                self._render_placeholder(slide, x, y, w, h, elem_id, alt)

    def _render_callout(
        self,
        slide, x, y, w, h,
        elem_id: str,
        content_data: Dict
    ):
        """渲染 Callout 註解"""
        text = self._get_content_text(elem_id, content_data)
        if not text:
            text = elem_id

        # 加入背景
        add_rounded_rect(slide, x, y, w, h,
                        line_color=ACCENT_ORANGE, fill_color=hex_to_bgr("#FFF8E1"),
                        weight=1.5)

        # 加入文字（帶 💡 圖標）
        add_textbox(slide, f"💡 {text}", x + 8, y + 4, w - 16, h - 8,
                   font_size=9, color=ACCENT_ORANGE)

    # =========================================================================
    # 圖表渲染
    # =========================================================================

    def _render_line_chart(self, slide, x, y, w, h, elem_id, content_data):
        """渲染折線圖"""
        chart_data = self._get_content_chart(elem_id, content_data)
        if chart_data:
            draw_line_chart(slide, x, y, w, h, chart_data)
        else:
            # 使用預設資料
            default_data = {
                "categories": ["Q1", "Q2", "Q3", "Q4"],
                "series": [{"name": "數據", "values": [10, 25, 35, 50]}]
            }
            draw_line_chart(slide, x, y, w, h, default_data, title=elem_id)

    def _render_bar_chart(self, slide, x, y, w, h, elem_id, content_data):
        """渲染長條圖"""
        chart_data = self._get_content_chart(elem_id, content_data)
        if chart_data:
            draw_bar_chart(slide, x, y, w, h, chart_data)
        else:
            default_data = {
                "categories": ["A", "B", "C"],
                "series": [{"name": "數據", "values": [30, 50, 20]}]
            }
            draw_bar_chart(slide, x, y, w, h, default_data, title=elem_id)

    def _render_pie_chart(self, slide, x, y, w, h, elem_id, content_data):
        """渲染圓餅圖"""
        chart_data = self._get_content_chart(elem_id, content_data)
        if chart_data:
            # 轉換格式
            pie_data = {
                "labels": chart_data.get("categories", []),
                "values": chart_data.get("series", [{}])[0].get("values", [])
            }
            draw_pie_chart(slide, x, y, w, h, pie_data)
        else:
            default_data = {"labels": ["A", "B", "C"], "values": [40, 35, 25]}
            draw_pie_chart(slide, x, y, w, h, default_data, title=elem_id)

    def _render_flow_diagram(self, slide, x, y, w, h, elem_id, content_data):
        """渲染流程圖"""
        flow_data = self._get_content_flow(elem_id, content_data)
        if flow_data:
            draw_flow_adaptive(slide, x, y, w, h, flow_data)
        else:
            default_nodes = [
                {"title": "步驟 1", "color": COLOR_BLUE},
                {"title": "步驟 2", "color": COLOR_BLUE},
                {"title": "步驟 3", "color": COLOR_GREEN}
            ]
            draw_flow_adaptive(slide, x, y, w, h, default_nodes)

    def _render_comparison(self, slide, x, y, w, h, elem_id, content_data):
        """渲染對比圖"""
        compare_data = self._get_content_comparison(elem_id, content_data)
        if compare_data:
            draw_before_after(
                slide, x, y, w, h,
                before_title=compare_data.get("before_title", "改善前"),
                before_items=compare_data.get("before_items", []),
                after_title=compare_data.get("after_title", "改善後"),
                after_items=compare_data.get("after_items", [])
            )
        else:
            # 繪製佔位框
            self._render_placeholder(slide, x, y, w, h, elem_id, "前後對比圖")

    def _render_placeholder(self, slide, x, y, w, h, elem_id, alt):
        """渲染佔位框"""
        # 繪製虛線邊框
        add_rounded_rect(slide, x, y, w, h,
                        line_color=COLOR_GRAY, fill_color=COLOR_GRAY_BG,
                        weight=1, dash=3)

        # 加入說明文字
        text = f"[圖表: {alt}]" if alt else f"[{elem_id}]"
        add_textbox(slide, text, x + 8, y + h / 2 - 10, w - 16, 20,
                   font_size=10, color=COLOR_GRAY, align=2)

    # =========================================================================
    # 內容取得輔助函數
    # =========================================================================

    def _get_content_text(self, elem_id: str, content_data: Dict) -> str:
        """從 content_data 取得文字內容"""
        texts = content_data.get("texts", {})
        return texts.get(elem_id, "")

    def _get_content_items(self, elem_id: str, content_data: Dict) -> List[str]:
        """從 content_data 取得項目列表"""
        items = content_data.get("items", {})
        return items.get(elem_id, [])

    def _get_content_table(self, elem_id: str, content_data: Dict) -> Dict:
        """從 content_data 取得表格資料"""
        tables = content_data.get("tables", {})
        return tables.get(elem_id, {})

    def _get_content_chart(self, elem_id: str, content_data: Dict) -> Dict:
        """從 content_data 取得圖表資料"""
        charts = content_data.get("charts", {})
        return charts.get(elem_id, {})

    def _get_content_flow(self, elem_id: str, content_data: Dict) -> List:
        """從 content_data 取得流程節點"""
        # 處理 id 前綴
        lookup_id = elem_id.replace("fig:", "") if elem_id.startswith("fig:") else elem_id

        # 優先從 diagrams_content 取得
        diagrams_content = content_data.get("diagrams_content", {})
        if lookup_id in diagrams_content:
            dc = diagrams_content[lookup_id]
            if dc.get("type") == "flow":
                # 從 stages 轉換為 nodes
                stages = dc.get("stages", [])
                nodes = []
                for stage in stages:
                    if stage.get("title"):
                        nodes.append({"title": stage["title"], "color": None})
                    for node in stage.get("nodes", []):
                        if node and node not in ("v", "|"):
                            nodes.append({"title": node, "color": None})
                return nodes if nodes else dc.get("nodes", [])
            # before_after 的 flow
            if dc.get("before", {}).get("flow"):
                return [{"title": n} for n in dc["before"]["flow"]]

        # 回退到舊格式
        flows = content_data.get("flows", {})
        return flows.get(elem_id, [])

    def _get_content_comparison(self, elem_id: str, content_data: Dict) -> Dict:
        """從 content_data 取得對比資料"""
        # 處理 id 前綴
        lookup_id = elem_id.replace("fig:", "") if elem_id.startswith("fig:") else elem_id

        # 優先從 diagrams_content 取得
        diagrams_content = content_data.get("diagrams_content", {})
        if lookup_id in diagrams_content:
            dc = diagrams_content[lookup_id]
            if dc.get("type") == "before_after":
                before = dc.get("before", {})
                after = dc.get("after", {})
                return {
                    "before_title": before.get("title", "改善前"),
                    "before_items": before.get("flow", [])[:6],  # 最多 6 項
                    "after_title": after.get("title", "改善後"),
                    "after_items": after.get("flow", [])[:6],
                    "before_annotations": before.get("annotations", []),
                    "after_annotations": after.get("annotations", [])
                }
            elif dc.get("type") == "platform_compare":
                return {
                    "before_title": dc.get("platform1", {}).get("title", "平台 A"),
                    "before_items": [r.split("OK")[0].strip() if "OK" in r else r for r in dc.get("rows", [])[:5]],
                    "after_title": dc.get("platform2", {}).get("title", "平台 B"),
                    "after_items": []
                }
            elif dc.get("type") == "comparison":
                return {
                    "before_title": dc.get("left", {}).get("title", "A"),
                    "before_items": dc.get("features", [])[:4],
                    "after_title": dc.get("right", {}).get("title", "B"),
                    "after_items": dc.get("features", [])[:4]
                }

        # 回退到舊格式
        comparisons = content_data.get("comparisons", {})
        return comparisons.get(elem_id, {})

    # =========================================================================
    # 儲存與關閉
    # =========================================================================

    def save(self, path: str, auto_close: bool = True):
        """
        儲存簡報

        Args:
            path: 輸出檔案路徑
            auto_close: 是否自動關閉簡報和 PowerPoint（預設 True）
        """
        if self.prs is None:
            raise RuntimeError("沒有簡報可儲存")

        abs_path = os.path.abspath(path)
        self.prs.SaveAs(abs_path)
        print(f"已儲存：{abs_path}")

        if auto_close:
            self.close()

    def close(self):
        """關閉簡報和 PowerPoint"""
        if self.mcp_client:
            self.mcp_client.stop()
            self.mcp_client = None

        if self.prs:
            try:
                self.prs.Close()
            except:
                pass
            self.prs = None

        if self.ppt:
            try:
                self.ppt.Quit()
            except:
                pass
            self.ppt = None

    def __enter__(self):
        """Context manager 支援"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 支援"""
        self.close()
        return False


# =============================================================================
# 便捷函數
# =============================================================================

def render_markdown_to_pptx(
    markdown_path: str,
    output_path: str,
    theme_path: str = "workspace/themes/default.json"
) -> str:
    """
    將 Markdown 渲染為 PPTX 的便捷函數

    Args:
        markdown_path: Markdown 檔案路徑
        output_path: 輸出 PPTX 路徑
        theme_path: 主題路徑

    Returns:
        str: 輸出檔案的絕對路徑
    """
    with LayoutRenderer() as renderer:
        renderer.create_presentation()

        # 計算佈局
        layout = renderer.compute_layout_from_markdown(
            markdown_path=markdown_path,
            theme_path=theme_path
        )

        # 渲染
        renderer.render_from_layout(layout, {})

        # 儲存
        renderer.save(output_path)

    return os.path.abspath(output_path)


# =============================================================================
# 測試
# =============================================================================

if __name__ == "__main__":
    print("render_pywin32.py 測試")
    print(f"SLIDE_WIDTH_PT: {SLIDE_WIDTH_PT}")
    print(f"SLIDE_HEIGHT_PT: {SLIDE_HEIGHT_PT}")
    print("模組載入成功")
