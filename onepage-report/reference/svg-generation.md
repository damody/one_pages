# SVG 生成規範

## 基本規格

```
- viewBox: "0 0 {width} {height}"（從尺寸欄位取得）
- 白色背景矩形
- 字型：font-family="Microsoft JhengHei, Arial, sans-serif"
- 圖要畫滿整個 viewBox，不要留太多空白
- **禁止使用 emoji**：cairosvg 無法渲染 emoji，必須用 SVG 圖形代替
```

---

## Emoji 替代方案（必須遵守）

| 原本 Emoji | 替代 SVG 圖形 |
|------------|---------------|
| ❌ | 紅色圓圈 + 白色叉叉線條 |
| ✓ ✅ | 綠色圓圈 + 白色勾勾線條 |
| ⚠️ | 黃色三角形 + 黑色驚嘆號 |
| 📊 | 藍色矩形 + 白色長條圖線條 |
| 🔄 | 藍色圓形箭頭 |
| ➡️ | polygon 箭頭圖形 |

### SVG 圖形範例

```xml
<!-- 紅色叉叉（代替 ❌）-->
<g>
  <circle cx="10" cy="10" r="10" fill="#F44336"/>
  <line x1="5" y1="5" x2="15" y2="15" stroke="white" stroke-width="2"/>
  <line x1="15" y1="5" x2="5" y2="15" stroke="white" stroke-width="2"/>
</g>

<!-- 綠色勾勾（代替 ✓）-->
<g>
  <circle cx="10" cy="10" r="10" fill="#4CAF50"/>
  <polyline points="5,10 8,14 15,6" stroke="white" stroke-width="2" fill="none"/>
</g>

<!-- 黃色警告（代替 ⚠️）-->
<g>
  <polygon points="10,2 19,18 1,18" fill="#FFC107" stroke="#FF9800" stroke-width="1"/>
  <text x="10" y="15" text-anchor="middle" font-size="12" font-weight="bold" fill="#333">!</text>
</g>
```

---

## 文字大小

| 用途 | 字體大小 |
|------|----------|
| 圖表標題 | font-size="24" |
| 區塊標題 | font-size="18" |
| 節點主文字 | font-size="14" |
| 節點說明文字 | font-size="12" |
| 標籤/註解 | font-size="11" |
| 數據/數值 | font-size="13" + 粗體 |

---

## 配色

| 用途 | 顏色 | Hex |
|------|------|-----|
| 正面/改善後 | 綠 | #4CAF50 |
| 負面/改善前 | 紅 | #F44336 |
| 中性/流程 | 藍 | #2196F3 |
| 重點標示 | 橙 | #FF9800 |
| 區塊背景 | 淺灰 | #F5F5F5 |
| 邊框 | 深灰 | #BDBDBD |
| 文字 | 深灰 | #333333 |
| 次要文字 | 灰 | #757575 |

---

## 圖表結構

| 類型 | 結構說明 |
|------|----------|
| before_after | 左右兩個圓角矩形，中間虛線箭頭，每個矩形內部要有詳細流程 |
| platform_compare | 上下兩個區塊，每個區塊內要有完整流程，用虛線標註差異 |
| flow | 橫向連接的節點，每個節點要有說明文字，箭頭上要標註條件或數據 |
| timeline | 時間軸線，每個事件要有時間標註和說明 |
| experiment_flow | 對照組 vs 實驗組的完整比較圖 |
| architecture | 分層或模組架構圖，標示本次改動位置 |

---

## 詳細程度檢查

生成前確認：
1. 每個節點都有具體內容（不只是名稱）
2. 數據和時間都有標註
3. 差異點都有標示
4. 圖例或說明完整

---

## Task Subagent 調用範例

```
Task(
  description="生成主圖 SVG",
  subagent_type="general-purpose",
  prompt="""
你是 SVG 圖表生成專家。請根據以下指示生成 SVG 圖表。

## 規格
- 尺寸：{width} x {height} 像素
- viewBox: "0 0 {width} {height}"
- 背景：白色 (#FFFFFF)
- 字型：font-family="Microsoft JhengHei, Arial, sans-serif"
- 配色：
  - 正面/改善後: #4CAF50 (綠)
  - 負面/改善前: #F44336 (紅)
  - 中性: #2196F3 (藍)
  - 區塊背景: #F5F5F5 (淺灰)
  - 邊框: #BDBDBD (深灰)
  - 文字: #333333

## 文字大小
- 區塊標題：font-size="18"
- 內容文字：font-size="14"
- 標籤/註解：font-size="12"

## 圖表內容
{從 diagrams.md 讀取的「SVG 生成指示」內容}

## 輸出
使用 Write 工具將完整 SVG 代碼寫入：./output/{filename}.svg
不要用 markdown 包裝，直接輸出純 SVG 代碼。
"""
)
```

---

## 透明背景處理

如果需要透明背景（讓 PNG 透明），在生成 SVG 時不要加背景矩形：

```xml
<!-- 不要這行 -->
<rect width="100%" height="100%" fill="#FFFFFF"/>

<!-- 直接開始畫內容 -->
<g transform="...">
  ...
</g>
```
