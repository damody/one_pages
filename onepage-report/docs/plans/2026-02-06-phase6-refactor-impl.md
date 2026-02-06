# Phase 6 重構實作計畫

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 將 Phase 6 從「subagent 產生 Python 程式碼」改為「subagent 產生 JSON + 固定渲染器」，減少 80% context 消耗。

**Architecture:** 主 agent 呼叫 MCP yogalayout 取得座標，subagent 只產生結構化 JSON（slide_data.json），固定的 Python 渲染器（render_from_json.py）讀取 JSON 後渲染 PPTX。

**Tech Stack:** Python 3.11+, pywin32, mcp-yogalayout, JSON Schema

---

## Task 1: 建立 slide_data.json Schema

**Files:**
- Create: `onepage-report/templates/slide-data-schema.json`

**Step 1: 建立 JSON Schema 檔案**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "slide-data-schema.json",
  "title": "Slide Data Schema",
  "description": "Phase 6 渲染器的輸入資料格式",
  "type": "object",
  "required": ["metadata", "pages"],
  "properties": {
    "metadata": {
      "type": "object",
      "required": ["title"],
      "properties": {
        "title": {"type": "string"},
        "subtitle": {"type": "string"},
        "total_pages": {"type": "integer", "minimum": 1}
      }
    },
    "pages": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["page", "elements"],
        "properties": {
          "page": {"type": "integer", "minimum": 1},
          "elements": {
            "type": "array",
            "items": {"$ref": "#/$defs/element"}
          }
        }
      }
    }
  },
  "$defs": {
    "element": {
      "type": "object",
      "required": ["id", "kind"],
      "properties": {
        "id": {"type": "string"},
        "kind": {"enum": ["text", "section", "figure", "table", "callout"]}
      },
      "allOf": [
        {
          "if": {"properties": {"kind": {"const": "text"}}},
          "then": {
            "properties": {
              "content": {"type": "string"},
              "role": {"enum": ["title", "subtitle", "h2", "body", "caption"]}
            },
            "required": ["content"]
          }
        },
        {
          "if": {"properties": {"kind": {"const": "section"}}},
          "then": {
            "properties": {
              "title": {"type": "string"},
              "bullets": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["title", "bullets"]
          }
        },
        {
          "if": {"properties": {"kind": {"const": "figure"}}},
          "then": {
            "properties": {
              "type": {"enum": ["before_after", "flow", "timeline", "platform_compare", "architecture", "line_chart", "bar_chart", "pie_chart"]},
              "data": {"type": "object"}
            },
            "required": ["type", "data"]
          }
        },
        {
          "if": {"properties": {"kind": {"const": "table"}}},
          "then": {
            "properties": {
              "headers": {"type": "array", "items": {"type": "string"}},
              "rows": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}}
            },
            "required": ["headers", "rows"]
          }
        },
        {
          "if": {"properties": {"kind": {"const": "callout"}}},
          "then": {
            "properties": {
              "content": {"type": "string"},
              "style": {"enum": ["info", "warning", "success"]}
            },
            "required": ["content"]
          }
        }
      ]
    },
    "before_after_data": {
      "type": "object",
      "properties": {
        "before": {
          "type": "object",
          "properties": {
            "title": {"type": "string"},
            "steps": {"type": "array", "items": {"type": "string"}}
          }
        },
        "after": {
          "type": "object",
          "properties": {
            "title": {"type": "string"},
            "steps": {"type": "array", "items": {"type": "string"}}
          }
        }
      }
    },
    "flow_data": {
      "type": "object",
      "properties": {
        "stages": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "title": {"type": "string"},
              "nodes": {"type": "array", "items": {"type": "string"}}
            }
          }
        }
      }
    },
    "timeline_data": {
      "type": "object",
      "properties": {
        "points": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "time": {"type": "string"},
              "label": {"type": "string"},
              "duration": {"type": "string"}
            }
          }
        }
      }
    },
    "platform_compare_data": {
      "type": "object",
      "properties": {
        "platforms": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "name": {"type": "string"},
              "items": {
                "type": "array",
                "items": {
                  "type": "object",
                  "properties": {
                    "text": {"type": "string"},
                    "status": {"enum": ["ok", "warning", "fail"]}
                  }
                }
              }
            }
          }
        }
      }
    },
    "architecture_data": {
      "type": "object",
      "properties": {
        "layers": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "name": {"type": "string"},
              "components": {"type": "array", "items": {"type": "string"}}
            }
          }
        }
      }
    }
  }
}
```

**Step 2: 驗證 Schema 語法正確**

Run: `python -c "import json; json.load(open('onepage-report/templates/slide-data-schema.json')); print('Schema valid')"`
Expected: `Schema valid`

**Step 3: Commit**

```bash
git add onepage-report/templates/slide-data-schema.json
git commit -m "feat(phase6): add slide-data JSON schema for structured rendering"
```

---

## Task 2: 建立範例 slide_data.json

**Files:**
- Create: `onepage-report/templates/slide-data-example.json`

**Step 1: 建立範例檔案**

```json
{
  "metadata": {
    "title": "天璣 SoC 導入 Anti-Lag 技術方案",
    "subtitle": "參考 AMD Anti-Lag 2 已驗證的技術路徑",
    "total_pages": 2
  },
  "pages": [
    {
      "page": 1,
      "elements": [
        {
          "id": "title",
          "kind": "text",
          "role": "title",
          "content": "天璣 SoC 導入 Anti-Lag 技術方案"
        },
        {
          "id": "subtitle",
          "kind": "text",
          "role": "subtitle",
          "content": "參考 AMD Anti-Lag 2 已驗證的技術路徑"
        },
        {
          "id": "section:success_factors",
          "kind": "section",
          "title": "參考案例：PC 平台驗證數據",
          "bullets": [
            "在遊戲引擎內嵌入同步點 [C1]",
            "解決 CPU-Bound 造成的 [[Frame Queue]] 堆積",
            "實測改善：Click-to-Photon 延遲降低 23-37%"
          ]
        },
        {
          "id": "fig:main:antilag_sdk",
          "kind": "figure",
          "type": "before_after",
          "data": {
            "before": {
              "title": "改善前：現況 Baseline",
              "steps": [
                "觸控事件 T=0ms",
                "InputDispatcher T≈3-5ms",
                "遊戲引擎處理 T≈10-15ms",
                "GPU 渲染 T≈16-33ms",
                "Frame Queue 等待 T≈15ms",
                "SurfaceFlinger T≈8-12ms",
                "Display T≈88ms"
              ]
            },
            "after": {
              "title": "改善後：導入 Anti-Lag SDK",
              "steps": [
                "觸控事件 T=0ms",
                "InputDispatcher T≈3-5ms",
                "遊戲引擎 + SDK 同步 T≈10-15ms",
                "GPU 渲染 T≈16-33ms",
                "Frame Queue ≈0ms (消除)",
                "SurfaceFlinger T≈8-12ms",
                "Display T≈78ms"
              ]
            }
          }
        },
        {
          "id": "section:problem",
          "kind": "section",
          "title": "現況問題",
          "bullets": [
            "Android 遊戲平均 Click-to-Photon 延遲：86-88ms",
            "Frame Queue 堆積造成 15ms 額外延遲",
            "競品（高通、三星）已開始布局低延遲技術"
          ]
        },
        {
          "id": "section:benefit",
          "kind": "section",
          "title": "預期效益",
          "bullets": [
            "系統總延遲降低 5-15%（保守估計）",
            "絕對值改善 4-10ms",
            "建立天璣平台低延遲競爭力"
          ]
        }
      ]
    },
    {
      "page": 2,
      "elements": [
        {
          "id": "section:action",
          "kind": "section",
          "title": "行動建議",
          "bullets": [
            "Phase 1：技術預研（2週）- 驗證 Fence API 可用性",
            "Phase 2：原型開發（4-6週）- SDK v0.1 + Demo",
            "Phase 3：廠商驗證（4週）- 與遊戲廠商合作測試"
          ]
        },
        {
          "id": "fig:appendix:timeline",
          "kind": "figure",
          "type": "timeline",
          "data": {
            "points": [
              {"time": "Phase 1", "label": "技術預研", "duration": "2週"},
              {"time": "Phase 2", "label": "原型開發", "duration": "4-6週"},
              {"time": "Phase 3", "label": "廠商驗證", "duration": "4週"}
            ]
          }
        },
        {
          "id": "table:metrics",
          "kind": "table",
          "headers": ["指標", "基線", "目標", "測試方法"],
          "rows": [
            ["Click-to-Photon", "86-88ms", "降低 ≥5%", "GameBench"],
            ["Frame Queue", "1.8 幀", "≤1.2 幀", "Systrace"],
            ["Frame Time σ", "3-4ms", "降低 ≥10%", "Perfetto"]
          ]
        }
      ]
    }
  ]
}
```

**Step 2: 驗證範例符合 Schema**

Run: `python -c "import json; d=json.load(open('onepage-report/templates/slide-data-example.json')); print(f'Valid: {len(d[\"pages\"])} pages, {sum(len(p[\"elements\"]) for p in d[\"pages\"])} elements')"`
Expected: `Valid: 2 pages, 8 elements`

**Step 3: Commit**

```bash
git add onepage-report/templates/slide-data-example.json
git commit -m "feat(phase6): add slide-data example for reference"
```

---

## Task 3: 建立 render_from_json.py 入口腳本

**Files:**
- Create: `onepage-report/scripts/render_from_json.py`

**Step 1: 建立入口腳本**

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
render_from_json.py - Phase 6 固定渲染器

用法:
    python render_from_json.py \
        --layout layout.json \
        --data slide_data.json \
        --output final.pptx

此腳本是固定的，不需要 subagent 產生。
Subagent 只需產生 slide_data.json。
"""

import argparse
import json
import os
import sys
from pathlib import Path

# 加入 reference 目錄到路徑
SCRIPT_DIR = Path(__file__).parent
REFERENCE_DIR = SCRIPT_DIR.parent / "reference"
sys.path.insert(0, str(REFERENCE_DIR))

from render_pywin32 import LayoutRenderer, SLIDE_WIDTH_PT, SLIDE_HEIGHT_PT
from modules_pywin32._colors_pywin32 import (
    COLOR_TEXT, ACCENT_BLUE, ACCENT_GREEN, ACCENT_ORANGE, ACCENT_RED, ACCENT_PURPLE
)


def load_json(path: str) -> dict:
    """載入 JSON 檔案"""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def convert_slide_data_to_content_data(slide_data: dict) -> dict:
    """
    將 slide_data.json 格式轉換為 render_pywin32 的 content_data 格式

    slide_data 格式：結構化的頁面和元素
    content_data 格式：按類型分組的字典（texts, items, tables, diagrams_content）
    """
    content_data = {
        "texts": {},
        "items": {},
        "tables": {},
        "charts": {},
        "flows": {},
        "comparisons": {},
        "diagrams_content": {}
    }

    for page in slide_data.get("pages", []):
        for elem in page.get("elements", []):
            elem_id = elem.get("id", "")
            kind = elem.get("kind", "")

            if kind == "text":
                content_data["texts"][elem_id] = elem.get("content", "")

            elif kind == "section":
                # Section 包含標題和條列項目
                content_data["texts"][f"{elem_id}:title"] = elem.get("title", "")
                content_data["items"][elem_id] = elem.get("bullets", [])

            elif kind == "table":
                content_data["tables"][elem_id] = {
                    "headers": elem.get("headers", []),
                    "rows": elem.get("rows", [])
                }

            elif kind == "figure":
                fig_type = elem.get("type", "")
                fig_data = elem.get("data", {})

                # 轉換為 diagrams_content 格式
                content_data["diagrams_content"][elem_id] = {
                    "type": fig_type,
                    **convert_figure_data(fig_type, fig_data)
                }

            elif kind == "callout":
                content_data["texts"][elem_id] = elem.get("content", "")

    return content_data


def convert_figure_data(fig_type: str, fig_data: dict) -> dict:
    """轉換圖表資料格式"""
    if fig_type == "before_after":
        before = fig_data.get("before", {})
        after = fig_data.get("after", {})
        return {
            "before": {
                "title": before.get("title", "改善前"),
                "flow": before.get("steps", [])
            },
            "after": {
                "title": after.get("title", "改善後"),
                "flow": after.get("steps", [])
            }
        }

    elif fig_type == "flow":
        return {
            "stages": fig_data.get("stages", [])
        }

    elif fig_type == "timeline":
        return {
            "points": fig_data.get("points", [])
        }

    elif fig_type == "platform_compare":
        platforms = fig_data.get("platforms", [])
        if len(platforms) >= 2:
            return {
                "platform1": {"title": platforms[0].get("name", "")},
                "platform2": {"title": platforms[1].get("name", "")},
                "rows": [item.get("text", "") for item in platforms[0].get("items", [])]
            }
        return {}

    elif fig_type == "architecture":
        return {
            "layers": fig_data.get("layers", [])
        }

    elif fig_type in ("line_chart", "bar_chart", "pie_chart"):
        return fig_data

    return fig_data


def merge_layout_with_slide_data(layout: dict, slide_data: dict) -> dict:
    """
    合併 layout.json 和 slide_data.json

    layout.json 提供座標，slide_data.json 提供內容
    """
    # 將 slide_data 的元素按 ID 索引
    elements_by_id = {}
    for page in slide_data.get("pages", []):
        for elem in page.get("elements", []):
            elem_id = elem.get("id", "")
            elements_by_id[elem_id] = elem
            # 同時加入 fig: 前綴版本
            if not elem_id.startswith("fig:"):
                elements_by_id[f"fig:{elem_id}"] = elem

    return elements_by_id


def render(layout_path: str, data_path: str, output_path: str, script_path: str = None):
    """
    主渲染函數

    Args:
        layout_path: MCP yogalayout 輸出的 layout.json
        data_path: subagent 產生的 slide_data.json
        output_path: 輸出 PPTX 路徑
        script_path: 演講稿輸出路徑（可選）
    """
    print(f"[render_from_json] 載入 layout: {layout_path}")
    layout = load_json(layout_path)

    print(f"[render_from_json] 載入 slide_data: {data_path}")
    slide_data = load_json(data_path)

    # 轉換為 content_data 格式
    content_data = convert_slide_data_to_content_data(slide_data)

    # 合併元素索引
    elements_index = merge_layout_with_slide_data(layout, slide_data)
    content_data["_elements_index"] = elements_index

    print(f"[render_from_json] 開始渲染...")

    # 建立渲染器
    renderer = LayoutRenderer(visible=False)
    renderer.create_presentation()

    # 處理多頁
    pages = layout.get("pages", [layout])  # 相容單頁和多頁格式

    for page_data in pages:
        page_num = page_data.get("page_number", 1)
        print(f"[render_from_json] 渲染第 {page_num} 頁...")
        renderer.render_from_layout(page_data, content_data)

    # 儲存
    abs_output = os.path.abspath(output_path)
    renderer.save(abs_output, auto_close=True)
    print(f"[render_from_json] 完成: {abs_output}")

    # 產生演講稿（如果有指定）
    if script_path:
        generate_script(slide_data, script_path)

    return abs_output


def generate_script(slide_data: dict, output_path: str):
    """從 slide_data 產生演講稿"""
    lines = []
    metadata = slide_data.get("metadata", {})

    lines.append(f"# {metadata.get('title', '報告')}")
    lines.append("")

    for page in slide_data.get("pages", []):
        page_num = page.get("page", 1)
        lines.append(f"## 第 {page_num} 頁")
        lines.append("")

        for elem in page.get("elements", []):
            kind = elem.get("kind", "")

            if kind == "section":
                title = elem.get("title", "")
                bullets = elem.get("bullets", [])
                lines.append(f"### {title}")
                for bullet in bullets:
                    lines.append(f"- {bullet}")
                lines.append("")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"[render_from_json] 演講稿已儲存: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Phase 6 固定渲染器 - 將 JSON 資料渲染為 PPTX"
    )
    parser.add_argument(
        "--layout", required=True,
        help="MCP yogalayout 輸出的 layout.json 路徑"
    )
    parser.add_argument(
        "--data", required=True,
        help="slide_data.json 路徑"
    )
    parser.add_argument(
        "--output", required=True,
        help="輸出 PPTX 路徑"
    )
    parser.add_argument(
        "--script",
        help="演講稿輸出路徑（可選）"
    )

    args = parser.parse_args()

    render(
        layout_path=args.layout,
        data_path=args.data,
        output_path=args.output,
        script_path=args.script
    )


if __name__ == "__main__":
    main()
```

