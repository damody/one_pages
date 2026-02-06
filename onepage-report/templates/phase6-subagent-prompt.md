# Phase 6 Subagent：產生 slide_data.json

你的任務是將報告內容轉換為結構化的 slide_data.json。

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

| kind | 必要欄位 | 說明 |
|------|---------|------|
| text | content, role | role: title/subtitle/h2/body/caption |
| section | title, bullets | 章節標題 + 條列項目 |
| figure | type, data | 圖表，type 決定 data 格式 |
| table | headers, rows | 表格 |
| callout | content | 提示框 |

## figure type 對應的 data 格式

### before_after（前後對比）
```json
{
  "before": {"title": "改善前", "steps": ["步驟1", "步驟2"]},
  "after": {"title": "改善後", "steps": ["步驟1", "步驟2"]}
}
```

### flow（流程圖）
```json
{
  "stages": [
    {"title": "階段1", "nodes": ["節點A", "節點B"]},
    {"title": "階段2", "nodes": ["節點C"]}
  ]
}
```

### timeline（時間軸）
```json
{
  "points": [
    {"time": "Phase 1", "label": "技術預研", "duration": "2週"},
    {"time": "Phase 2", "label": "原型開發", "duration": "4週"}
  ]
}
```

### platform_compare（平台對比）
```json
{
  "platforms": [
    {"name": "PC", "items": [{"text": "Driver 層控制", "status": "ok"}]},
    {"name": "Android", "items": [{"text": "需 SDK", "status": "warning"}]}
  ]
}
```

### architecture（架構圖）
```json
{
  "layers": [
    {"name": "Application", "components": ["Game", "SDK"]},
    {"name": "Framework", "components": ["SurfaceFlinger"]}
  ]
}
```

## 轉換規則

1. **標題**：`# xxx` → `{"kind": "text", "role": "title", "content": "xxx"}`
2. **副標題**：`> xxx` 或副標題行 → `{"kind": "text", "role": "subtitle"}`
3. **章節**：`## xxx` + 條列 → `{"kind": "section", "title": "xxx", "bullets": [...]}`
4. **圖表**：`<fig id="xxx" ... />` → `{"kind": "figure", "id": "xxx", "type": "...", "data": {...}}`
5. **表格**：Markdown 表格 → `{"kind": "table", "headers": [...], "rows": [...]}`

## 重要

1. **保留所有標記**：`[C1]`、`[[Term]]` 等標記必須保留在 content 中
2. **不要遺漏內容**：每個 `##` 標題都要對應一個 section
3. **圖表 ID 格式**：使用 `fig:main:xxx` 或 `fig:appendix:xxx`
4. **直接輸出 JSON**：不要加 markdown code block
