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


def parse_diagram_content(diagram_section: str, diagram_type: str) -> dict:
    """
    解析圖表內容區塊，提取結構化渲染資料

    Args:
        diagram_section: 圖表的 Markdown 區塊
        diagram_type: 圖表類型 (before_after, flow, platform_compare, timeline, comparison)

    Returns:
        dict: 結構化的圖表內容
    """
    content = {"type": diagram_type}

    # 提取「圖表內容」區塊
    # 因為 code block 內可能有 --- 等字符，直接使用貪婪模式匹配到結尾
    content_match = re.search(r'### 圖表內容\s*\n([\s\S]+)', diagram_section)
    if not content_match:
        return content

    content_block = content_match.group(1).strip()

    if diagram_type == "before_after":
        content.update(_parse_before_after_content(content_block))
    elif diagram_type == "flow":
        content.update(_parse_flow_content(content_block))
    elif diagram_type == "platform_compare":
        content.update(_parse_platform_compare_content(content_block))
    elif diagram_type == "timeline":
        content.update(_parse_timeline_content(content_block))
    elif diagram_type in ("comparison", "architecture"):
        content.update(_parse_comparison_content(content_block))

    return content


def _parse_before_after_content(content_block: str) -> dict:
    """解析 before_after 類型的內容"""
    result = {"before": {}, "after": {}}

    # 分割 Before 和 After 區塊
    before_match = re.search(r'\*\*Before[^*]*\*\*\s*\n([\s\S]+?)(?=\*\*After|\Z)', content_block)
    after_match = re.search(r'\*\*After[^*]*\*\*\s*\n([\s\S]+?)(?=\n---|\Z)', content_block)

    if before_match:
        before_block = before_match.group(1)
        result["before"]["title"] = "改善前"

        # 提取流程（從 ``` 區塊或 -> 連接的文字）
        code_match = re.search(r'```\s*\n([\s\S]+?)\n```', before_block)
        if code_match:
            flow_text = code_match.group(1).strip()
            # 解析箭頭連接的流程
            nodes = re.split(r'\s*->\s*', flow_text.split('\n')[0])
            result["before"]["flow"] = [n.strip().strip('[]') for n in nodes if n.strip()]

        # 提取重點標注
        annotations = []
        for line in before_block.split('\n'):
            if line.strip().startswith('- '):
                annotations.append(line.strip()[2:])
        result["before"]["annotations"] = annotations

    if after_match:
        after_block = after_match.group(1)
        result["after"]["title"] = "改善後"

        code_match = re.search(r'```\s*\n([\s\S]+?)\n```', after_block)
        if code_match:
            flow_text = code_match.group(1).strip()
            nodes = re.split(r'\s*->\s*', flow_text.split('\n')[0])
            result["after"]["flow"] = [n.strip().strip('[]') for n in nodes if n.strip()]

        annotations = []
        for line in after_block.split('\n'):
            if line.strip().startswith('- '):
                annotations.append(line.strip()[2:])
        result["after"]["annotations"] = annotations

    return result


