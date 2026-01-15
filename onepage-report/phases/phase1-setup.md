# Phase 1：設定詢問

## 1.0 繼續執行檢測（最優先）

**首先檢查是否有之前的執行記錄：**

1. 使用 Glob 工具檢查 `./output/phase*/` 目錄是否存在
2. 如果存在任何 phase 目錄，詢問使用者：

```json
{
  "questions": [
    {
      "question": "檢測到之前的執行記錄，要從哪裡繼續？",
      "header": "繼續",
      "multiSelect": false,
      "options": [
        {"label": "從頭開始", "description": "清除所有 checkpoint，重新執行"},
        {"label": "從 Phase 2 繼續", "description": "使用 phase1/ 的設定，從讀取素材開始"},
        {"label": "從 Phase 3 繼續", "description": "使用 phase2/ 的素材，從產生初稿開始"},
        {"label": "從 Phase 4 繼續", "description": "使用 phase3/ 的初稿，從審稿開始"}
      ]
    }
  ]
}
```

**注意：** 只顯示實際存在的選項。例如如果只有 phase1/ 存在，就只顯示「從頭開始」和「從 Phase 2 繼續」。

3. 根據使用者選擇設定 `RESUME_FROM` 變數：
   - 從頭開始：`RESUME_FROM = 1`，並刪除所有 `./output/phase*/` 目錄
   - 從 Phase N 繼續：`RESUME_FROM = N`

4. 如果 `RESUME_FROM > 1`：
   - 讀取 `./output/phase1/config.md` 還原全域變數
   - 跳過下方的設定詢問，直接進入下一個 Phase

---

## 1.1 設定詢問（僅當 RESUME_FROM = 1 時執行）

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
| `RESUME_FROM` | 從哪個 Phase 繼續 | 1 |

---

## 1.3 Checkpoint 寫入

設定完成後，將全域變數儲存到 checkpoint：

1. 建立目錄：`mkdir -p ./output/phase1`

2. 使用 Write 工具寫入 `./output/phase1/config.md`：

```markdown
# Phase 1 設定

PURPOSE: {PURPOSE 的值}
EVIDENCE: {EVIDENCE 的值}
MAX_ITERATIONS: {MAX_ITERATIONS 的值}
DIAGRAM_METHOD: {DIAGRAM_METHOD 的值}
LAYOUT_REVIEW_ROUNDS: {LAYOUT_REVIEW_ROUNDS 的值}
REVIEW_WEB_SEARCH: {REVIEW_WEB_SEARCH 的值}
CITATION_WEB_SEARCH: {CITATION_WEB_SEARCH 的值}
INPUT_PATH: {input_path 的值}
```

---

## 1.4 Checkpoint 讀取格式

當 `RESUME_FROM > 1` 時，從 `./output/phase1/config.md` 讀取並解析：

- 每行格式為 `變數名: 值`
- 將值還原到對應的全域變數
