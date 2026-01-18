# -*- coding: utf-8 -*-
"""
Yoga Converter: 將 Phase 5 的 one_page.md + diagrams.md 轉換為 mcp-yogalayout 格式

mcp-yogalayout 期望的 Markdown 格式：
- # 標題
- > 副標題 / callout
- ## 區塊標題
- 表格 (| col1 | col2 |)
- 項目符號 (- item)
- <fig id="xxx" ratio="16:9" kind="diagram|chart|image" alt="描述" />

Phase 5 格式：
- one_page.md: 純 Markdown 報告
- diagrams.md: 自然語言描述的圖表規格
"""

import re
import os
import json
import argparse
from pathlib import Path
from typing import Optional


def parse_diagrams_spec(diagrams_md: str) -> dict:
    """
    解析 diagrams.md，提取圖表規格

    Returns:
        dict: {
            "main": {"title": "...", "type": "...", "description": "..."},
            "appendix": [{"title": "...", "type": "...", "description": "..."}, ...]
        }
    """
    diagrams = {"main": None, "appendix": []}

    # 分割成區塊
    sections = re.split(r'^## ', diagrams_md, flags=re.MULTILINE)

    for section in sections:
        if not section.strip():
            continue

        lines = section.strip().split('\n')
        if not lines:
            continue

        # 取得標題
        title_line = lines[0]

        # 解析類型
        diagram_type = "diagram"  # 預設
        description = ""

        for line in lines[1:]:
            line = line.strip()
            if line.startswith('- **類型**：'):
                type_match = re.search(r'- \*\*類型\*\*：(\w+)', line)
                if type_match:
                    diagram_type = type_match.group(1)
            elif line.startswith('- **說明**：'):
                desc_match = re.search(r'- \*\*說明\*\*：(.+)', line)
                if desc_match:
                    description = desc_match.group(1)

        # 取得 SVG 生成指示
        svg_match = re.search(r'### SVG 生成指示\s*\n([\s\S]+?)(?=\n---|$)', section)
        if svg_match:
            svg_instruction = svg_match.group(1).strip()
            if not description:
                description = svg_instruction[:100] + "..." if len(svg_instruction) > 100 else svg_instruction

        diagram_info = {
            "title": title_line.replace('主圖：', '').replace('附錄圖', '').strip(),
            "type": diagram_type,
            "description": description
        }

        if '主圖' in title_line:
            diagrams["main"] = diagram_info
        elif '附錄圖' in title_line:
            diagrams["appendix"].append(diagram_info)

    return diagrams


def convert_diagram_type_to_kind(diagram_type: str) -> str:
    """
    將 diagrams.md 的類型轉換為 mcp-yogalayout 的 kind

    Args:
        diagram_type: before_after | platform_compare | flow | timeline | architecture

    Returns:
        kind: diagram | chart | image
    """
    # 這些類型都是用 pywin32 Shapes 繪製的「圖形」
    shape_types = {'before_after', 'platform_compare', 'flow', 'timeline', 'architecture'}

    # 這些類型使用原生 Chart
    chart_types = {'line_chart', 'bar_chart', 'pie_chart', 'area_chart'}

    if diagram_type in shape_types:
        return "diagram"
    elif diagram_type in chart_types:
        return "chart"
    else:
        return "diagram"  # 預設


def generate_fig_id(title: str, index: int = 0) -> str:
    """
    根據標題生成 fig id

    Args:
        title: 圖表標題
        index: 索引（用於附錄圖）

    Returns:
        fig_id: 例如 "flow", "compare", "fig1"
    """
    # 移除中文，只保留英文和數字
    ascii_title = re.sub(r'[^\x00-\x7F]+', '', title).strip()

    if ascii_title:
        # 轉換為 snake_case
        fig_id = re.sub(r'\s+', '_', ascii_title.lower())
        fig_id = re.sub(r'[^a-z0-9_]', '', fig_id)
        return fig_id[:20] if fig_id else f"fig{index}"
    else:
        return f"fig{index}"


def convert_one_page_to_yoga(one_page_md: str, diagrams: dict) -> str:
    """
    將 one_page.md 轉換為 mcp-yogalayout 格式

    主要轉換：
    1. 保留標題、副標題、區塊
    2. 在適當位置插入 <fig> 標籤
    3. 保留表格和項目符號

    Args:
        one_page_md: Phase 5 的 one_page.md 內容
        diagrams: parse_diagrams_spec 的輸出

    Returns:
        yoga_md: mcp-yogalayout 格式的 Markdown
    """
    lines = one_page_md.split('\n')
    result_lines = []

    main_fig_inserted = False
    appendix_fig_index = 0

    # 定義要插入主圖的區塊關鍵字
    main_fig_sections = ['資料流', '流程', '架構', 'Pipeline', '示意']

    for i, line in enumerate(lines):
        # 檢查是否是區塊標題
        if line.startswith('## '):
            section_title = line[3:].strip()
            result_lines.append(line)

            # 檢查是否應該在此區塊後插入主圖
            if not main_fig_inserted and diagrams.get("main"):
                for keyword in main_fig_sections:
                    if keyword in section_title:
                        # 插入主圖
                        main_info = diagrams["main"]
                        fig_id = generate_fig_id(main_info["title"], 0)
                        kind = convert_diagram_type_to_kind(main_info["type"])
                        alt = main_info["description"][:100] if main_info["description"] else main_info["title"]

                        result_lines.append(f'<fig id="{fig_id}" ratio="16:9" kind="{kind}" alt="{alt}" />')
                        main_fig_inserted = True
                        break
        else:
            result_lines.append(line)

    # 如果主圖還沒插入，在文件末尾前插入
    if not main_fig_inserted and diagrams.get("main"):
        main_info = diagrams["main"]
        fig_id = generate_fig_id(main_info["title"], 0)
        kind = convert_diagram_type_to_kind(main_info["type"])
        alt = main_info["description"][:100] if main_info["description"] else main_info["title"]

        # 在倒數第二段前插入
        insert_pos = len(result_lines) - 1
        for idx in range(len(result_lines) - 1, -1, -1):
            if result_lines[idx].startswith('## '):
                insert_pos = idx + 1
                break

        result_lines.insert(insert_pos, f'<fig id="{fig_id}" ratio="16:9" kind="{kind}" alt="{alt}" />')

    # 處理附錄圖（如果有 "附錄" 或 "技術細節" 區塊）
    for appendix_info in diagrams.get("appendix", []):
        fig_id = generate_fig_id(appendix_info["title"], appendix_fig_index + 1)
        kind = convert_diagram_type_to_kind(appendix_info["type"])
        alt = appendix_info["description"][:100] if appendix_info["description"] else appendix_info["title"]

        # 在文件末尾加入附錄圖（會在附錄頁渲染）
        result_lines.append('')
        result_lines.append(f'<!-- Appendix Figure {appendix_fig_index + 1}: {appendix_info["title"]} -->')
        result_lines.append(f'<fig id="{fig_id}" ratio="16:9" kind="{kind}" alt="{alt}" />')

        appendix_fig_index += 1

    return '\n'.join(result_lines)