def _parse_flow_content(content_block: str) -> dict:
    """解析 flow 類型的內容 - 支援多階段格式"""
    result = {"stages": []}

    # diagrams.md 格式：一行可能包含多個階段（用多個空格分隔）
    # 例如：「第一階段：輸入捕獲                第二階段：引擎處理」

    # 先找所有階段標題（可能在同一行或不同行）
    stage_titles = {}  # {序號: 標題}
    stage_order = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]

    for line in content_block.split('\n'):
        # 找這一行中所有的「第X階段」
        matches = re.findall(r'第([一二三四五六七八九十\d]+)階段[：:]\s*([^\s第]+(?:\s*[^\s第]+)?)', line)
        for stage_num, stage_title in matches:
            stage_titles[stage_num] = stage_title.strip()

    # 解析 ASCII 圖表中的區塊
    code_match = re.search(r'```\s*\n([\s\S]+?)\n```', content_block)
    if code_match:
        ascii_art = code_match.group(1)

        # 把 ASCII 圖分成左右兩半（根據空格列分割）
        lines = ascii_art.split('\n')

        # 找出所有 +----+ 區塊並提取內容
        all_blocks = []
        current_block = []
        in_block = False

        for line in lines:
            if '+--' in line and '--+' in line:
                if in_block and current_block:
                    all_blocks.append(current_block)
                    current_block = []
                in_block = True
            elif in_block and '|' in line:
                # 提取 | xxx | 中的內容
                content = re.findall(r'\|\s*([^|]+)\s*\|', line)
                for c in content:
                    text = c.strip()
                    # 過濾掉純裝飾行
                    if text and text != 'v' and not text.startswith('-') and len(text) > 1:
                        current_block.append(text)

        if current_block:
            all_blocks.append(current_block)

        # 把區塊分配給各階段
        if stage_titles:
            for i, (num, title) in enumerate(sorted(stage_titles.items(),
                    key=lambda x: stage_order.index(x[0]) if x[0] in stage_order else int(x[0]))):
                stage = {"title": title, "nodes": []}
                # 嘗試找對應的區塊
                if i < len(all_blocks):
                    stage["nodes"] = all_blocks[i][:6]
                result["stages"].append(stage)
        else:
            # 沒找到階段標題，用區塊建立節點列表
            nodes = []
            for block in all_blocks:
                nodes.extend(block)
            result["nodes"] = nodes[:8]

    # 同時提取「每階段標註」區塊的內容
    annotations = []
    for line in content_block.split('\n'):
        if line.strip().startswith('- 第') and '階段' in line:
            annotations.append(line.strip()[2:])
    if annotations:
        result["annotations"] = annotations

    return result


def _parse_platform_compare_content(content_block: str) -> dict:
    """解析 platform_compare 類型的內容"""
    result = {"platform1": {}, "platform2": {}, "rows": []}

    # 找平台標題
    platforms = re.findall(r'(PC|Android|Windows|iOS)[^)]*\)', content_block)
    if len(platforms) >= 2:
        result["platform1"]["title"] = platforms[0]
        result["platform2"]["title"] = platforms[1]

    # 找對比行（包含 OK、X、# 等符號的行）
    for line in content_block.split('\n'):
        if any(sym in line for sym in ['OK ', 'X ', '# ', '* ']):
            # 清理並提取內容
            clean_line = line.strip()
            if clean_line:
                result["rows"].append(clean_line)

    return result


def _parse_timeline_content(content_block: str) -> dict:
    """解析 timeline 類型的內容 - 支援橫向時間軸"""
    result = {"points": [], "dimensions": []}

    # diagrams.md 格式是橫向時間軸：
    #   T0           T1              T2              T3              T4
    #   v            v               v               v               v
    # 觸控事件    引擎讀取輸入    GPU 開始渲染    SurfaceFlinger    螢幕像素

    lines = content_block.split('\n')

    # 找包含 T0, T1, T2... 的行
    time_line = None
    time_line_idx = -1
    for i, line in enumerate(lines):
        if re.search(r'\bT\d+\b.*\bT\d+\b', line):  # 至少有兩個 TX
            time_line = line
            time_line_idx = i
            break

    if time_line and time_line_idx >= 0:
        # 提取時間點
        time_points = re.findall(r'(T\d+)', time_line)

        # 跳過箭頭行（v 或 |），找描述行
        desc_line = None
        for i in range(time_line_idx + 1, min(time_line_idx + 5, len(lines))):
            line = lines[i].strip()
            if line and not re.match(r'^[|v\s]+$', line):
                desc_line = lines[i]
                break

        if desc_line:
            # 根據位置對應時間點和描述
            # 用空格分割描述（多個空格作為分隔符）
            descriptions = re.split(r'\s{2,}', desc_line.strip())
            descriptions = [d.strip() for d in descriptions if d.strip()]

            for j, tp in enumerate(time_points):
                desc = descriptions[j] if j < len(descriptions) else ""
                result["points"].append({"time": tp, "desc": desc})

    # 解析 POC 三維度
    # 找「系統延遲」「1% Low」「功耗」相關的區塊
    dimension_keywords = ["系統延遲", "Low FPS", "1% Low", "功耗", "延遲", "FPS", "功耗行為"]

    for keyword in dimension_keywords:
        if keyword in content_block:
            # 找包含該關鍵字的區塊
            for line in lines:
                if keyword in line:
                    # 提取該區塊的關鍵信息
                    clean = re.sub(r'[|+\-=]', '', line).strip()
                    if clean and clean not in result["dimensions"]:
                        result["dimensions"].append(clean)
                        break

    # 如果沒找到，嘗試從 ASCII 方框中提取
    if not result["dimensions"]:
        box_content = re.findall(r'\|\s*([^|]{3,}?)\s*\|', content_block)
        for c in box_content:
            text = c.strip()
            if text and any(kw in text for kw in ["延遲", "FPS", "功耗", "目標", "量測", "Pass"]):
                result["dimensions"].append(text)

    return result


