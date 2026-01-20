# -*- coding: utf-8 -*-
"""
Yoga Converter v2.0: 將 Phase 5 的 one_page.md + diagrams.md 轉換為 mcp-yogalayout 格式

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

v2.0 改進（真正的 One Page）：
- 所有附錄圖都嵌入報告中，讓 yogalayout 統一計算佈局
- 根據圖表數量動態調整 ratio，讓更多內容塞入一頁
- 智慧地決定每張圖的插入位置（基於內容相關性）
"""

import re
import os
import json
import argparse
from pathlib import Path
from typing import Optional, List, Dict, Tuple


# 圖表類型與適合的 ratio 對應（預設使用緊湊型）
DIAGRAM_RATIOS = {
    "before_after": "21:9",      # 前後對比：寬扁型
    "platform_compare": "21:9",  # 平台對比：寬扁型
    "flow": "21:9",              # 流程圖：寬扁型
    "timeline": "21:9",          # 時間軸：寬扁型
    "architecture": "3:1",       # 架構圖：極扁型
    "comparison": "21:9",        # 比較圖：寬扁型
    "default": "16:9",           # 預設
}

# 當圖表數量多時，使用更緊湊的 ratio
COMPACT_RATIOS = {
    "before_after": "3:1",
    "platform_compare": "3:1",
    "flow": "3:1",
    "timeline": "3:1",
    "architecture": "4:1",
    "comparison": "3:1",
    "default": "21:9",
}

# 圖表類型與適合插入的區塊關鍵字
DIAGRAM_INSERTION_HINTS = {
    "before_after": ["改善", "效果", "對比", "前後", "優化", "效益", "預期"],
    "platform_compare": ["平台", "PC", "Android", "對照", "差異", "比較", "對照表"],
    "flow": ["流程", "步驟", "鏈路", "路徑", "全鏈路", "Pipeline", "觸控"],
    "timeline": ["延遲", "時間", "量測", "指標", "成功判定", "POC", "判定"],
    "architecture": ["架構", "系統", "模組", "組件", "引擎", "Unity", "Unreal"],
    "comparison": ["比較", "差異", "對比", "Unity", "Unreal", "引擎"],
}


