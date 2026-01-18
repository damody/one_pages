# -*- coding: utf-8 -*-
"""
原生折線圖繪製（pywin32 版本）

使用 pywin32 COM API 建立 PowerPoint 原生 Chart 物件，
支援完整的圖表編輯功能。

Chart Type 常用值：
- 4: xlLine 折線圖
- 65: xlLineMarkers 帶標記的折線圖
- 51: xlColumnClustered 群組長條圖
- 5: xlPie 圓餅圖
- -4169: xlXYScatter 散佈圖
"""

from ._colors_pywin32 import (
    COLOR_BLUE, COLOR_GREEN, COLOR_RED, COLOR_ORANGE, COLOR_PURPLE,
    COLOR_WHITE, COLOR_TEXT, FONT_NAME
)


# =============================================================================
# 圖表類型常數
# =============================================================================

XL_LINE = 4
XL_LINE_MARKERS = 65
XL_COLUMN_CLUSTERED = 51
XL_COLUMN_STACKED = 52
XL_BAR_CLUSTERED = 57
XL_PIE = 5
XL_DOUGHNUT = -4120
XL_AREA = 1
XL_XY_SCATTER = -4169


# =============================================================================
# 折線圖
# =============================================================================

def draw_line_chart(slide, left, top, width, height,
                    series_data, title=None, show_legend=True,
                    show_markers=True, show_data_labels=False):
    """
    使用 pywin32 建立原生折線圖

    Args:
        slide: pywin32 Slide 物件
        left, top: 左上角位置（pt）
        width, height: 寬高（pt）
        series_data: 資料字典：
            {
                "categories": ["Q1", "Q2", "Q3", "Q4"],
                "series": [
                    {"name": "2024", "values": [100, 120, 140, 160]},
                    {"name": "2025", "values": [110, 130, 155, 180]}
                ]
            }
        title: 圖表標題（可選）
        show_legend: 是否顯示圖例
        show_markers: 是否顯示資料點標記
        show_data_labels: 是否顯示資料標籤

    Returns:
        Shape 物件（圖表）
    """
    # 選擇圖表類型
    chart_type = XL_LINE_MARKERS if show_markers else XL_LINE

    # 建立圖表
    chart_shape = slide.Shapes.AddChart2(
        Style=-1,  # 使用預設樣式
        Type=chart_type,
        Left=left, Top=top, Width=width, Height=height
    )
    chart = chart_shape.Chart

    # 取得資料
    categories = series_data.get("categories", [])
    series_list = series_data.get("series", [])

    if not categories or not series_list:
        return chart_shape

    try:
        # 方法 1：使用 ChartData.Activate 啟用編輯模式
        chart.ChartData.Activate()
        workbook = chart.ChartData.Workbook
        worksheet = workbook.Worksheets(1)

        # 清除預設資料（保留第一列第一欄空白）
        used_range = worksheet.UsedRange
        if used_range:
            used_range.Clear()

        # 寫入類別（第一欄，從第二列開始）
        for i, cat in enumerate(categories):
            worksheet.Cells(i + 2, 1).Value = cat

        # 寫入數列（從第二欄開始）
        for col_idx, series in enumerate(series_list):
            # 數列名稱（第一列）
            worksheet.Cells(1, col_idx + 2).Value = series.get("name", f"Series {col_idx + 1}")

            # 數列數值
            values = series.get("values", [])
            for row_idx, val in enumerate(values):
                worksheet.Cells(row_idx + 2, col_idx + 2).Value = val

        # 設定資料範圍（使用 A1 表示法）
        num_rows = len(categories) + 1
        num_cols = len(series_list) + 1

        # 計算欄位字母（A, B, C, ...）
        def col_letter(n):
            result = ""
            while n > 0:
                n, remainder = divmod(n - 1, 26)
                result = chr(65 + remainder) + result
            return result

        end_col = col_letter(num_cols)
        range_str = f"A1:{end_col}{num_rows}"

        # 使用 SetSourceData 設定資料範圍
        data_range = worksheet.Range(range_str)
        chart.SetSourceData(data_range)

        workbook.Close(False)

    except Exception as e:
        # 方法 2：如果上述方法失敗，嘗試使用 SeriesCollection 直接設定
        try:
            # 清除現有的數列
            while chart.SeriesCollection().Count > 0:
                chart.SeriesCollection(1).Delete()

            # 添加新數列
            for series_info in series_list:
                series = chart.SeriesCollection().NewSeries()
                series.Name = series_info.get("name", "")
                series.Values = series_info.get("values", [])
                series.XValues = categories

        except Exception as inner_e:
            # 如果兩種方法都失敗，返回帶有預設資料的圖表
            print(f"警告：圖表資料設定失敗: {inner_e}")

    # 設定標題
    if title:
        chart.HasTitle = True
        chart.ChartTitle.Text = title
        try:
            chart.ChartTitle.Format.TextFrame2.TextRange.Font.Size = 12
            chart.ChartTitle.Format.TextFrame2.TextRange.Font.Name = FONT_NAME
        except:
            pass
    else:
        chart.HasTitle = False

    # 設定圖例
    if show_legend:
        chart.HasLegend = True
        chart.Legend.Position = -4107  # xlLegendPositionBottom
    else:
        chart.HasLegend = False

    # 設定資料標籤
    if show_data_labels:
        for series in chart.SeriesCollection():
            series.HasDataLabels = True

    # 樣式調整
    try:
        chart.PlotArea.Format.Fill.Visible = False
        chart.ChartArea.Format.Line.Visible = False
    except:
        pass

    return chart_shape


