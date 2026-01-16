"""
PPTX 顏色常數與字體定義
用於所有圖表繪製函數的共用常數
"""
from pptx.dml.color import RGBColor

# === 標準顏色（Material Design）===
COLOR_RED = RGBColor(244, 67, 54)       # #F44336 - 改善前/問題/負面
COLOR_GREEN = RGBColor(76, 175, 80)     # #4CAF50 - 改善後/成功/正面
COLOR_BLUE = RGBColor(33, 150, 243)     # #2196F3 - 流程/節點/中性
COLOR_ORANGE = RGBColor(255, 152, 0)    # #FF9800 - 警告/注意
COLOR_PURPLE = RGBColor(156, 39, 176)   # #9C27B0 - 特殊/強調
COLOR_GRAY_BG = RGBColor(245, 245, 245) # #F5F5F5 - 區塊背景
COLOR_GRAY_DARK = RGBColor(97, 97, 97)  # #616161 - 深灰/副標題
COLOR_TEXT = RGBColor(51, 51, 51)       # #333333 - 主要文字
COLOR_WHITE = RGBColor(255, 255, 255)   # #FFFFFF - 白色文字
COLOR_ACCENT = RGBColor(0, 121, 107)    # #00796B - 強調色 Teal

# === MTK 風格配色 ===
BG_COLOR = RGBColor(255, 249, 230)      # 米色背景
ACCENT_BLUE = RGBColor(70, 130, 180)    # Steel Blue
ACCENT_ORANGE = RGBColor(230, 126, 34)  # 橙色
ACCENT_GREEN = RGBColor(39, 174, 96)    # 綠色
ACCENT_PURPLE = RGBColor(142, 68, 173)  # 紫色
ACCENT_RED = RGBColor(192, 0, 0)        # 深紅色

# === 字體設定 ===
FONT_NAME = "Microsoft JhengHei"  # 微軟正黑體

# === 佈局配置 ===
FLOW_LAYOUT_CONFIG = {
    "max_horizontal_nodes": 6,    # 超過此數量強制縱向
    "min_node_width": 0.8,        # 最小節點寬度（吋）
    "min_gap": 0.08,              # 最小節點間距
    "default_gap": 0.12,          # 預設間距
    "char_width_avg": 0.09,       # 中文字元寬度估算
    "padding_horizontal": 0.2,    # 節點內留白
}
