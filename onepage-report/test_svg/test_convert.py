#!/usr/bin/env python3
"""測試 SVG 轉 PNG 功能"""

import os
import cairosvg

def convert_svg_to_png(svg_path, png_path=None, scale=2):
    """將 SVG 轉換為透明背景的 PNG"""
    if png_path is None:
        png_path = svg_path.rsplit('.', 1)[0] + '.png'

    cairosvg.svg2png(
        url=svg_path,
        write_to=png_path,
        scale=scale,
        background_color=None  # 保持透明背景
    )
    print(f"✓ Converted: {os.path.basename(svg_path)} → {os.path.basename(png_path)}")
    return png_path


if __name__ == '__main__':
    # 轉換測試 SVG
    svg_file = 'test_diagram.svg'

    if os.path.exists(svg_file):
        png_file = convert_svg_to_png(svg_file)

        # 檢查輸出
        if os.path.exists(png_file):
            size = os.path.getsize(png_file)
            print(f"✓ PNG 檔案已產生: {png_file} ({size} bytes)")
        else:
            print("✗ PNG 檔案產生失敗")
    else:
        print(f"✗ 找不到 SVG 檔案: {svg_file}")