**Step 2: 驗證腳本語法正確**

Run: `python -m py_compile onepage-report/scripts/render_from_json.py && echo "Syntax OK"`
Expected: `Syntax OK`

**Step 3: Commit**

```bash
git add onepage-report/scripts/render_from_json.py
git commit -m "feat(phase6): add fixed JSON renderer script"
```

---

## Task 4: 建立 subagent prompt 模板

**Files:**
- Create: `onepage-report/templates/phase6-subagent-prompt.md`

**Step 1: 建立輕量 prompt 模板**

```markdown
# Phase 6 Subagent：產生 slide_data.json

你的任務是將報告內容轉換為結構化的 slide_data.json。

## 輸入

### 報告內容（one_page_yoga.md）
```
{one_page_content}
```

### 圖表內容（content.json 的 diagrams_info）
```json
{diagrams_info}
```

## 輸出格式

產生 slide_data.json，格式如下：

```json
{
  "metadata": {
    "title": "報告標題",
    "subtitle": "副標題",
    "total_pages": N
  },
  "pages": [
    {
      "page": 1,
      "elements": [
        {"id": "title", "kind": "text", "role": "title", "content": "..."},
        {"id": "section:xxx", "kind": "section", "title": "...", "bullets": [...]},
        {"id": "fig:xxx", "kind": "figure", "type": "before_after", "data": {...}}
      ]
    }
  ]
}
```

## element kind 類型

| kind | 必要欄位 |
|------|---------|
| text | content, role (title/subtitle/h2/body) |
| section | title, bullets |
| figure | type, data |
| table | headers, rows |
| callout | content |

## figure type 對應

| type | data 格式 |
|------|----------|
| before_after | {before: {title, steps}, after: {title, steps}} |
| flow | {stages: [{title, nodes}]} |
| timeline | {points: [{time, label, duration}]} |
| platform_compare | {platforms: [{name, items: [{text, status}]}]} |
| architecture | {layers: [{name, components}]} |

## 規則

1. 保留所有 [C1]、[[Term]] 標記
2. 每個 ## 標題對應一個 section element
3. 每個 <fig> 標籤對應一個 figure element
4. 不要遺漏任何內容

直接輸出 JSON，不要加 markdown code block。
```

