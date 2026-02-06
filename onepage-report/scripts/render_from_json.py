#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
render_from_json.py - Phase 6 固定渲染器

用法:
    python render_from_json.py \
        --layout layout.json \
        --data slide_data.json \
        --output final.pptx

此腳本是固定的，不需要 subagent 產生。
Subagent 只需產生 slide_data.json。
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# 加入 reference 目錄到路徑
SCRIPT_DIR = Path(__file__).parent
REFERENCE_DIR = SCRIPT_DIR.parent / "reference"
sys.path.insert(0, str(REFERENCE_DIR))

# 延遲載入 pywin32 相關模組
_renderer_module = None
_shapes_module = None
_colors_module = None


def _load_modules():
    """延遲載入渲染模組"""
    global _renderer_module, _shapes_module, _colors_module
    if _renderer_module is None:
        from render_pywin32 import LayoutRenderer, SLIDE_WIDTH_PT, SLIDE_HEIGHT_PT
        from modules_pywin32._colors_pywin32 import (
            COLOR_TEXT, ACCENT_BLUE, ACCENT_GREEN, ACCENT_ORANGE,
            ACCENT_RED, ACCENT_PURPLE, BG_COLOR, COLOR_WHITE
        )
        from modules_pywin32._shapes_pywin32 import (
            add_background, add_textbox, add_rounded_rect, add_rect
        )
        _renderer_module = {
            'LayoutRenderer': LayoutRenderer,
            'SLIDE_WIDTH_PT': SLIDE_WIDTH_PT,
            'SLIDE_HEIGHT_PT': SLIDE_HEIGHT_PT
        }
        _colors_module = {
            'COLOR_TEXT': COLOR_TEXT,
            'ACCENT_BLUE': ACCENT_BLUE,
            'ACCENT_GREEN': ACCENT_GREEN,
            'ACCENT_ORANGE': ACCENT_ORANGE,
            'ACCENT_RED': ACCENT_RED,
            'ACCENT_PURPLE': ACCENT_PURPLE,
            'BG_COLOR': BG_COLOR,
            'COLOR_WHITE': COLOR_WHITE
        }
        _shapes_module = {
            'add_background': add_background,
            'add_textbox': add_textbox,
            'add_rounded_rect': add_rounded_rect,
            'add_rect': add_rect
        }
    return _renderer_module, _shapes_module, _colors_module


def load_json(path: str) -> dict:
    """載入 JSON 檔案"""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def convert_slide_data_to_content_data(slide_data: dict) -> dict:
    """
    將 slide_data.json 格式轉換為 render_pywin32 的 content_data 格式

    slide_data 格式：結構化的頁面和元素
    content_data 格式：按類型分組的字典（texts, items, tables, diagrams_content）
    """
    content_data = {
        "texts": {},
        "items": {},
        "tables": {},
        "charts": {},
        "flows": {},
        "comparisons": {},
        "diagrams_content": {}
    }

    for page in slide_data.get("pages", []):
        for elem in page.get("elements", []):
            elem_id = elem.get("id", "")
            kind = elem.get("kind", "")

            if kind == "text":
                content_data["texts"][elem_id] = elem.get("content", "")

            elif kind == "section":
                # Section 包含標題和條列項目
                content_data["texts"][f"{elem_id}:title"] = elem.get("title", "")
                content_data["items"][elem_id] = elem.get("bullets", [])

            elif kind == "table":
                content_data["tables"][elem_id] = {
                    "headers": elem.get("headers", []),
                    "rows": elem.get("rows", [])
                }

            elif kind == "figure":
                fig_type = elem.get("type", "")
                fig_data = elem.get("data", {})

                # 移除 fig: 前綴存入 diagrams_content
                clean_id = elem_id.replace("fig:", "") if elem_id.startswith("fig:") else elem_id

                # 轉換為 diagrams_content 格式
                content_data["diagrams_content"][clean_id] = {
                    "type": fig_type,
                    **convert_figure_data(fig_type, fig_data)
                }

            elif kind == "callout":
                content_data["texts"][elem_id] = elem.get("content", "")

    return content_data


def convert_figure_data(fig_type: str, fig_data: dict) -> dict:
    """轉換圖表資料格式"""
    if fig_type == "before_after":
        before = fig_data.get("before", {})
        after = fig_data.get("after", {})
        return {
            "before": {
                "title": before.get("title", "改善前"),
                "flow": before.get("steps", [])
            },
            "after": {
                "title": after.get("title", "改善後"),
                "flow": after.get("steps", [])
            }
        }

    elif fig_type == "flow":
        return {
            "stages": fig_data.get("stages", [])
        }

    elif fig_type == "timeline":
        points = fig_data.get("points", [])
        return {
            "events": [
                {"name": p.get("label", ""), "time": p.get("time", ""), "desc": p.get("duration", "")}
                for p in points
            ]
        }

    elif fig_type == "platform_compare":
        platforms = fig_data.get("platforms", [])
        return {
            "platform1": {
                "title": platforms[0].get("name", "") if len(platforms) > 0 else "",
                "nodes": [item.get("text", "") for item in platforms[0].get("items", [])] if len(platforms) > 0 else []
            },
            "platform2": {
                "title": platforms[1].get("name", "") if len(platforms) > 1 else "",
                "nodes": [item.get("text", "") for item in platforms[1].get("items", [])] if len(platforms) > 1 else []
            }
        }

    elif fig_type == "architecture":
        return {
            "layers": fig_data.get("layers", [])
        }

    elif fig_type in ("line_chart", "bar_chart", "pie_chart"):
        return fig_data

    return fig_data