def _parse_comparison_content(content_block: str) -> dict:
    """解析 comparison/architecture 類型的內容 - 支援左右對比格式"""
    result = {"left": {"title": "", "features": []}, "right": {"title": "", "features": []}, "features": []}

    lines = content_block.split('\n')

    # 找標題行（包含 vs 或左右並排的標題）
    # 格式：「Unity (低延遲模式)                    Unreal (高吞吐模式)」
    for line in lines:
        # 跳過標題裝飾行
        if line.strip().startswith('+') or line.strip().startswith('|'):
            continue
        if 'Unity' in line and 'Unreal' in line:
            # 左右並排的標題
            parts = re.split(r'\s{4,}', line)  # 用多個空格分割
            if len(parts) >= 2:
                result["left"]["title"] = parts[0].strip()
                result["right"]["title"] = parts[1].strip()
            break

    # 如果沒找到標題，嘗試其他模式
    if not result["left"]["title"]:
        for line in lines:
            if 'Unity' in line and '(' in line and not line.strip().startswith('+'):
                match = re.search(r'(Unity[^)]*\))', line)
                if match:
                    result["left"]["title"] = match.group(1)
            if 'Unreal' in line and '(' in line and not line.strip().startswith('+'):
                match = re.search(r'(Unreal[^)]*\))', line)
                if match:
                    result["right"]["title"] = match.group(1)

    # 如果還是沒找到，用簡單名稱
    if not result["left"]["title"]:
        result["left"]["title"] = "Unity"
    if not result["right"]["title"]:
        result["right"]["title"] = "Unreal"

    # 找「特性：」區塊並提取列表（注意可能在 code block 內）
    # 格式：
    # 特性：                                特性：
    # - 緩衝區較淺 (Double Buffer)          - 多幀管線 (Pipelined)

    left_features = []
    right_features = []
    in_feature_block = False

    for line in lines:
        if '特性：' in line or '特性:' in line:
            in_feature_block = True
            continue

        if in_feature_block:
            if line.strip().startswith('- '):
                # 檢查是否有左右兩個特性（用多個空格分隔）
                parts = re.split(r'\s{4,}', line)
                if len(parts) >= 2:
                    left_item = parts[0].strip()
                    right_item = parts[1].strip()
                    if left_item.startswith('- '):
                        left_features.append(left_item[2:].strip())
                    if right_item.startswith('- '):
                        right_features.append(right_item[2:].strip())
                else:
                    # 單一特性
                    item = line.strip()[2:].strip()
                    if item:
                        left_features.append(item)

            elif 'Anti-Lag' in line or '預期效果' in line:
                # 進入預期效果區塊，繼續收集
                continue
            elif line.strip().startswith('```'):
                # code block 結束
                break
            elif line.strip() and not line.strip().startswith('-') and not line.strip().startswith('|') and not line.strip().startswith('+'):
                # 非列表行，可能是區塊結束
                if '特性' not in line and 'Anti-Lag' not in line and '預期' not in line:
                    in_feature_block = False

    result["left"]["features"] = left_features[:4]
    result["right"]["features"] = right_features[:4]

    # 合併所有特性到 features（向後兼容）
    all_features = []
    left_title = result["left"]["title"].split('(')[0].strip() if result["left"]["title"] else "Left"
    right_title = result["right"]["title"].split('(')[0].strip() if result["right"]["title"] else "Right"

    for lf, rf in zip(left_features, right_features):
        all_features.append(f"{left_title}: {lf}")
        all_features.append(f"{right_title}: {rf}")

    # 如果沒有成對的，就用 left_features
    if not all_features:
        all_features = left_features + right_features

    result["features"] = all_features[:8]

    return result


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
    mode: str = "one_page",
    diagrams_structured_path: Optional[str] = None
) -> dict:
    """
    轉換 Phase 5 檔案到 mcp-yogalayout 格式

    Args:
        one_page_path: one_page.md 路徑
        diagrams_path: diagrams.md 路徑
        output_path: 輸出的 yoga markdown 路徑
        content_output_path: 輸出的 content.json 路徑（可選）
        mode: "one_page" 或 "multi_page"
        diagrams_structured_path: AI 預處理過的結構化圖表 JSON 路徑（可選）
            如果提供，將直接使用此 JSON 的 diagrams 欄位作為 diagrams_content，
            跳過從 diagrams.md 解析內容的步驟

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
        diagrams_content = {}  # 結構化圖表內容
        total_count = 0

        # 檢查是否有 AI 預處理過的結構化 JSON
        structured_diagrams = None
        if diagrams_structured_path:
            try:
                with open(diagrams_structured_path, 'r', encoding='utf-8') as f:
                    structured_data = json.load(f)
                    structured_diagrams = structured_data.get("diagrams", {})
                    print(f"[yoga_converter] 載入結構化圖表 JSON: {diagrams_structured_path}")
                    print(f"[yoga_converter] 包含 {len(structured_diagrams)} 個圖表")
            except Exception as e:
                print(f"[yoga_converter] 警告：無法載入結構化 JSON，將使用 diagrams.md 解析: {e}")
                structured_diagrams = None

        # 分割 diagrams.md 成區塊，用於解析詳細內容（當沒有結構化 JSON 時使用）
        diagram_sections = re.split(r'^## ', diagrams_md, flags=re.MULTILINE) if not structured_diagrams else []

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

            # 優先使用結構化 JSON，否則從 diagrams.md 解析
            if structured_diagrams and fig_id in structured_diagrams:
                diagrams_content[fig_id] = structured_diagrams[fig_id]
                print(f"[yoga_converter] 使用結構化資料: {fig_id}")
            else:
                # 找到對應的區塊並解析內容
                for section in diagram_sections:
                    if '主圖' in section:
                        content = parse_diagram_content(section, main["type"])
                        diagrams_content[fig_id] = content
                        break

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

            # 優先使用結構化 JSON，否則從 diagrams.md 解析
            if structured_diagrams and fig_id in structured_diagrams:
                diagrams_content[fig_id] = structured_diagrams[fig_id]
                print(f"[yoga_converter] 使用結構化資料: {fig_id}")
            else:
                # 找到對應的區塊並解析內容
                appendix_num = i + 1
                for section in diagram_sections:
                    if f'附錄圖 {appendix_num}' in section or f'附錄圖{appendix_num}' in section:
                        content = parse_diagram_content(section, appendix["type"])
                        diagrams_content[fig_id] = content
                        break

        content_data = {
            "diagrams_info": diagrams_list,  # 供渲染驗證使用
            "diagrams_content": diagrams_content,  # 新增：結構化圖表內容
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
    parser.add_argument(
        '--diagrams-structured',
        help='Path to AI pre-processed structured diagrams JSON (optional). '
             'If provided, will use this instead of parsing diagrams.md'
    )

    args = parser.parse_args()

    result = convert_files(
        args.one_page,
        args.diagrams,
        args.output,
        args.content_json,
        args.mode,
        getattr(args, 'diagrams_structured', None)
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