# =============================================================================
# 長條圖
# =============================================================================

def _set_chart_data(chart, categories, series_list):
    """
    內部輔助函數：設定圖表資料

    Args:
        chart: Chart 物件
        categories: 類別列表
        series_list: 數列列表

    Returns:
        bool: 是否成功設定
    """
    if not categories or not series_list:
        return False

    try:
        # 方法 1：使用 ChartData.Activate 啟用編輯模式
        chart.ChartData.Activate()
        workbook = chart.ChartData.Workbook
        worksheet = workbook.Worksheets(1)

        # 清除預設資料
        used_range = worksheet.UsedRange
        if used_range:
            used_range.Clear()

        # 寫入類別（第一欄，從第二列開始）
        for i, cat in enumerate(categories):
            worksheet.Cells(i + 2, 1).Value = cat

        # 寫入數列（從第二欄開始）
        for col_idx, series in enumerate(series_list):
            worksheet.Cells(1, col_idx + 2).Value = series.get("name", f"Series {col_idx + 1}")
            values = series.get("values", [])
            for row_idx, val in enumerate(values):
                worksheet.Cells(row_idx + 2, col_idx + 2).Value = val

        # 設定資料範圍（使用 A1 表示法）
        num_rows = len(categories) + 1
        num_cols = len(series_list) + 1

        def col_letter(n):
            result = ""
            while n > 0:
                n, remainder = divmod(n - 1, 26)
                result = chr(65 + remainder) + result
            return result

        end_col = col_letter(num_cols)
        range_str = f"A1:{end_col}{num_rows}"
        data_range = worksheet.Range(range_str)
        chart.SetSourceData(data_range)

        workbook.Close(False)
        return True

    except Exception as e:
        # 方法 2：使用 SeriesCollection
        try:
            while chart.SeriesCollection().Count > 0:
                chart.SeriesCollection(1).Delete()

            for series_info in series_list:
                series = chart.SeriesCollection().NewSeries()
                series.Name = series_info.get("name", "")
                series.Values = series_info.get("values", [])
                series.XValues = categories
            return True

        except Exception as inner_e:
            print(f"警告：圖表資料設定失敗: {inner_e}")
            return False


def draw_bar_chart(slide, left, top, width, height,
                   series_data, title=None, show_legend=True,
                   horizontal=False, stacked=False):
    """
    使用 pywin32 建立長條圖

    Args:
        slide: pywin32 Slide 物件
        left, top: 左上角位置（pt）
        width, height: 寬高（pt）
        series_data: 資料字典（同 draw_line_chart）
        title: 圖表標題
        show_legend: 是否顯示圖例
        horizontal: 是否為水平長條圖
        stacked: 是否為堆疊長條圖

    Returns:
        Shape 物件（圖表）
    """
    # 選擇圖表類型
    if horizontal:
        chart_type = XL_BAR_CLUSTERED
    elif stacked:
        chart_type = XL_COLUMN_STACKED
    else:
        chart_type = XL_COLUMN_CLUSTERED

    # 建立圖表
    chart_shape = slide.Shapes.AddChart2(
        Style=-1,
        Type=chart_type,
        Left=left, Top=top, Width=width, Height=height
    )
    chart = chart_shape.Chart

    # 取得資料
    categories = series_data.get("categories", [])
    series_list = series_data.get("series", [])

    # 設定資料
    _set_chart_data(chart, categories, series_list)

    # 設定
    if title:
        chart.HasTitle = True
        chart.ChartTitle.Text = title
    else:
        chart.HasTitle = False

    chart.HasLegend = show_legend

    return chart_shape


