# Phase 2：讀取素材（v2 - 平行 WebSearch 設計）

> **執行者：主 agent + 平行 subagents**
> **輸入：** `./output/phase1/config.md` + `{input_path}` 素材路徑
> **輸出：** `./output/phase2/`

---

## 2.0 架構概述（v2 改進）

```
Phase 2 v2 流程（預估 4-5 分鐘，vs 原本 9.5 分鐘）：
┌──────────────────────────────────────────────────────────────┐
│ 階段 1：主 agent 讀取素材（不使用 subagent）                    │
│ ┌────────────────────────────────────────────────────────┐   │
│ │ 主 Agent：讀取檔案 + 建立初步 Citation Map              │   │
│ │ 輸入：{input_path} 素材                                 │   │
│ │ 輸出：materials.md, 初步 citation_map.md, terms.md     │   │
│ │ ⏱️ ~2 分鐘                                              │   │
│ └────────────────────────────────────────────────────────┘   │
│                         ↓                                    │
│ 階段 2：平行 WebSearch 擴充 Citation（同時啟動，若啟用）        │
│ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐  │
│ │ Subagent A      │ │ Subagent B      │ │ Subagent C      │  │
│ │ Citations C1-C3 │ │ Citations C4-C6 │ │ Citations C7+   │  │
│ │ ⏱️ ~2 min       │ │ ⏱️ ~2 min       │ │ ⏱️ ~2 min       │  │
│ └─────────────────┘ └─────────────────┘ └─────────────────┘  │
│      ↑                   ↑                   ↑               │
│      └───────────────────┴───────────────────┘               │
│              都回傳 JSON 格式的補充說明                        │
│              ⏱️ 總計 ~2 分鐘（取最慢的）                       │
│                         ↓                                    │
│ 階段 3：主 agent 合併結果                                      │
│ ┌────────────────────────────────────────────────────────┐   │
│ │ 主 Agent：合併 WebSearch 結果到 citation_map.md         │   │
│ │ ⏱️ ~0.5 分鐘                                            │   │
│ └────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

**核心改變**：
- ✅ 階段 1 由主 agent 執行（減少 subagent 開銷）
- ✅ 階段 2 的 WebSearch 平行化（3 個 subagent 同時執行）
- ✅ 若 `CITATION_WEB_SEARCH = false`，跳過階段 2（節省更多時間）
- ✅ 總時間從 9.5 分鐘減少到 ~4-5 分鐘

---

## 2.0.1 入口檢查

**IF `RESUME_FROM` > 2：**
1. 從 `./output/phase2/` 讀取 checkpoint
2. 跳過本 Phase，直接進入 Phase 3

**ELSE：** 正常執行下方流程

---

## 階段 1：主 agent 讀取素材

### 2.1.1 判斷輸入類型

| 輸入格式 | 判斷條件 | 處理方式 |
|----------|----------|----------|
| 資料夾 | 路徑是目錄 | 掃描 .txt/.md/.pptx/.pdf 檔案 |
| PPTX 檔案 | 以 .pptx 結尾 | 使用 extract_pptx.py 抽取 |
| PDF 檔案 | 以 .pdf 結尾 | 使用 extract_pdf.py 抽取 |
| URL | 以 http:// 或 https:// 開頭 | 使用 WebFetch 抓取 |

### 2.1.2 資料夾處理

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

### 2.1.3 單一 PPTX 檔案處理

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

3. 執行抽取並讀取結果

### 2.1.4 單一 PDF 檔案處理

1. 先列出頁面清單讓使用者選擇：
   ```bash
   python {skill_dir}/scripts/extract_pdf.py {input_path} --list
   ```

2. 使用 AskUserQuestion 詢問頁碼範圍和 OCR 選項

3. 執行抽取並讀取結果

### 2.1.5 URL 處理

使用 WebFetch 工具抓取網頁內容：
```
WebFetch: {input_path}
prompt: 請抽取這個網頁的主要內容，包括標題、重點、數據等。忽略導覽列、廣告、頁尾等。
```

### 2.1.6 整理素材

將所有來源的內容整理成統一格式：

```markdown
# 素材彙整

--- 來源：{source1}（{type1}）---
{content1}

--- 來源：{source2}（{type2}）---
{content2}
```

### 2.1.7 建立初步 Citation Map

為每個素材段落建立 citation ID：

```markdown
# Citation Map

