# -*- coding: utf-8 -*-
"""
測試四張圖放到同一張投影片

解析 D:\mcp-yogalayout\examples\diagrams.md 並渲染：
1. 主圖：前後對比 (before_after)
2. 附錄圖1：平台對比 (platform_compare)
3. 附錄圖2：時間軸 (timeline)
4. 附錄圖3：架構圖 (architecture)
"""

import sys
from pathlib import Path

# 設定路徑
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

import win32com.client as win32
from modules_pywin32._colors_pywin32 import (
    COLOR_RED, COLOR_GREEN, COLOR_BLUE, COLOR_ORANGE, COLOR_GRAY,
    COLOR_GRAY_BG, COLOR_TEXT, COLOR_WHITE, COLOR_PINK, hex_to_bgr
)
from modules_pywin32._shapes_pywin32 import add_textbox, add_background
from modules_pywin32.draw_before_after_pywin32 import draw_before_after_with_vertical_flow
from modules_pywin32.draw_platform_compare_pywin32 import draw_platform_compare
from modules_pywin32.draw_timeline_pywin32 import draw_timeline
from modules_pywin32.draw_architecture_pywin32 import draw_architecture


def main():
    print("=" * 60)
    print("測試：四張圖放到同一張投影片")
    print("=" * 60)

    # 啟動 PowerPoint
    ppt = win32.Dispatch("PowerPoint.Application")
    ppt.Visible = True

    # 建立簡報
    prs = ppt.Presentations.Add()

    # 設定投影片大小為 16:9
    prs.PageSetup.SlideWidth = 960
    prs.PageSetup.SlideHeight = 540

    # 新增投影片
    slide = prs.Slides.Add(1, 12)  # ppLayoutBlank

    # 背景
    add_background(slide, 960, 540, hex_to_bgr("#FFF9E6"))

    # 標題
    add_textbox(slide, "Anti-Lag 技術概覽 - 四張圖表展示",
               20, 10, 920, 28,
               font_size=16, bold=True, color=COLOR_TEXT)

    # 佈局：2x2 四宮格
    # 左上：前後對比圖
    # 右上：平台對比圖
    # 左下：時間軸圖
    # 右下：架構圖

    margin = 20
    gap = 12
    cell_width = (960 - 2 * margin - gap) / 2
    cell_height = (540 - 45 - margin - gap) / 2

    # === 左上：前後對比圖 ===
    print("繪製：前後對比圖...")
    x1, y1 = margin, 45

    before_nodes = [
        {"title": "CPU 準備", "desc": "快速產生畫面"},
        {"title": "Frame Queue", "desc": "排了3-4幀", "highlight": True},
        {"title": "GPU 繪圖", "desc": "渲染畫面"},
    ]
    after_nodes = [
        {"title": "CPU 準備", "desc": "SDK 控制節奏"},
        {"title": "Frame Queue", "desc": "只有1幀"},
        {"title": "GPU 繪圖", "desc": "最新畫面"},
    ]

    draw_before_after_with_vertical_flow(
        slide, x1, y1, cell_width, cell_height,
        "改善前：延遲50-66ms", before_nodes,
        "改善後：延遲16ms", after_nodes,
        center_arrow_label="導入 SDK"
    )
    print("  ✓ 前後對比圖完成")

    # === 右上：平台對比圖 ===
    print("繪製：平台對比圖...")
    x2, y2 = margin + cell_width + gap, 45

    pc_nodes = [
        {"title": "滑鼠輸入", "desc": "csrss.exe"},
        {"title": "遊戲引擎", "desc": "SDK同步"},
        {"title": "GPU", "desc": "D3D12"},
        {"title": "顯示", "desc": "VRR"},
    ]
    android_nodes = [
        {"title": "觸控輸入", "desc": "InputReader"},
        {"title": "遊戲引擎", "desc": "待導入SDK"},
        {"title": "GPU", "desc": "Mali"},
        {"title": "顯示", "desc": "SF合成"},
    ]

    draw_platform_compare(
        slide, x2, y2, cell_width, cell_height,
        "PC: Windows 11 + Anti-Lag", pc_nodes,
        "手機: Android + 天璣", android_nodes,
        differences=[{"desc": "PC有SDK，手機待導入"}]
    )
    print("  ✓ 平台對比圖完成")

    # === 左下：時間軸圖 ===
    print("繪製：時間軸圖...")
    x3, y3 = margin, 45 + cell_height + gap

    timeline_events = [
        {"name": "觸控", "time": "T=0", "desc": "觸控IC"},
        {"name": "InputReader", "time": "T=2ms", "desc": "讀取事件", "duration": "2ms"},
        {"name": "遊戲處理", "time": "T=7ms", "desc": "遊戲邏輯", "duration": "5ms"},
        {"name": "GPU渲染", "time": "T=15ms", "desc": "渲染畫面", "duration": "8ms", "highlight": True},
        {"name": "SF合成", "time": "T=30ms", "desc": "合成圖層", "duration": "15ms", "highlight": True},
        {"name": "顯示", "time": "T=50ms", "desc": "像素發光"},
    ]

    draw_timeline(slide, x3, y3, cell_width, cell_height,
                 timeline_events, title="Android 觸控延遲鏈路")
    print("  ✓ 時間軸圖完成")

    # === 右下：架構圖 ===
    print("繪製：架構圖...")
    x4, y4 = margin + cell_width + gap, 45 + cell_height + gap

    arch_layers = [
        {
            "name": "應用層",
            "modules": [
                {"name": "和平菁英"},
                {"name": "鳴潮"},
            ]
        },
        {
            "name": "SDK 層（POC）",
            "color": hex_to_bgr("#FFF3E0"),
            "modules": [
                {"name": "Anti-Lag SDK", "highlight": True},
            ]
        },
        {
            "name": "框架層",
            "modules": [
                {"name": "SurfaceFlinger"},
                {"name": "FPSGO"},
            ]
        },
        {
            "name": "硬體層",
            "modules": [
                {"name": "天璣 SoC"},
                {"name": "Mali GPU"},
            ]
        },
    ]

    draw_architecture(slide, x4, y4, cell_width, cell_height,
                     arch_layers, title="MTK Anti-Lag SDK 架構")
    print("  ✓ 架構圖完成")

    # 儲存
    output_dir = SCRIPT_DIR / "test_output"
    output_dir.mkdir(exist_ok=True)
    output_path = str(output_dir / "four_diagrams.pptx")

    prs.SaveAs(output_path)
    print(f"\n已儲存：{output_path}")

    # 關閉
    prs.Close()
    ppt.Quit()

    print("\n" + "=" * 60)
    print("測試完成！PowerPoint 已自動關閉。")
    print("=" * 60)


if __name__ == "__main__":
    main()