**Step 2: Commit**

```bash
git add onepage-report/templates/phase6-subagent-prompt.md
git commit -m "feat(phase6): add lightweight subagent prompt template"
```

---

## Task 5: 修改 phase6-render.md

**Files:**
- Modify: `onepage-report/phases/phase6-render.md`

**Step 1: 備份原檔案**

Run: `cp onepage-report/phases/phase6-render.md onepage-report/phases/phase6-render.md.bak`

**Step 2: 重寫 phase6-render.md**

將整個檔案替換為以下內容（大幅簡化）：

```markdown
# Phase 6：渲染輸出（v2 - JSON 模板設計）

> **執行者：主 agent**
> **輸入：** `./output/phase5/` + `./output/phase3/`（bypass 檔案）
> **輸出：** `./output/final.pptx` + `./output/script.txt`

---

## 6.0 架構概述

```
Phase 6 v2 流程：
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
│                                                              │
│ 4. 主 agent：執行固定渲染器                                    │
│    python render_from_json.py → final.pptx                   │
└──────────────────────────────────────────────────────────────┘
```

**核心改變**：
- Subagent 不需要讀取任何 Python 模組
- Subagent 只產生結構化 JSON
- 渲染器是固定的 Python 腳本

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

主 agent 直接呼叫 MCP 工具：

```
mcp__mcp-yogalayout__layout_compute_slide_layout(
  markdown_path="output/one_page_yoga.md",
  output_dir="output",
  theme_path="workspace/themes/default.json",
  options={
    "auto_paginate": true,
    "density": "compact"
  }
)
```

**儲存結果**：將 MCP 回傳的 JSON 寫入 `./output/layout.json`

---

## 6.3 呼叫 Subagent 產生 slide_data.json

### 6.3.1 讀取 prompt 模板

```
Read {skill_dir}/templates/phase6-subagent-prompt.md
```

### 6.3.2 讀取輸入資料

```
Read ./output/one_page_yoga.md
Read ./output/content.json
```

### 6.3.3 呼叫 Subagent

```python
Task(
  description="Phase 6：產生 slide_data.json",
  subagent_type="general-purpose",
  model="haiku",  # 輕量任務用 Haiku
  prompt=f"""
{phase6_subagent_prompt}

## 輸入

### 報告內容
{one_page_yoga_content}

### 圖表資訊
{content_json}

請產生 slide_data.json。
"""
)
```

### 6.3.4 儲存 Subagent 輸出

將 subagent 回傳的 JSON 寫入 `./output/slide_data.json`

### 6.3.5 驗證 slide_data.json

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
📊 ./output/final.pptx
📝 ./output/script.txt

中間檔案（可用於除錯）：
- ./output/layout.json（MCP 座標）
- ./output/slide_data.json（結構化內容）
```
```

**Step 3: Commit**

```bash
git add onepage-report/phases/phase6-render.md
git commit -m "refactor(phase6): simplify to JSON template design