### C1
- **來源**：notes.md
- **位置**：第 1-5 行
- **原文**：Framepacing V2 透過SF queue來用部份延遲換部份功耗...

### C2
- **來源**：notes.md
- **位置**：第 6-10 行
- **原文**：傳統方法透過拉高 CPU 頻率來維持 99% 不掉幀率...
```

**建立規則：**
- 每個有實質內容的段落都給一個 citation ID（C1, C2, C3...）
- 記錄來源檔案、位置、原文摘要
- 後續 Phase 3 產出內容時引用這些 ID

### 2.1.8 術語識別

掃描素材中國中生看不懂的詞：

- 英文專有名詞（如：Click-to-Photon、Frame Pacing）
- 英文縮寫（如：FPS、SoC、NUMA）
- 技術術語（如：latency、buffer、pipeline）

**術語清單格式：**

```markdown
# 術語處理清單

| 術語 | 處理方式 | 白話解釋 | 來源 |
|------|----------|----------|------|
| Click-to-Photon | 保留+解釋 | 從按下按鈕到畫面顯示的總延遲時間 | WebSearch |
| Frame Pacing | 保留+解釋 | 控制遊戲畫面輸出節奏的技術 | 使用者提供 |
| latency | 改寫 | 改用「延遲」 | 直接翻譯 |
```

### 2.1.9 階段 1 完成後寫入初步檔案

```bash
python -c "from pathlib import Path; Path('output/phase2').mkdir(parents=True, exist_ok=True)"
```

```python
Write("./output/phase2/materials.md", materials_content)
Write("./output/phase2/citation_map.md", citation_map_content)  # 初步版本
Write("./output/phase2/terms.md", terms_content)
```

---

## 階段 2：平行 WebSearch 擴充 Citation

**觸發條件**：`CITATION_WEB_SEARCH = true`

若 `CITATION_WEB_SEARCH = false`，跳過此階段，直接進入 Checkpoint 驗證。

### 2.2.1 分組 Citations

將 citation_map.md 中的 citations 分成 3 組：

| 群組 | Citations | Subagent |
|------|-----------|----------|
| A | C1, C2, C3 | Subagent A |
| B | C4, C5, C6 | Subagent B |
| C | C7, C8, C9, C10... | Subagent C |

**注意**：若 citations 少於 3 個，只啟動需要的 subagent 數量。

### 2.2.2 平行呼叫 3 個 Subagents

**⚠️ 重要：在同一個訊息中發起所有 Task，Claude Code 會平行執行**

```python
# 同時發起 3 個 Task（平行執行）

# Subagent A: C1-C3
Task(
  description="Phase 2A：WebSearch C1-C3",
  subagent_type="general-purpose",
  model="haiku",  # WebSearch 不需要深度推理
  prompt=f"""
你負責擴充 Citation C1-C3 的補充說明。

## ⚠️ 重要：只使用 WebSearch，不要使用其他工具
- 使用 WebSearch 搜尋術語定義和背景知識
- 不要使用 Read、Write、WebFetch 工具
- 直接回傳 JSON 結果

## 待處理的 Citations

{citations_c1_c3}

## 處理流程

對每個 Citation：
1. 識別原文中的技術術語和核心主題
2. WebSearch 搜尋術語定義（搜尋：「{{術語}} 是什麼 技術 解釋」）
3. WebSearch 搜尋主題背景（搜尋：「{{主題}} 技術方案 原理」）
4. 整理成補充說明（國中生能懂，<= 200 字）

## 輸出格式（JSON）

```json
{{
  "citations": [
    {{
      "id": "C1",
      "terms": ["術語1", "術語2"],
      "supplement": {{
        "term_explanations": "術語解釋...",
        "background": "背景知識...",
        "sources": ["url1", "url2"]
      }}
    }}
  ]
}}
```

請直接輸出 JSON，不要加 code block。
"""
)

# Subagent B: C4-C6
Task(
  description="Phase 2B：WebSearch C4-C6",
  subagent_type="general-purpose",
  model="haiku",
  prompt=f"""
你負責擴充 Citation C4-C6 的補充說明。

## ⚠️ 重要：只使用 WebSearch，不要使用其他工具

## 待處理的 Citations

{citations_c4_c6}

## 處理流程

（同 Subagent A）

## 輸出格式（JSON）

（同 Subagent A）

請直接輸出 JSON，不要加 code block。
"""
)

