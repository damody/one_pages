# -*- coding: utf-8 -*-
"""
pywin32 顏色常數與轉換函數（BGR 格式）

pywin32 COM API 使用 BGR 格式而非 RGB：
- RGB(255, 0, 0) 紅色 → BGR = 0x0000FF
- RGB(0, 255, 0) 綠色 → BGR = 0x00FF00
- RGB(0, 0, 255) 藍色 → BGR = 0xFF0000

轉換公式: BGR = R + (G << 8) + (B << 16)
"""


def rgb_to_bgr(r: int, g: int, b: int) -> int:
    """
    將 RGB 轉換為 BGR（pywin32 格式）

    Args:
        r: 紅色值 (0-255)
        g: 綠色值 (0-255)
        b: 藍色值 (0-255)

    Returns:
        BGR 格式的整數值
    """
    return r + (g << 8) + (b << 16)


def hex_to_bgr(hex_color: str) -> int:
    """
    將 #RRGGBB 轉換為 BGR

    Args:
        hex_color: 十六進位顏色字串，例如 "#FF0000" 或 "FF0000"

    Returns:
        BGR 格式的整數值
    """
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return rgb_to_bgr(r, g, b)


def bgr_to_hex(bgr: int) -> str:
    """
    將 BGR 轉換回 #RRGGBB 格式

    Args:
        bgr: BGR 格式的整數值

    Returns:
        十六進位顏色字串
    """
    r = bgr & 0xFF
    g = (bgr >> 8) & 0xFF
    b = (bgr >> 16) & 0xFF
    return f"#{r:02X}{g:02X}{b:02X}"


def get_text_color(bg_color: int) -> int:
    """
    根據背景色自動選擇對比文字色

    Args:
        bg_color: 背景色（BGR 格式）

    Returns:
        文字色（BGR 格式）- 深色背景返回白色，淺色背景返回深灰
    """
    r = bg_color & 0xFF
    g = (bg_color >> 8) & 0xFF
    b = (bg_color >> 16) & 0xFF
    # 計算亮度 (0-255)
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    # 亮度 > 180 用深色字，否則用白色字
    return COLOR_TEXT if brightness > 180 else COLOR_WHITE


# =============================================================================
# 標準顏色（Material Design）- BGR 格式
# =============================================================================

COLOR_RED = hex_to_bgr("#F44336")       # 紅色 - 問題/錯誤/改善前
COLOR_GREEN = hex_to_bgr("#4CAF50")     # 綠色 - 成功/改善後
COLOR_BLUE = hex_to_bgr("#2196F3")      # 藍色 - 流程/節點
COLOR_ORANGE = hex_to_bgr("#FF9800")    # 橘色 - 警告/風險
COLOR_PURPLE = hex_to_bgr("#9C27B0")    # 紫色 - 特殊/強調
COLOR_TEAL = hex_to_bgr("#009688")      # 青色 - 輔助色
COLOR_PINK = hex_to_bgr("#E91E63")      # 粉紅 - 觸控/輸入

# 灰階色
COLOR_GRAY_BG = hex_to_bgr("#F5F5F5")   # 淺灰背景
COLOR_GRAY_LIGHT = hex_to_bgr("#E0E0E0")  # 淺灰
COLOR_GRAY = hex_to_bgr("#9E9E9E")      # 中灰
COLOR_GRAY_DARK = hex_to_bgr("#616161")  # 深灰
COLOR_TEXT = hex_to_bgr("#333333")      # 文字色
COLOR_WHITE = hex_to_bgr("#FFFFFF")     # 白色
COLOR_BLACK = hex_to_bgr("#000000")     # 黑色

# =============================================================================
# MTK 風格配色
# =============================================================================

BG_COLOR = hex_to_bgr("#FFF9E6")        # 米色背景
ACCENT_BLUE = hex_to_bgr("#4682B4")     # 鋼青色 - 技術/成功
ACCENT_ORANGE = hex_to_bgr("#E67E22")   # 深橘色 - 問題/POC
ACCENT_GREEN = hex_to_bgr("#27AE60")    # 翠綠色 - 效益/解決
ACCENT_PURPLE = hex_to_bgr("#8E44AD")   # 深紫色 - 架構/技術
ACCENT_RED = hex_to_bgr("#C00000")      # 深紅色 - 行動/決策

# =============================================================================
# 圖表專用顏色（from test_shapes_full.py）
# =============================================================================

CHART_RED = hex_to_bgr("#F44336")       # 改善前/問題
CHART_GREEN = hex_to_bgr("#4CAF50")     # 改善後/成功
CHART_BLUE = hex_to_bgr("#33B5E5")      # 流程/節點
CHART_ORANGE = hex_to_bgr("#FF9800")    # 警告/風險
CHART_PURPLE = hex_to_bgr("#9C27B0")    # 硬體/底層
CHART_ACCENT = hex_to_bgr("#00796B")    # 強調色 Teal

# =============================================================================
# 字體設定
# =============================================================================

FONT_NAME = "Microsoft JhengHei"        # 微軟正黑體
FONT_NAME_EN = "Segoe UI"               # 英文字體
FONT_NAME_MONO = "Consolas"             # 等寬字體

# =============================================================================
# 調色板（用於圖表繪製）
# =============================================================================

PALETTE = {
    "danger": {"stroke": COLOR_RED, "fill": COLOR_GRAY_BG},
    "ok": {"stroke": COLOR_GREEN, "fill": COLOR_GRAY_BG},
    "info": {"stroke": COLOR_BLUE, "fill": COLOR_WHITE},
    "accent": {"stroke": COLOR_ORANGE, "fill": None},
    "pink": {"stroke": COLOR_PINK, "fill": COLOR_WHITE},
    "default": {"stroke": COLOR_GRAY_DARK, "fill": COLOR_WHITE},
}


# =============================================================================
# 測試
# =============================================================================

if __name__ == "__main__":
    print("pywin32 顏色模組測試")
    print(f"COLOR_RED (BGR): {hex(COLOR_RED)} -> {bgr_to_hex(COLOR_RED)}")
    print(f"COLOR_GREEN (BGR): {hex(COLOR_GREEN)} -> {bgr_to_hex(COLOR_GREEN)}")
    print(f"COLOR_BLUE (BGR): {hex(COLOR_BLUE)} -> {bgr_to_hex(COLOR_BLUE)}")
    print(f"BG_COLOR (BGR): {hex(BG_COLOR)} -> {bgr_to_hex(BG_COLOR)}")
