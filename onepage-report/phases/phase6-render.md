# Phase 6：渲染輸出

## 6.1 建立輸出目錄

```bash
mkdir -p ./output
```

---

## 6.2 儲存 diagrams.md 並產生圖表

根據 `DIAGRAM_METHOD` 設定決定圖表產生方式：

| DIAGRAM_METHOD | 處理流程 | 參考檔案 |
|----------------|----------|----------|
| `svg_png` | 使用 Task subagent 生成 SVG → cairosvg 轉 PNG → 嵌入 PPTX | `Read {skill_dir}/reference/svg-generation.md` |
| `pptx_shapes` | 在 render_this.py 中直接使用 python-pptx shapes API 繪製 | `Read {skill_dir}/reference/pptx-shapes.md` |

1. 將 diagrams.md 內容儲存到 `./output/diagrams.md`

---

### 6.2.A 方式一：SVG/PNG（當 DIAGRAM_METHOD = svg_png）

**執行前請讀取：** `{skill_dir}/reference/svg-generation.md`

使用 **Task 工具調用 subagent** 生成 SVG 圖表。

對於 diagrams.md 中的**每個圖表區塊**，使用 Task 工具調用 subagent 生成 SVG：

```
Task(
  description="生成{區塊名稱} SVG",
  subagent_type="general-purpose",
  prompt="""
你是 SVG 圖表生成專家。請根據以下指示生成 SVG 圖表。

{從 reference/svg-generation.md 讀取的規格}

## 圖表內容
{從 diagrams.md 讀取的「SVG 生成指示」內容}

## 輸出
使用 Write 工具將完整 SVG 代碼寫入：./output/{output_filename}.svg
不要用 markdown 包裝，直接輸出純 SVG 代碼。
"""
)
```

**輸出檔案命名：**

| 區塊名稱 | 輸出檔案 |
|----------|----------|
| 主圖 | `./output/main_diagram.svg` |
| 附錄圖 1 | `./output/appendix_diagram_1.svg` |
| 附錄圖 2 | `./output/appendix_diagram_2.svg` |

**執行順序：** 可以**並行**執行多個 Task 來加速生成

---

### 6.2.5 SVG 轉 PNG（透明背景）

在嵌入 PPTX 之前，將所有 SVG 轉換為透明背景的 PNG：

```python
import os
import cairosvg

def convert_svg_to_png(svg_path, png_path=None, scale=2):
    if png_path is None:
        png_path = svg_path.rsplit('.', 1)[0] + '.png'
    cairosvg.svg2png(
        url=svg_path,
        write_to=png_path,
        scale=scale,
        background_color=None  # 保持透明背景
    )
    return png_path

# 轉換所有 SVG 檔案
svg_files = [f for f in os.listdir('.') if f.endswith('.svg')]
for svg_file in svg_files:
    convert_svg_to_png(svg_file)
```

---

### 6.2.B 方式二：PPTX Shapes（當 DIAGRAM_METHOD = pptx_shapes）

**執行前請讀取：** `{skill_dir}/reference/pptx-shapes.md`

使用 python-pptx 內建的 shapes API 直接在投影片上繪製圖表。

優點：
- 產生的圖表可直接在 PowerPoint 中編輯
- 不需要 cairosvg 依賴
- 避免 emoji 無法渲染的問題

---

## 6.3 產生 PPTX

這是最關鍵的步驟。

### 執行前準備

1. 讀取 `{skill_dir}/scripts/pptx_reference.py` 了解 python-pptx API 用法

2. 根據 one_page.md 的內容，動態產生 Python 程式碼

### ⚠️ 內容完整性要求（絕對禁止刪減）

- **one_page.md 的每一段文字都必須出現在投影片中**
- **glossary.md 的每一個術語解釋都必須放入附錄**
- 不能因為版面不夠就省略內容
- 如果內容太多，應該調小字體（最小 8pt）或分多頁，而不是刪減
- 表格的每一行每一列都必須完整呈現

### 佈局決策原則

- 圖表與相關說明要放在一起
- 根據內容量決定佈局（不要固定）
- 證據多 → 可能需要左右分欄
- 圖表複雜 → 給圖更多空間
- 字體大小根據內容量調整（但不小於 8pt）
- **有表格時**：表格放在投影片下方或右側

### 產生程式碼

將產生的程式碼儲存到 `./output/render_this.py`

---

## 6.3.1 Sub Agent 驗證步驟（必須執行）

在執行 render_this.py 之前，必須呼叫 Task tool 讓獨立的 sub agent 檢查程式碼是否完整包含所有內容。