def extract_chart_data_from_diagrams(diagrams_md: str) -> dict:
    """
    從 diagrams.md 提取可用於圖表的數據

    用於識別折線圖、長條圖等需要原生 Chart 的情況

    Returns:
        dict: {fig_id: {chart_type, data}}
    """
    chart_data = {}

    # 尋找折線圖相關的描述
    line_chart_patterns = [
        r'折線圖',
        r'趨勢圖',
        r'line\s*chart',
        r'時間.*變化',
    ]

    for pattern in line_chart_patterns:
        if re.search(pattern, diagrams_md, re.IGNORECASE):
            # 嘗試提取數據點
            # 例如：「Q1: 100, Q2: 120, Q3: 140」
            data_match = re.search(
                r'(?:數據|data).*?[：:]\s*(.+?)(?:\n|$)',
                diagrams_md,
                re.IGNORECASE
            )
            if data_match:
                chart_data["line_chart"] = {
                    "type": "line",
                    "raw_data": data_match.group(1)
                }

    return chart_data


def convert_files(
    one_page_path: str,
    diagrams_path: str,
    output_path: str,
    content_output_path: Optional[str] = None
) -> dict:
    """
    轉換 Phase 5 檔案到 mcp-yogalayout 格式

    Args:
        one_page_path: one_page.md 路徑
        diagrams_path: diagrams.md 路徑
        output_path: 輸出的 yoga markdown 路徑
        content_output_path: 輸出的 content.json 路徑（可選）

    Returns:
        dict: {
            "yoga_md_path": str,
            "content_json_path": str (if content_output_path provided),
            "diagrams_info": dict
        }
    """
    # 讀取檔案
    with open(one_page_path, 'r', encoding='utf-8') as f:
        one_page_md = f.read()

    with open(diagrams_path, 'r', encoding='utf-8') as f:
        diagrams_md = f.read()

    # 解析 diagrams.md
    diagrams_info = parse_diagrams_spec(diagrams_md)

    # 轉換為 yoga 格式
    yoga_md = convert_one_page_to_yoga(one_page_md, diagrams_info)

    # 寫入輸出
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(yoga_md)

    result = {
        "yoga_md_path": output_path,
        "diagrams_info": diagrams_info
    }

    # 如果指定了 content.json 輸出路徑
    if content_output_path:
        # 提取圖表數據，供渲染時使用
        chart_data = extract_chart_data_from_diagrams(diagrams_md)

        content_data = {
            "diagrams": diagrams_info,
            "chart_data": chart_data,
            "source_files": {
                "one_page": one_page_path,
                "diagrams": diagrams_path
            }
        }

        with open(content_output_path, 'w', encoding='utf-8') as f:
            json.dump(content_data, f, ensure_ascii=False, indent=2)

        result["content_json_path"] = content_output_path

    return result


def main():
    parser = argparse.ArgumentParser(
        description='Convert Phase 5 markdown to mcp-yogalayout format'
    )
    parser.add_argument(
        '--one-page',
        required=True,
        help='Path to one_page.md'
    )
    parser.add_argument(
        '--diagrams',
        required=True,
        help='Path to diagrams.md'
    )
    parser.add_argument(
        '--output',
        required=True,
        help='Output path for yoga markdown'
    )
    parser.add_argument(
        '--content-json',
        help='Output path for content.json (optional)'
    )

    args = parser.parse_args()

    result = convert_files(
        args.one_page,
        args.diagrams,
        args.output,
        args.content_json
    )

    print(f"Converted: {result['yoga_md_path']}")
    if 'content_json_path' in result:
        print(f"Content JSON: {result['content_json_path']}")

    print(f"\nDiagrams found:")
    if result['diagrams_info'].get('main'):
        main_info = result['diagrams_info']['main']
        print(f"  Main: {main_info['title']} ({main_info['type']})")
    for i, appendix in enumerate(result['diagrams_info'].get('appendix', [])):
        print(f"  Appendix {i+1}: {appendix['title']} ({appendix['type']})")


if __name__ == '__main__':
    main()
