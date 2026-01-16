"""
元素追蹤與排版審查系統
用於檢測投影片上元素是否重疊
"""

# 全域元素追蹤清單（按投影片分組）
slide_elements = {}  # {slide_index: [{"name": ..., "type": ..., "left": ..., "top": ..., "right": ..., "bottom": ...}, ...]}
current_slide_index = 0


def reset_element_tracker():
    """重置元素追蹤清單"""
    global slide_elements, current_slide_index
    slide_elements = {}
    current_slide_index = 0


def set_current_slide(index):
    """設定當前投影片索引"""
    global current_slide_index
    current_slide_index = index
    if index not in slide_elements:
        slide_elements[index] = []


def track_element(name, left, top, width, height, element_type="generic"):
    """
    追蹤元素位置

    Args:
        name: 元素名稱（用於識別）
        left, top: 左上角位置（吋）
        width, height: 寬高（吋）
        element_type: 元素類型 ("text", "diagram", "card", "background")
    """
    global slide_elements, current_slide_index

    if current_slide_index not in slide_elements:
        slide_elements[current_slide_index] = []

    slide_elements[current_slide_index].append({
        "name": name,
        "type": element_type,
        "left": left,
        "top": top,
        "right": left + width,
        "bottom": top + height
    })


def boxes_overlap(box1, box2):
    """
    檢查兩個元素是否重疊

    Args:
        box1, box2: {"left": float, "top": float, "right": float, "bottom": float}

    Returns:
        bool: 是否重疊
    """
    return not (
        box1["right"] <= box2["left"] or   # box1 在 box2 左邊
        box1["left"] >= box2["right"] or   # box1 在 box2 右邊
        box1["bottom"] <= box2["top"] or   # box1 在 box2 上方
        box1["top"] >= box2["bottom"]      # box1 在 box2 下方
    )


def calculate_overlap_area(box1, box2):
    """計算兩個元素的重疊面積"""
    if not boxes_overlap(box1, box2):
        return 0.0

    overlap_left = max(box1["left"], box2["left"])
    overlap_right = min(box1["right"], box2["right"])
    overlap_top = max(box1["top"], box2["top"])
    overlap_bottom = min(box1["bottom"], box2["bottom"])

    return (overlap_right - overlap_left) * (overlap_bottom - overlap_top)


def check_overlaps(slide_index):
    """
    檢查指定投影片上的元素是否有重疊

    Returns:
        list: 重疊的元素對 [{"element_a": ..., "element_b": ..., "overlap_area": ...}, ...]
    """
    if slide_index not in slide_elements:
        return []

    elements = slide_elements[slide_index]
    overlaps = []

    # 過濾掉背景元素
    non_bg_elements = [e for e in elements if e["type"] != "background"]

    for i in range(len(non_bg_elements)):
        for j in range(i + 1, len(non_bg_elements)):
            box1 = non_bg_elements[i]
            box2 = non_bg_elements[j]

            if boxes_overlap(box1, box2):
                overlap_area = calculate_overlap_area(box1, box2)
                overlaps.append({
                    "element_a": box1,
                    "element_b": box2,
                    "overlap_area": overlap_area
                })

    return overlaps


def layout_review(max_rounds=2):
    """
    執行排版審查

    Args:
        max_rounds: 最大審查輪數

    Returns:
        dict: 審查結果 {"passed": bool, "rounds": int, "total_overlaps": int, "details": [...]}
    """
    print(f"\n{'='*50}")
    print(f"開始排版審查（最多 {max_rounds} 輪）")
    print(f"{'='*50}")

    all_details = []
    total_overlaps = 0

    for slide_idx in slide_elements:
        overlaps = check_overlaps(slide_idx)
        element_count = len([e for e in slide_elements[slide_idx] if e["type"] != "background"])

        print(f"\n投影片 {slide_idx + 1}:")
        print(f"  檢查元素數量：{element_count}")
        print(f"  偵測到重疊：{len(overlaps)} 處")

        if overlaps:
            total_overlaps += len(overlaps)
            for idx, overlap in enumerate(overlaps, 1):
                ea = overlap["element_a"]
                eb = overlap["element_b"]
                area = overlap["overlap_area"]

                detail = {
                    "slide": slide_idx + 1,
                    "element_a": ea["name"],
                    "element_b": eb["name"],
                    "overlap_area": area
                }
                all_details.append(detail)

                print(f"\n  重疊 {idx}:")
                print(f"    「{ea['name']}」與「{eb['name']}」重疊")
                print(f"    - {ea['name']}: ({ea['left']:.2f}, {ea['top']:.2f}) - ({ea['right']:.2f}, {ea['bottom']:.2f})")
                print(f"    - {eb['name']}: ({eb['left']:.2f}, {eb['top']:.2f}) - ({eb['right']:.2f}, {eb['bottom']:.2f})")
                print(f"    - 重疊面積：{area:.3f} 平方吋")

    print(f"\n{'='*50}")
    if total_overlaps == 0:
        print("排版審查通過！無重疊")
        print(f"{'='*50}\n")
        return {"passed": True, "rounds": 1, "total_overlaps": 0, "details": []}
    else:
        print(f"排版審查完成：發現 {total_overlaps} 處重疊")
        print("請手動調整元素位置以消除重疊")
        print(f"{'='*50}\n")
        return {"passed": False, "rounds": 1, "total_overlaps": total_overlaps, "details": all_details}