- Remove subagent Python module reading
- Add fixed render_from_json.py renderer
- Subagent only produces slide_data.json
- Estimated 80% context reduction"
```

---

## Task 6: 更新 SKILL.md

**Files:**
- Modify: `onepage-report/SKILL.md:212-232`

**Step 1: 更新 Phase 6 說明**

找到 `## Phase 6：渲染輸出` 區塊，替換為：

```markdown
## Phase 6：渲染輸出（v2 - JSON 模板設計）

**執行流程：** 詳見 `{skill_dir}/phases/phase6-render.md`

**v2 改進**：
- Subagent 不再讀取 Python 模組（減少 80% context）
- Subagent 只產生 `slide_data.json`（結構化資料）
- 固定渲染器 `render_from_json.py` 處理 PPTX 產生

**主 agent 執行步驟**：
1. 執行 `yoga_converter.py` 合併內容
2. 呼叫 MCP yogalayout 取得座標
3. 呼叫輕量 subagent 產生 `slide_data.json`
4. 執行 `render_from_json.py` 產生 PPTX

**Subagent prompt**：
- 讀取 `{skill_dir}/templates/phase6-subagent-prompt.md`
- 只需傳入 `content.json` 和報告內容
- 預估 token：15-20k（vs 原本 98k）
```