def parse_diagrams_spec(diagrams_md: str) -> dict:
    """
    解析 diagrams.md，提取圖表規格

    Returns:
        dict: {
            "main": {"title": "...", "type": "...", "description": "...", "size": "..."},
            "appendix": [{"title": "...", "type": "...", "description": "...", "size": "..."}, ...]
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

        # 解析類型和尺寸
        diagram_type = "diagram"  # 預設
        description = ""
        size = ""

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
            elif line.startswith('- **尺寸**：'):
                size_match = re.search(r'- \*\*尺寸\*\*：(.+)', line)
                if size_match:
                    size = size_match.group(1)

        # 嘗試從內容區塊提取更詳細的描述
        content_match = re.search(r'### 圖表內容\s*\n([\s\S]+?)(?=\n---|\n## |$)', section)
        if content_match and not description:
            content = content_match.group(1).strip()
            # 取第一段作為描述
            first_para = content.split('\n\n')[0]
            description = first_para[:150].replace('\n', ' ')

        diagram_info = {
            "title": title_line.replace('主圖：', '').replace('附錄圖', '').strip(),
            "type": diagram_type,
            "description": description,
            "size": size,
            "original_title": title_line.strip()
        }

        if '主圖' in title_line:
            diagrams["main"] = diagram_info
        elif '附錄圖' in title_line:
            diagrams["appendix"].append(diagram_info)

    return diagrams


def convert_diagram_type_to_kind(diagram_type: str) -> str:
    """
    將 diagrams.md 的類型轉換為 mcp-yogalayout 的 kind
    """
    shape_types = {'before_after', 'platform_compare', 'flow', 'timeline', 'architecture', 'comparison'}
    chart_types = {'line_chart', 'bar_chart', 'pie_chart', 'area_chart'}

    if diagram_type in shape_types:
        return "diagram"
    elif diagram_type in chart_types:
        return "chart"
    else:
        return "diagram"


def get_ratio_for_diagram(diagram_type: str, total_diagrams: int) -> str:
    """
    根據圖表類型和總數決定 ratio

    Args:
        diagram_type: 圖表類型
        total_diagrams: 總圖表數量

    Returns:
        ratio: 例如 "16:9", "21:9", "3:1"
    """
    # 如果圖表多於 3 張，使用更緊湊的 ratio
    if total_diagrams > 3:
        return COMPACT_RATIOS.get(diagram_type, COMPACT_RATIOS["default"])
    else:
        return DIAGRAM_RATIOS.get(diagram_type, DIAGRAM_RATIOS["default"])


def generate_fig_id(title: str, index: int = 0, prefix: str = "") -> str:
    """
    根據標題生成 fig id
    """
    # 移除中文，只保留英文和數字
    ascii_title = re.sub(r'[^\x00-\x7F]+', '', title).strip()

    if ascii_title:
        fig_id = re.sub(r'\s+', '_', ascii_title.lower())
        fig_id = re.sub(r'[^a-z0-9_]', '', fig_id)
        fig_id = fig_id[:20] if fig_id else f"fig{index}"
    else:
        fig_id = f"fig{index}"

    if prefix:
        fig_id = f"{prefix}:{fig_id}"

    return fig_id


def find_best_insertion_point(lines: List[str], diagram_type: str, used_positions: set) -> int:
    """
    找到最適合插入圖表的位置

    Args:
        lines: Markdown 行列表
        diagram_type: 圖表類型
        used_positions: 已使用的位置集合

    Returns:
        最佳插入位置（行索引）
    """
    hints = DIAGRAM_INSERTION_HINTS.get(diagram_type, [])
    best_pos = -1
    best_score = 0

    for i, line in enumerate(lines):
        if i in used_positions:
            continue

        if line.startswith('## '):
            section_title = line[3:].strip()
            score = 0

            for hint in hints:
                if hint in section_title:
                    score += 10

            # 找到該區塊的結尾（下一個 ## 或檔案結尾）
            end_pos = len(lines)
            for j in range(i + 1, len(lines)):
                if lines[j].startswith('## '):
                    end_pos = j
                    break

            # 在區塊內部搜尋關鍵字
            for j in range(i, end_pos):
                for hint in hints:
                    if hint in lines[j]:
                        score += 1

            if score > best_score:
                best_score = score
                # 插入在區塊結尾前
                best_pos = end_pos

    return best_pos if best_pos > 0 else len(lines)


def convert_one_page_to_yoga(one_page_md: str, diagrams: dict, mode: str = "one_page") -> str:
    """
    將 one_page.md 轉換為 mcp-yogalayout 格式

    Args:
        one_page_md: Phase 5 的 one_page.md 內容
        diagrams: parse_diagrams_spec 的輸出
        mode: "one_page" (盡量塞一頁) 或 "multi_page" (主圖一頁、附錄另頁)

    Returns:
        yoga_md: mcp-yogalayout 格式的 Markdown
    """
    lines = one_page_md.split('\n')
    result_lines = lines.copy()

    # 計算總圖表數
    total_diagrams = (1 if diagrams.get("main") else 0) + len(diagrams.get("appendix", []))

    # 追蹤已使用的插入位置
    used_positions = set()
    insertions = []  # (position, fig_tag)

    # 處理主圖
    if diagrams.get("main"):
        main_info = diagrams["main"]
        fig_id = generate_fig_id(main_info["title"], 0, "main")
        kind = convert_diagram_type_to_kind(main_info["type"])
        ratio = get_ratio_for_diagram(main_info["type"], total_diagrams)
        alt = main_info["description"][:100] if main_info["description"] else main_info["title"]

        # 找最佳插入位置
        pos = find_best_insertion_point(result_lines, main_info["type"], used_positions)
        fig_tag = f'\n<fig id="{fig_id}" ratio="{ratio}" kind="{kind}" alt="{alt}" />\n'

        insertions.append((pos, fig_tag, "main"))
        used_positions.add(pos)

    # 處理附錄圖
    if mode == "one_page":
        # One Page 模式：所有圖都嵌入報告中
        for i, appendix_info in enumerate(diagrams.get("appendix", [])):
            fig_id = generate_fig_id(appendix_info["title"], i + 1, "appendix")
            kind = convert_diagram_type_to_kind(appendix_info["type"])
            ratio = get_ratio_for_diagram(appendix_info["type"], total_diagrams)
            alt = appendix_info["description"][:100] if appendix_info["description"] else appendix_info["title"]

            # 找最佳插入位置
            pos = find_best_insertion_point(result_lines, appendix_info["type"], used_positions)
            fig_tag = f'\n<fig id="{fig_id}" ratio="{ratio}" kind="{kind}" alt="{alt}" />\n'

            insertions.append((pos, fig_tag, f"appendix_{i}"))
            used_positions.add(pos)

    # 按位置排序（從後往前插入，避免位置偏移）
    insertions.sort(key=lambda x: x[0], reverse=True)

    for pos, fig_tag, label in insertions:
        if pos >= len(result_lines):
            result_lines.append(fig_tag)
        else:
            result_lines.insert(pos, fig_tag)

    # Multi Page 模式：附錄圖放在文件末尾，用分隔符標記
    if mode == "multi_page" and diagrams.get("appendix"):
        result_lines.append('\n\n---\n\n## 附錄圖表\n')

        for i, appendix_info in enumerate(diagrams.get("appendix", [])):
            fig_id = generate_fig_id(appendix_info["title"], i + 1, "appendix")
            kind = convert_diagram_type_to_kind(appendix_info["type"])
            ratio = "16:9"  # Multi page 可以用較大的 ratio
            alt = appendix_info["description"][:100] if appendix_info["description"] else appendix_info["title"]

            result_lines.append(f'\n### {appendix_info["original_title"]}')
            result_lines.append(f'<fig id="{fig_id}" ratio="{ratio}" kind="{kind}" alt="{alt}" />\n')

    return '\n'.join(result_lines)


def extract_chart_data_from_diagrams(diagrams_md: str) -> dict:
    """
    從 diagrams.md 提取可用於圖表的數據
    """
    chart_data = {}

    line_chart_patterns = [
        r'折線圖',
        r'趨勢圖',
        r'line\s*chart',
        r'時間.*變化',
    ]

    for pattern in line_chart_patterns:
        if re.search(pattern, diagrams_md, re.IGNORECASE):
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
    content_output_path: Optional[str] = None,
    mode: str = "one_page"
) -> dict:
    """
    轉換 Phase 5 檔案到 mcp-yogalayout 格式

    Args:
        one_page_path: one_page.md 路徑
        diagrams_path: diagrams.md 路徑
        output_path: 輸出的 yoga markdown 路徑
        content_output_path: 輸出的 content.json 路徑（可選）
        mode: "one_page" 或 "multi_page"

    Returns:
        dict: 轉換結果
    """
    with open(one_page_path, 'r', encoding='utf-8') as f:
        one_page_md = f.read()

    with open(diagrams_path, 'r', encoding='utf-8') as f:
        diagrams_md = f.read()

    diagrams_info = parse_diagrams_spec(diagrams_md)
    yoga_md = convert_one_page_to_yoga(one_page_md, diagrams_info, mode)

    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(yoga_md)

    result = {
        "yoga_md_path": output_path,
        "diagrams_info": diagrams_info,
        "mode": mode,
        "total_diagrams": (1 if diagrams_info.get("main") else 0) + len(diagrams_info.get("appendix", []))
    }

    if content_output_path:
        chart_data = extract_chart_data_from_diagrams(diagrams_md)

        # 產生 diagrams_info 列表，方便驗證時使用
        diagrams_list = []
        total_count = 0

        if diagrams_info.get("main"):
            main = diagrams_info["main"]
            fig_id = generate_fig_id(main["title"], 0, "main")
            diagrams_list.append({
                "id": fig_id,
                "kind": convert_diagram_type_to_kind(main["type"]),
                "type": main["type"],
                "title": main["title"],
                "description": main.get("description", "")
            })
            total_count += 1

        for i, appendix in enumerate(diagrams_info.get("appendix", [])):
            fig_id = generate_fig_id(appendix["title"], i + 1, "appendix")
            diagrams_list.append({
                "id": fig_id,
                "kind": convert_diagram_type_to_kind(appendix["type"]),
                "type": appendix["type"],
                "title": appendix["title"],
                "description": appendix.get("description", "")
            })
            total_count += 1

        content_data = {
            "diagrams_info": diagrams_list,  # 供渲染驗證使用
            "total_diagrams": total_count,
            "diagrams_raw": diagrams_info,   # 原始解析結果
            "chart_data": chart_data,
            "source_files": {
                "one_page": one_page_path,
                "diagrams": diagrams_path
            },
            "mode": mode
        }

        with open(content_output_path, 'w', encoding='utf-8') as f:
            json.dump(content_data, f, ensure_ascii=False, indent=2)

        result["content_json_path"] = content_output_path

    return result


def main():
    parser = argparse.ArgumentParser(
        description='Convert Phase 5 markdown to mcp-yogalayout format (v2.0)'
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
    parser.add_argument(
        '--mode',
        choices=['one_page', 'multi_page'],
        default='one_page',
        help='Layout mode: one_page (pack everything) or multi_page (appendix on separate pages)'
    )

    args = parser.parse_args()

    result = convert_files(
        args.one_page,
        args.diagrams,
        args.output,
        args.content_json,
        args.mode
    )

    print(f"Converted: {result['yoga_md_path']}")
    print(f"Mode: {result['mode']}")
    print(f"Total diagrams: {result['total_diagrams']}")

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
