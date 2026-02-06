# Phase 6：渲染輸出（v2 - JSON 模板設計）

> **執行者：主 agent**
> **輸入：** `./output/phase5/` + `./output/phase3/`（bypass 檔案）
> **輸出：** `./output/final.pptx` + `./output/script.txt`

---

## 6.0 架構概述（v2 改進）

```
Phase 6 v2 流程（預估 15-20k tokens，vs 原本 98k）：
┌──────────────────────────────────────────────────────────────┐
│ 1. 主 agent：執行 yoga_converter.py 合併內容                   │
│    輸出：one_page_yoga.md, content.json                       │
│                                                              │
│ 2. 主 agent：呼叫 MCP yogalayout                              │
│    輸出：layout.json（座標）                                   │
│                                                              │
│ 3. 主 agent：呼叫輕量 subagent                                 │
│    輸入：content.json + prompt 模板（50 行）                   │
│    輸出：slide_data.json                                      │
│    ⚠️ Subagent 不需讀取任何 Python 模組！                      │
│                                                              │
│ 4. 主 agent：執行固定渲染器                                    │
│    python render_from_json.py → final.pptx                   │
└──────────────────────────────────────────────────────────────┘
```

**核心改變**：
- ✅ Subagent 不再讀取 Python 模組（減少 80% context）
- ✅ Subagent 只產生結構化 JSON
- ✅ 渲染器是固定的 Python 腳本，不需每次產生

---

## 6.1 準備輸入檔案

### 6.1.1 建立輸出目錄

```bash
python -c "from pathlib import Path; Path('output').mkdir(parents=True, exist_ok=True)"
```

### 6.1.2 執行 yoga_converter.py

```bash
python {skill_dir}/scripts/yoga_converter.py \
  --one-page ./output/phase5/one_page.md \
  --diagrams ./output/phase5/diagrams.md \
  --output ./output/one_page_yoga.md \
  --content-json ./output/content.json \
  --mode one_page
```

### 6.1.3 驗證輸出

```bash
python -c "
from pathlib import Path
yoga = Path('output/one_page_yoga.md')
content = Path('output/content.json')
ok = yoga.exists() and content.exists()
print(f'yoga_converter OK: {ok}')
if not ok: raise SystemExit(1)
"
```

---

## 6.2 呼叫 MCP yogalayout

主 agent 直接呼叫 MCP 工具（不透過 subagent）：

```python
mcp__mcp-yogalayout__layout_compute_slide_layout(
  markdown_path="output/one_page_yoga.md",
  output_dir="output",
  theme_path="workspace/themes/default.json",
  options={
    "auto_paginate": True,
    "density": "compact"
  }
)
```

**儲存結果**：將 MCP 回傳的 JSON 寫入 `./output/layout.json`

```python
# 使用 Write 工具儲存 MCP 回傳結果
Write("./output/layout.json", mcp_result_json)
```

---

## 6.3 呼叫 Subagent 產生 slide_data.json

### 6.3.1 讀取必要檔案

```
Read {skill_dir}/templates/phase6-subagent-prompt.md  # 輕量 prompt（50 行）
Read ./output/content.json                            # 圖表資訊
```

**⚠️ 注意：不需要讀取任何 Python 模組！**

### 6.3.2 呼叫 Subagent

```python
Task(
  description="Phase 6：產生 slide_data.json",
  subagent_type="general-purpose",
  model="haiku",  # 輕量任務用 Haiku 加速
  prompt=f"""
{phase6_subagent_prompt}

## 輸入

### 報告內容（one_page_yoga.md）
{one_page_yoga_content}

### 圖表資訊（content.json）
{content_json}

請產生 slide_data.json，直接輸出 JSON。
"""
)
```

### 6.3.3 儲存 Subagent 輸出

將 subagent 回傳的 JSON 寫入 `./output/slide_data.json`

### 6.3.4 驗證 slide_data.json