**Step 2: Commit**

```bash
git add onepage-report/SKILL.md
git commit -m "docs(skill): update Phase 6 documentation for v2 design"
```

---

## Task 7: 整合測試

**Files:**
- Test files in `./output/`

**Step 1: 準備測試資料**

使用現有的 `./output/phase5/` 檔案（如果存在），或使用範例資料。

**Step 2: 執行完整流程**

```bash
# 1. yoga_converter
python .claude/skills/onepage-report/scripts/yoga_converter.py \
  --one-page ./output/phase5/one_page.md \
  --diagrams ./output/phase5/diagrams.md \
  --output ./output/one_page_yoga.md \
  --content-json ./output/content.json

# 2. 使用範例 slide_data（先跳過 subagent）
cp .claude/skills/onepage-report/templates/slide-data-example.json ./output/slide_data.json

# 3. 執行渲染器（需要先有 layout.json）
# 注意：需要先呼叫 MCP 產生 layout.json
```

**Step 3: 驗證輸出**

```bash
python -c "
from pathlib import Path
pptx = Path('output/final.pptx')
if pptx.exists():
    print(f'PPTX 大小: {pptx.stat().st_size / 1024:.1f} KB')
else:
    print('PPTX 不存在')
"
```

**Step 4: Commit 測試結果**

```bash
git add -A
git commit -m "test(phase6): verify JSON template rendering pipeline"
```

---

## 完成檢查清單

- [ ] Task 1: slide-data-schema.json 已建立
- [ ] Task 2: slide-data-example.json 已建立
- [ ] Task 3: render_from_json.py 已建立並通過語法檢查
- [ ] Task 4: phase6-subagent-prompt.md 已建立
- [ ] Task 5: phase6-render.md 已更新為 v2
- [ ] Task 6: SKILL.md 已更新
- [ ] Task 7: 整合測試通過