def render(
    layout_path: str,
    data_path: str,
    output_path: str,
    script_path: Optional[str] = None
):
    """
    主渲染函數

    Args:
        layout_path: MCP yogalayout 輸出的 layout.json
        data_path: subagent 產生的 slide_data.json
        output_path: 輸出 PPTX 路徑
        script_path: 演講稿輸出路徑（可選）
    """
    # 載入模組
    renderer_mod, shapes_mod, colors_mod = _load_modules()
    LayoutRenderer = renderer_mod['LayoutRenderer']

    print(f"[render_from_json] 載入 layout: {layout_path}")
    layout = load_json(layout_path)

    print(f"[render_from_json] 載入 slide_data: {data_path}")
    slide_data = load_json(data_path)

    # 轉換為 content_data 格式
    content_data = convert_slide_data_to_content_data(slide_data)

    print(f"[render_from_json] 開始渲染...")
    print(f"  - texts: {len(content_data['texts'])} 個")
    print(f"  - items: {len(content_data['items'])} 個")
    print(f"  - tables: {len(content_data['tables'])} 個")
    print(f"  - diagrams: {len(content_data['diagrams_content'])} 個")

    # 建立渲染器
    renderer = LayoutRenderer(visible=True)
    renderer.create_presentation()

    # 處理多頁（相容單頁和多頁格式）
    if "pages" in layout:
        pages = layout["pages"]
    else:
        # 單頁格式
        pages = [layout]

    for i, page_data in enumerate(pages):
        page_num = page_data.get("page_number", i + 1)
        print(f"[render_from_json] 渲染第 {page_num} 頁...")
        renderer.render_from_layout(page_data, content_data)

    # 儲存
    abs_output = os.path.abspath(output_path)
    renderer.save(abs_output, auto_close=True)
    print(f"[render_from_json] PPTX 已儲存: {abs_output}")

    # 產生演講稿（如果有指定）
    if script_path:
        generate_script(slide_data, script_path)

    return abs_output


def generate_script(slide_data: dict, output_path: str):
    """從 slide_data 產生演講稿"""
    lines = []
    metadata = slide_data.get("metadata", {})

    lines.append(f"# {metadata.get('title', '報告')}")
    if metadata.get("subtitle"):
        lines.append(f"> {metadata.get('subtitle')}")
    lines.append("")

    for page in slide_data.get("pages", []):
        page_num = page.get("page", 1)
        lines.append(f"---")
        lines.append(f"## 第 {page_num} 頁")
        lines.append("")

        for elem in page.get("elements", []):
            kind = elem.get("kind", "")
            elem_id = elem.get("id", "")

            if kind == "text" and elem.get("role") == "title":
                continue  # 跳過標題（已在開頭）

            if kind == "section":
                title = elem.get("title", "")
                bullets = elem.get("bullets", [])
                lines.append(f"### {title}")
                lines.append("")
                for bullet in bullets:
                    lines.append(f"- {bullet}")
                lines.append("")

            elif kind == "figure":
                fig_type = elem.get("type", "")
                lines.append(f"[圖表: {elem_id} ({fig_type})]")
                lines.append("")

            elif kind == "table":
                lines.append(f"[表格: {elem_id}]")
                lines.append("")

    script_content = "\n".join(lines)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(script_content)

    print(f"[render_from_json] 演講稿已儲存: {output_path}")


def validate_inputs(layout_path: str, data_path: str) -> bool:
    """驗證輸入檔案"""
    errors = []

    if not Path(layout_path).exists():
        errors.append(f"layout.json 不存在: {layout_path}")

    if not Path(data_path).exists():
        errors.append(f"slide_data.json 不存在: {data_path}")

    if errors:
        for err in errors:
            print(f"[錯誤] {err}")
        return False

    # 驗證 JSON 格式
    try:
        layout = load_json(layout_path)
        if "elements" not in layout and "pages" not in layout:
            errors.append("layout.json 缺少 elements 或 pages")
    except json.JSONDecodeError as e:
        errors.append(f"layout.json 格式錯誤: {e}")

    try:
        data = load_json(data_path)
        if "pages" not in data:
            errors.append("slide_data.json 缺少 pages")
    except json.JSONDecodeError as e:
        errors.append(f"slide_data.json 格式錯誤: {e}")

    if errors:
        for err in errors:
            print(f"[錯誤] {err}")
        return False

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Phase 6 固定渲染器 - 將 JSON 資料渲染為 PPTX"
    )
    parser.add_argument(
        "--layout", required=True,
        help="MCP yogalayout 輸出的 layout.json 路徑"
    )
    parser.add_argument(
        "--data", required=True,
        help="slide_data.json 路徑"
    )
    parser.add_argument(
        "--output", required=True,
        help="輸出 PPTX 路徑"
    )
    parser.add_argument(
        "--script",
        help="演講稿輸出路徑（可選）"
    )
    parser.add_argument(
        "--validate-only", action="store_true",
        help="只驗證輸入，不執行渲染"
    )

    args = parser.parse_args()

    # 驗證輸入
    if not validate_inputs(args.layout, args.data):
        sys.exit(1)

    if args.validate_only:
        print("[render_from_json] 驗證通過")
        sys.exit(0)

    # 執行渲染
    try:
        render(
            layout_path=args.layout,
            data_path=args.data,
            output_path=args.output,
            script_path=args.script
        )
    except Exception as e:
        print(f"[錯誤] 渲染失敗: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
