# Phase 1：設定詢問

使用**一次** AskUserQuestion 工具，同時詢問以下問題：

```json
{
  "questions": [
    {
      "question": "這份報告需要什麼程度的佐證？",
      "header": "佐證",
      "multiSelect": false,
      "options": [
        {"label": "E0 使用現有數據 (預設)", "description": "不要求新實驗，使用素材中的現有數據"},
        {"label": "E1 輕佐證", "description": "需要 1-2 個關鍵指標（如 FPS、功耗）"},
        {"label": "E2 強佐證", "description": "需要完整實驗設計與數據"}
      ]
    },
    {
      "question": "需要幾輪審稿？",
      "header": "審稿",
      "multiSelect": false,
      "options": [
        {"label": "5 輪 (預設)", "description": "審稿→重寫→審稿，最多五輪"},
        {"label": "3 輪", "description": "審稿→重寫→審稿，最多三輪"},
        {"label": "自訂", "description": "輸入自訂次數"}
      ]
    },
    {
      "question": "示意圖要用什麼方式繪製？",
      "header": "繪圖",
      "multiSelect": false,
      "options": [
        {"label": "PPTX Shapes (預設)", "description": "使用 PowerPoint 內建圖形繪製，可直接在 PPT 中編輯"},
        {"label": "SVG/PNG", "description": "使用 SVG 生成後轉 PNG 嵌入，圖表精細但無法編輯"}
      ]
    },
    {
      "question": "需要幾輪排版審查？",
      "header": "排版",
      "multiSelect": false,
      "options": [
        {"label": "2 輪 (預設)", "description": "檢查元素重疊，自動修正 2 次"},
        {"label": "1 輪", "description": "快速檢查一次"},
        {"label": "3 輪", "description": "嚴格審查三次"},
        {"label": "關閉", "description": "不進行排版審查"}
      ]
    },
    {
      "question": "審稿時是否用網路搜尋補充資料？",
      "header": "查證搜尋",
      "multiSelect": false,
      "options": [
        {"label": "關閉 (預設)", "description": "審稿發現資料不足時，直接詢問使用者補充"},
        {"label": "啟用", "description": "審稿發現資料不足時，先用 WebSearch 查證，再詢問使用者確認"}
      ]
    },
    {
      "question": "Citation Map 是否用網路搜尋補充說明？",
      "header": "引用搜尋",
      "multiSelect": false,
      "options": [
        {"label": "關閉 (預設)", "description": "Citation Map 只記錄素材來源，不補充外部說明"},
        {"label": "啟用", "description": "在 Citation Map 中用 WebSearch 補充相關背景說明"}
      ]
    }
  ]
}
```

使用者回答後，再**單獨詢問**報告目的（因為這是文字輸入）：

```json
{
  "questions": [
    {
      "question": "這份報告想要達成什麼？（範例：核准 POC、申請加人、採用方案 A、核准預算）",
      "header": "目的",
      "multiSelect": false,
      "options": [
        {"label": "核准 POC", "description": "請主管核准進行概念驗證"},
        {"label": "申請資源", "description": "申請人力、預算或設備"},
        {"label": "採用方案", "description": "建議採用特定技術方案"},
        {"label": "知會進度", "description": "報告專案進度或成果"}
      ]
    }
  ]
}
```

如果使用者在「審稿」選擇「自訂」，再追問具體次數。

## 全域變數

記錄使用者的選擇：

| 變數 | 說明 | 預設值 |
|------|------|--------|
| `PURPOSE` | 報告目的 | - |
| `EVIDENCE` | 佐證強度 | E0 |
| `MAX_ITERATIONS` | 審稿輪數 | 5 |
| `DIAGRAM_METHOD` | 繪圖方式 | pptx_shapes |
| `LAYOUT_REVIEW_ROUNDS` | 排版審查輪數 | 2（0 = 關閉）|
| `REVIEW_WEB_SEARCH` | 審稿時是否啟用網路查證 | false |
| `CITATION_WEB_SEARCH` | Citation Map 是否啟用網路補充 | false |