```
Task(
  subagent_type="general-purpose",
  prompt="""
你是程式碼審查員，請驗證以下 Python 程式碼是否完整包含 markdown 的所有內容。

## 審查任務
逐一比對 markdown 和 Python 程式碼，確保沒有遺漏任何內容。

## 輸入 1：one_page.md 內容
{貼上完整 one_page.md}

## 輸入 2：glossary.md 內容
{貼上完整 glossary.md}

## 輸入 3：render_this.py 內容
{貼上完整 render_this.py}

## 審查清單（每項都要檢查）
1. one_page.md 的標題是否出現在 Python 中？
2. one_page.md 的每一個段落是否都有對應的文字？
3. one_page.md 的每一個重點是否都有出現？
4. one_page.md 的表格是否完整（每行每列）？
5. glossary.md 的每一個術語是否都在附錄中？
6. 數字是否正確（沒有抄錯或遺漏）？

## 輸出格式
- ✅ 內容完整：所有內容都已包含
- ❌ 有遺漏：列出遺漏的內容
"""
)
```

**如果 Sub Agent 發現遺漏：**
1. 根據指出的遺漏修改 render_this.py
2. 再次呼叫 Sub Agent 驗證
3. 重複直到 ✅ 內容完整

---

## 6.3.2 執行產生 PPTX

驗證通過後，執行 Python：

```bash
cd ./output && python render_this.py
```

---

## 6.3.3 產生附錄投影片

### 投影片結構

```
投影片 1：主報告（one_page.md 內容 + 主圖）
投影片 2：附錄 - 流程圖詳解（如有附錄圖）
投影片 3：附錄 - 術語解釋（glossary.md 內容）
```

### 附錄圖表佈局

| 附錄圖數量 | 佈局 | 每頁圖數 |
|-----------|------|---------|
| 1-2 張 | 上下排列 | 1-2 |
| 3-4 張 | 2x2 網格 | 4 |
| 5+ 張 | 分多頁，每頁 2x2 | 4 |

### 術語超連結

- 主投影片中的 `[[術語]]` 標記會轉換為藍色底線文字
- 點擊可跳轉到附錄投影片（術語解釋頁）
- 附錄投影片顯示所有術語的白話解釋

---

## 6.3.5 排版審查（Layout Review）

**觸發條件**：`LAYOUT_REVIEW_ROUNDS > 0`

在生成 PPTX 後，執行排版審查以確保所有元素不會重疊。

### 審查流程

```
FOR round = 1 TO LAYOUT_REVIEW_ROUNDS:
    1. 收集投影片上所有元素的邊界框 (bounding box)
    2. 對每對元素計算是否重疊
    3. 若有重疊：
       a. 記錄重疊元素對
       b. 決定修正策略
       c. 執行修正（調整位置、縮減內容或字體）
    4. 若無重疊：提前結束審查，輸出「排版審查通過」
```

### 修正策略優先順序

| 優先順序 | 策略 | 說明 |
|----------|------|------|
| 1 | 調整位置 | 將下方元素往下移 |
| 2 | 縮減間距 | 減少元素內部的 padding 和 line spacing |
| 3 | 縮減內容 | 減少列表項目數量或縮短文字 |
| 4 | 縮小字體 | 降低字體大小（最小 7pt） |

---

## 6.4 輸出演講稿

將最終版 script.md 儲存到 `./output/speaker_script.md`

**注意**：演講稿會同時存在兩處：
1. PPTX 投影片的備註欄（方便簡報時直接看）
2. `./output/speaker_script.md` 獨立檔案（方便編輯或列印）

---

## 6.5 輸出其他檔案

- `./output/citation_map.md`：來源對照表（含 web search 補充說明）
- `./output/glossary.md`：術語詞彙表

---

## 6.6 完成

告知使用者：

```
報告產生完成！

輸出檔案：
📊 ./output/one_page.pptx（投影片，含主報告 + 附錄術語解釋）
📝 ./output/speaker_script.md（演講稿獨立檔案）
🖼️ ./output/*.svg（原始圖表）
🖼️ ./output/*.png（透明背景圖表，嵌入 PPTX 用）
📚 ./output/citation_map.md（來源對照表，含 web search 補充說明）
📖 ./output/glossary.md（術語詞彙表）

投影片結構：
- 第 1 頁：主報告（含術語上標標記）
- 第 2 頁：附錄 - 術語解釋（適合非技術背景讀者）

建議：
1. 開啟 PPTX 確認排版
2. 簡報時可開啟「簡報者檢視畫面」查看備註欄的演講稿
3. 如需調整，可以直接編輯 PPTX
4. 如被問「這數字哪來的？」，可查閱 citation_map.md
5. 如聽眾對術語有疑問，可切到附錄頁說明
```