# =============================================================================
# 圓餅圖
# =============================================================================

def draw_pie_chart(slide, left, top, width, height,
                   data, title=None, show_legend=True,
                   show_percentage=True):
    """
    使用 pywin32 建立圓餅圖

    Args:
        slide: pywin32 Slide 物件
        left, top: 左上角位置（pt）
        width, height: 寬高（pt）
        data: 資料字典：
            {
                "labels": ["A", "B", "C"],
                "values": [30, 50, 20]
            }
        title: 圖表標題
        show_legend: 是否顯示圖例
        show_percentage: 是否顯示百分比

    Returns:
        Shape 物件（圖表）
    """
    chart_shape = slide.Shapes.AddChart2(
        Style=-1,
        Type=XL_PIE,
        Left=left, Top=top, Width=width, Height=height
    )
    chart = chart_shape.Chart

    # 取得資料
    labels = data.get("labels", [])
    values = data.get("values", [])

    if labels and values:
        # 轉換為 series_data 格式
        series_list = [{"name": "數據", "values": values}]
        _set_chart_data(chart, labels, series_list)

    # 設定
    if title:
        chart.HasTitle = True
        chart.ChartTitle.Text = title
    else:
        chart.HasTitle = False

    chart.HasLegend = show_legend

    # 顯示百分比
    if show_percentage:
        try:
            for point in chart.SeriesCollection(1).Points():
                point.HasDataLabel = True
                point.DataLabel.ShowPercentage = True
                point.DataLabel.ShowValue = False
        except:
            pass

    return chart_shape


# =============================================================================
# 面積圖
# =============================================================================

def draw_area_chart(slide, left, top, width, height,
                    series_data, title=None, show_legend=True):
    """
    使用 pywin32 建立面積圖

    Args:
        slide: pywin32 Slide 物件
        left, top: 左上角位置（pt）
        width, height: 寬高（pt）
        series_data: 資料字典（同 draw_line_chart）
        title: 圖表標題
        show_legend: 是否顯示圖例

    Returns:
        Shape 物件（圖表）
    """
    chart_shape = slide.Shapes.AddChart2(
        Style=-1,
        Type=XL_AREA,
        Left=left, Top=top, Width=width, Height=height
    )
    chart = chart_shape.Chart

    # 取得資料
    categories = series_data.get("categories", [])
    series_list = series_data.get("series", [])

    # 設定資料
    _set_chart_data(chart, categories, series_list)

    # 設定
    if title:
        chart.HasTitle = True
        chart.ChartTitle.Text = title
    else:
        chart.HasTitle = False

    chart.HasLegend = show_legend

    return chart_shape


# =============================================================================
# 便捷函數
# =============================================================================

def draw_simple_line_chart(slide, left, top, width, height,
                           categories, values, title=None):
    """
    建立簡單的單數列折線圖

    Args:
        slide: pywin32 Slide 物件
        left, top: 左上角位置（pt）
        width, height: 寬高（pt）
        categories: 類別列表
        values: 數值列表
        title: 圖表標題

    Returns:
        Shape 物件
    """
    series_data = {
        "categories": categories,
        "series": [{"name": "數據", "values": values}]
    }
    return draw_line_chart(slide, left, top, width, height,
                          series_data, title, show_legend=False)


def draw_comparison_line_chart(slide, left, top, width, height,
                               categories, before_values, after_values,
                               before_label="改善前", after_label="改善後",
                               title=None):
    """
    建立對比折線圖（改善前 vs 改善後）

    Args:
        slide: pywin32 Slide 物件
        left, top: 左上角位置（pt）
        width, height: 寬高（pt）
        categories: 類別列表
        before_values: 改善前數值
        after_values: 改善後數值
        before_label: 改善前標籤
        after_label: 改善後標籤
        title: 圖表標題

    Returns:
        Shape 物件
    """
    series_data = {
        "categories": categories,
        "series": [
            {"name": before_label, "values": before_values},
            {"name": after_label, "values": after_values}
        ]
    }
    return draw_line_chart(slide, left, top, width, height,
                          series_data, title, show_legend=True)
