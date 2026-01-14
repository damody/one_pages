# Phase 2：讀取素材

根據 `{input_path}` 判斷輸入類型並處理。

## 2.1 判斷輸入類型

| 輸入格式 | 判斷條件 | 處理方式 |
|----------|----------|----------|
| 資料夾 | 路徑是目錄 | 掃描 .txt/.md/.pptx/.pdf 檔案 |
| PPTX 檔案 | 以 .pptx 結尾 | 使用 extract_pptx.py 抽取 |
| PDF 檔案 | 以 .pdf 結尾 | 使用 extract_pdf.py 抽取 |
| URL | 以 http:// 或 https:// 開頭 | 使用 WebFetch 抓取 |

---

## 2.2 資料夾處理

1. 使用 Glob 工具掃描資料夾內的檔案：
   ```
   Glob: {input_path}/**/*.txt
   Glob: {input_path}/**/*.md
   Glob: {input_path}/**/*.pptx
   Glob: {input_path}/**/*.pdf
   ```

2. 對於 .txt/.md 檔案：使用 Read 工具讀取內容

3. 對於 .pptx 檔案：
   - 先詢問使用者要抽取哪些投影片
   - 執行 extract_pptx.py 抽取內容：
   ```bash
   python {skill_dir}/scripts/extract_pptx.py {pptx_file} ./temp_extract/ --slides "{slide_range}"
   ```
   - 讀取 ./temp_extract/text.md 作為素材

4. 對於 .pdf 檔案：
   - 先詢問使用者要抽取哪些頁面，是否需要 OCR
   - 執行 extract_pdf.py 抽取內容：
   ```bash
   python {skill_dir}/scripts/extract_pdf.py {pdf_file} ./temp_extract/ --pages "{page_range}" [--ocr]
   ```
   - 讀取 ./temp_extract/text.md 作為素材

---

## 2.3 單一 PPTX 檔案處理

1. 先列出投影片清單讓使用者選擇：
   ```bash
   python {skill_dir}/scripts/extract_pptx.py {input_path} --list
   ```

2. 使用 AskUserQuestion 詢問：
   ```
   以下是 PPTX 的投影片清單：
   {slide_list}

   請輸入要抽取的投影片範圍：
   - 範例："1-5" 或 "1,3,5,7" 或 "1-3,7,10-12"
   - 留空表示全部抽取
   ```

3. 執行抽取：
   ```bash
   python {skill_dir}/scripts/extract_pptx.py {input_path} ./temp_extract/ --slides "{slide_range}"
   ```

4. 讀取 ./temp_extract/text.md 作為素材

---

## 2.4 單一 PDF 檔案處理

1. 先列出頁面清單讓使用者選擇：
   ```bash
   python {skill_dir}/scripts/extract_pdf.py {input_path} --list
   ```

2. 使用 AskUserQuestion 詢問：
   ```
   以下是 PDF 的頁面清單：
   {page_list}

   請輸入要抽取的頁碼範圍：
   - 範例："1-5" 或 "1,3,5,7" 或 "1-3,7,10-12"
   - 留空表示全部抽取

   是否啟用 OCR？（適用於掃描文件）
   1. 否（預設）
   2. 是
   ```

3. 執行抽取：
   ```bash
   python {skill_dir}/scripts/extract_pdf.py {input_path} ./temp_extract/ --pages "{page_range}" [--ocr]
   ```

4. 讀取 ./temp_extract/text.md 作為素材

---

## 2.5 URL 處理

1. 使用 WebFetch 工具抓取網頁內容：
   ```
   WebFetch: {input_path}
   prompt: 請抽取這個網頁的主要內容，包括標題、重點、數據等。忽略導覽列、廣告、頁尾等。
   ```

2. 將抓取的內容整理成素材格式

---

## 2.6 整理素材

將所有來源的內容整理成統一格式：

```
=== 素材彙整 ===

--- 來源：{source1}（{type1}）---
{content1}

--- 來源：{source2}（{type2}）---
{content2}
```

其中 type 可以是：txt、md、pptx:slide=1-5、url

---

## 2.7 建立 Citation Map

為每個素材段落建立 citation ID，方便追溯來源：

```markdown
## Citation Map

### C1
- **來源**：notes.md
- **位置**：第 1-5 行
- **原文**：Framepacing V2 透過SF queue來用部份延遲換部份功耗...

### C2
- **來源**：notes.md
- **位置**：第 6-10 行
- **原文**：傳統方法透過拉高 CPU 頻率來維持 99% 不掉幀率...

### C3
- **來源**：presentation.pptx:slide=3
- **位置**：shape 2
- **原文**：BufferTX 緩衝池可維持 0-3 個緩衝幀...
```

**建立規則：**
- 每個有實質內容的段落都給一個 citation ID（C1, C2, C3...）
- 記錄來源檔案、位置、原文摘要
- 後續 Phase 3 產出內容時引用這些 ID

---

## 2.8 Citation Map 擴充（Web Search + AI 整理）

對每個 Citation 執行 web search，用 AI 整理成詳細說明，讓後續步驟能直接使用這些補充資訊。

### 處理流程