```bash
python -c "
import json
from pathlib import Path
data = json.loads(Path('output/slide_data.json').read_text(encoding='utf-8'))
pages = len(data.get('pages', []))
elements = sum(len(p.get('elements', [])) for p in data.get('pages', []))
print(f'slide_data.json: {pages} pages, {elements} elements')
if pages == 0: raise SystemExit(1)
"
```

---

## 6.4 執行固定渲染器

```bash
python {skill_dir}/scripts/render_from_json.py \
  --layout ./output/layout.json \
  --data ./output/slide_data.json \
  --output ./output/final.pptx \
  --script ./output/script.txt
```

**渲染器特點**：
- 固定的 Python 腳本，不需 subagent 產生
- 自動轉換 slide_data.json 為 render_pywin32 格式
- 支援所有圖表類型（before_after, flow, timeline 等）

---

## 6.5 Checkpoint 驗證

```bash
python -c "
from pathlib import Path
required = [
    'output/one_page_yoga.md',
    'output/content.json',
    'output/layout.json',
    'output/slide_data.json',
    'output/final.pptx',
    'output/script.txt'
]
missing = [f for f in required if not Path(f).exists()]
print('missing:', missing)
raise SystemExit(1 if missing else 0)
"
```

---

## 6.6 完成

```
✅ 報告產生完成！

輸出檔案：
📊 ./output/final.pptx（投影片）
📝 ./output/script.txt（演講稿）

中間檔案（可用於除錯）：
- ./output/layout.json（MCP 座標）
- ./output/slide_data.json（結構化內容）
- ./output/one_page_yoga.md（合併後 Markdown）
- ./output/content.json（圖表資訊）
```

---

## 附錄 A：slide_data.json 格式參考

詳見 `{skill_dir}/templates/slide-data-schema.json`

### 快速參考

```json
{
  "metadata": {"title": "...", "subtitle": "...", "total_pages": N},
  "pages": [
    {
      "page": 1,
      "elements": [
        {"id": "title", "kind": "text", "role": "title", "content": "..."},
        {"id": "section:xxx", "kind": "section", "title": "...", "bullets": [...]},
        {"id": "fig:xxx", "kind": "figure", "type": "before_after", "data": {...}},
        {"id": "table:xxx", "kind": "table", "headers": [...], "rows": [...]}
      ]
    }
  ]
}
```

### element kind 類型

| kind | 必要欄位 |
|------|---------|
| text | content, role |
| section | title, bullets |
| figure | type, data |
| table | headers, rows |
| callout | content |

### figure type 對應

| type | data 格式 |
|------|----------|
| before_after | `{before: {title, steps}, after: {title, steps}}` |
| flow | `{stages: [{title, nodes}]}` |
| timeline | `{points: [{time, label, duration}]}` |
| platform_compare | `{platforms: [{name, items}]}` |
| architecture | `{layers: [{name, components}]}` |

---

## 附錄 B：與 v1 的差異

| 項目 | v1（原設計） | v2（新設計） |
|------|-------------|-------------|
| Subagent 讀取模組 | 8 個 Python 模組 (~2500 行) | 0 個 |
| Subagent prompt | ~300 行 | ~50 行 |
| Subagent 輸出 | Python 程式碼 | JSON 資料 |
| 渲染器 | 每次產生 | 固定腳本 |
| 預估 context | 98k tokens | 15-20k tokens |
| MCP 呼叫 | Subagent 執行 | 主 agent 執行 |

---

## 附錄 C：錯誤處理

### slide_data.json 驗證失敗

如果 subagent 輸出的 JSON 格式不正確：

1. 檢查 subagent 輸出是否包含 markdown code block（應該移除）
2. 重新呼叫 subagent，強調「直接輸出 JSON，不要加 code block」

### 渲染器執行失敗

如果 `render_from_json.py` 失敗：

1. 檢查 `layout.json` 是否包含 `elements` 或 `pages`
2. 檢查 `slide_data.json` 的圖表 ID 是否與 `layout.json` 匹配
3. 查看錯誤訊息並修正對應的 JSON 資料