# Subagent C: C7+
Task(
  description="Phase 2C：WebSearch C7+",
  subagent_type="general-purpose",
  model="haiku",
  prompt=f"""
你負責擴充 Citation C7 及之後的補充說明。

## ⚠️ 重要：只使用 WebSearch，不要使用其他工具

## 待處理的 Citations

{citations_c7_plus}

## 處理流程

（同 Subagent A）

## 輸出格式（JSON）

（同 Subagent A）

請直接輸出 JSON，不要加 code block。
"""
)
```

### 2.2.3 等待所有 Subagent 完成

Claude Code 會自動等待所有平行 Task 完成後再繼續。

---

## 階段 3：主 agent 合併結果

### 2.3.1 解析 Subagent 輸出

```python
# 解析每個 subagent 回傳的 JSON
results_a = json.loads(subagent_a_output)
results_b = json.loads(subagent_b_output)
results_c = json.loads(subagent_c_output)

# 合併所有 citations
all_supplements = {}
for result in [results_a, results_b, results_c]:
    for citation in result.get("citations", []):
        all_supplements[citation["id"]] = citation["supplement"]
```

### 2.3.2 更新 Citation Map

將補充說明合併到 citation_map.md：

```markdown
# Citation Map

### C1
- **來源**：notes.md
- **位置**：第 1-5 行
- **原文**：Framepacing V2 透過SF queue來用部份延遲換部份功耗...
- **補充說明**：
  - **術語解釋**：Framepacing（幀調度）是一種控制 GPU 渲染幀率的技術...
  - **背景知識**：此技術源自 PC 遊戲領域，主要解決幀率不穩定問題...
  - **參考來源**：[url1], [url2]

### C2
...
```

### 2.3.3 寫入最終 Citation Map

```python
Write("./output/phase2/citation_map.md", updated_citation_map)
```

---

## 2.4 Checkpoint 驗證

```bash
python -c "
from pathlib import Path
files = [
    'output/phase2/materials.md',
    'output/phase2/citation_map.md',
    'output/phase2/terms.md'
]
missing = [f for f in files if not Path(f).exists() or Path(f).stat().st_size == 0]
print('missing_or_empty', missing)
raise SystemExit(1 if missing else 0)
"
```

---

## 附錄 A：與 v1 的差異

| 項目 | v1（原設計） | v2（新設計） |
|------|-------------|-------------|
| 執行方式 | 1 個 subagent 串行處理所有內容 | 主 agent + 3 個平行 subagent |
| WebSearch | 每個 citation 依序搜尋 | 3 組平行搜尋 |
| 預估時間 | 9.5 分鐘 | 4-5 分鐘 |
| Context 使用 | subagent 需讀取所有素材 | 主 agent 直接處理，subagent 只收到分配的 citations |

---

## 附錄 B：CITATION_WEB_SEARCH = false 時的流程

若使用者在 Phase 1 設定 `CITATION_WEB_SEARCH = false`：

1. 階段 1 正常執行（讀取素材、建立初步 Citation Map）
2. **跳過階段 2**（不執行 WebSearch）
3. Citation Map 只包含原文摘要，不包含補充說明
4. 進入 Checkpoint 驗證

這是最快的執行路徑，預估 ~2 分鐘完成 Phase 2。

---

## 附錄 C：術語處理詳細規則

### 識別目標

- 英文專有名詞（如：Click-to-Photon、Frame Pacing、Anti-Lag）
- 英文縮寫（如：FPS、SoC、NUMA、CCX）
- 技術術語（如：latency、buffer、pipeline、migration）
- 任何可能讓國中生困惑的詞

### 處理流程

```
對於每個識別到的術語：

1. 先嘗試 WebSearch 查詢
   - 搜尋：「{術語} 是什麼 解釋」
   - 如果找到清楚的解釋 → 記錄到術語清單

2. 如果 WebSearch 找不到或解釋不清楚
   - 使用 AskUserQuestion 詢問使用者

3. 如果使用者也不知道或說可以刪掉
   - 從素材中移除該術語
   - 改用白話文描述
```

### 重要原則

- 寧可多問，也不要留下看不懂的術語
- 如果術語對報告結論很重要，一定要找到解釋
- 所有保留的術語都要加入 glossary.md