```
對每個 Citation (C1, C2, C3...)：

  步驟 1：提取關鍵資訊
    - 識別原文中的技術術語（英文專有名詞、縮寫）
    - 識別原文的核心主題/概念
    - 例：原文「Framepacing V2 透過SF queue來換功耗」
      → 術語：Framepacing、SF queue
      → 主題：遊戲幀率控制、功耗優化

  步驟 2：執行 Web Search（兩階段）

    階段 A - 術語搜尋：
      對識別出的每個術語執行 WebSearch
      搜尋範例：
        - 「Framepacing 技術 解釋」
        - 「SurfaceFlinger queue Android」
      目的：獲取術語的準確定義和技術背景

    階段 B - 主題搜尋：
      對原文的核心主題執行更廣泛的搜尋
      搜尋範例：
        - 「遊戲幀率控制 功耗優化 技術方案」
        - 「mobile game frame pacing power consumption」
      目的：獲取相關背景知識和業界做法

  步驟 3：WebFetch 取得詳細內容
    - 對搜尋結果中最相關的 2-3 個網頁執行 WebFetch
    - 抓取詳細內容供後續整理

  步驟 4：AI 整理結果
    整合搜尋結果，產生「補充說明」：
    - 術語解釋：用白話文解釋原文中的專有名詞（國中生能懂）
    - 背景知識：補充原文沒提到但重要的背景資訊
    - 參考來源：標註資訊來源 URL
    字數限制：每個 citation 的補充說明 <= 300 字

  步驟 5：更新 Citation Map
    將補充說明加入對應的 citation 條目
```

### 更新後的 Citation Map 格式

```markdown
## Citation Map

### C1
- **來源**：notes.md
- **位置**：第 1-5 行
- **原文**：Framepacing V2 透過SF queue來用部份延遲換部份功耗...
- **補充說明**：
  - **術語解釋**：Framepacing（幀調度）是一種控制 GPU 渲染幀率的技術，
    透過調節幀生成時機來達到穩定幀率和降低功耗。SF queue 指 SurfaceFlinger
    的緩衝佇列，Android 系統用它來管理螢幕顯示的圖形緩衝區。
  - **背景知識**：此技術源自 PC 遊戲領域，主要解決幀率不穩定導致的畫面撕裂
    和功耗過高問題。常見實作包括 NVIDIA 的 Frame Queue 和 AMD 的 Anti-Lag。
  - **參考來源**：[https://example1.com], [https://example2.com]
```

### 限制與優化

1. **搜尋數量控制**
   - 每個 citation 最多執行 2 次 WebSearch（術語 + 主題各 1 次）
   - 每次搜尋最多取前 3 個結果做 WebFetch
   - 若 citation 總數超過 10 個，優先處理與結論最相關的段落

2. **整理品質要求**
   - 補充說明須符合「國中生能懂」標準
   - 避免重複已存在於原文的資訊
   - 對不確定的資訊標註「可能」「一般認為」
   - 若搜尋無結果或結果不可靠，標註「無可靠補充資訊」

3. **與後續步驟整合**
   - Phase 3.1：產生 one_page.md 時可引用補充說明的背景知識
   - Phase 3.4：glossary.md 可直接採用補充說明中的術語解釋
   - Phase 4：審稿時可檢查補充說明與原文是否矛盾

---

## 2.9 術語處理（國中生看不懂的詞）

讀取素材後，掃描是否有國中生看不懂的英文名詞或術語。

### 識別目標

- 英文專有名詞（如：Click-to-Photon、Frame Pacing、Anti-Lag）
- 英文縮寫（如：FPS、SoC、NUMA、CCX）
- 技術術語（如：latency、buffer、pipeline、migration）
- 任何可能讓國中生困惑的詞

### 處理流程

```
對於每個識別到的術語：

1. 先嘗試 WebSearch 查詢
   - 搜尋：「{術語} 是什麼 解釋」或「{術語} meaning explanation」
   - 如果找到清楚的解釋 → 記錄到術語清單，繼續使用

2. 如果 WebSearch 找不到或解釋不清楚
   - 使用 AskUserQuestion 詢問使用者：

   「素材中出現了 '{術語}'，這個詞國中生可能看不懂。
   請問：
   1. 這個詞的白話解釋是什麼？
   2. 或者，可以刪掉/改用其他說法嗎？」

3. 如果使用者也不知道或說可以刪掉
   - 從素材中移除該術語
   - 改用白話文描述（如果可以）
   - 或直接刪除該段落（如果無法改寫）
```

### 術語清單格式

```markdown
## 術語處理清單

| 術語 | 處理方式 | 白話解釋 | 來源 |
|------|----------|----------|------|
| Click-to-Photon | 保留+解釋 | 從按下按鈕到畫面顯示的總延遲時間 | WebSearch |
| Frame Pacing | 保留+解釋 | 控制遊戲畫面輸出節奏的技術 | 使用者提供 |
| NUMA | 刪除 | - | 使用者說可刪 |
| latency | 改寫 | 改用「延遲」 | 直接翻譯 |
```

### 重要原則

- 寧可多問，也不要留下看不懂的術語
- 如果術語對報告結論很重要，一定要找到解釋
- 如果術語不重要，可以直接刪掉或改用白話文
- 所有保留的術語都要加入 glossary.md
