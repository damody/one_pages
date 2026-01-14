#!/usr/bin/env python3
"""測試 SVG 轉 PNG - 多種方案"""

import os

def method1_cairosvg(svg_path, png_path):
    """方案 1: 使用 cairosvg（可能有中文字型問題）"""
    import cairosvg
    cairosvg.svg2png(
        url=svg_path,
        write_to=png_path,
        scale=2,
        background_color=None
    )
    return os.path.exists(png_path)


def method2_svglib(svg_path, png_path):
    """方案 2: 使用 svglib + reportlab（較好的字型支援）"""
    try:
        from svglib.svglib import svg2rlg
        from reportlab.graphics import renderPM

        drawing = svg2rlg(svg_path)
        if drawing:
            renderPM.drawToFile(drawing, png_path, fmt="PNG", dpi=144)
            return os.path.exists(png_path)
    except ImportError:
        print("需要安裝: pip install svglib reportlab")
    return False


def method3_inkscape(svg_path, png_path):
    """方案 3: 使用 Inkscape CLI（最佳字型支援，需安裝 Inkscape）"""
    import subprocess
    try:
        result = subprocess.run([
            'inkscape',
            svg_path,
            '--export-type=png',
            f'--export-filename={png_path}',
            '--export-dpi=192'
        ], capture_output=True, text=True)
        return os.path.exists(png_path)
    except FileNotFoundError:
        print("需要安裝 Inkscape 並加入 PATH")
    return False


if __name__ == '__main__':
    svg_file = 'test_chinese.svg'

    print("=" * 50)
    print("測試 SVG 轉 PNG（繁體中文）")
    print("=" * 50)

    # 測試方案 1: cairosvg
    print("\n[方案 1] cairosvg:")
    png1 = 'output_cairosvg.png'
    if method1_cairosvg(svg_file, png1):
        print(f"  ✓ 產生: {png1}")
    else:
        print(f"  ✗ 失敗")

    # 測試方案 2: svglib
    print("\n[方案 2] svglib + reportlab:")
    png2 = 'output_svglib.png'
    if method2_svglib(svg_file, png2):
        print(f"  ✓ 產生: {png2}")
    else:
        print(f"  ✗ 失敗")

    # 測試方案 3: Inkscape
    print("\n[方案 3] Inkscape CLI:")
    png3 = 'output_inkscape.png'
    if method3_inkscape(svg_file, png3):
        print(f"  ✓ 產生: {png3}")
    else:
        print(f"  ✗ 失敗")

    print("\n" + "=" * 50)
    print("請開啟各 PNG 檔案比較中文顯示效果")
    print("=" * 50)
