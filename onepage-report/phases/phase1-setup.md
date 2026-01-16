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

使用**一次** AskUserQuestion 工具，同時詢問 4 個問題（AskUserQuestion 上限為 4 題）：

```json
{
  "questions": [
    {
      "question": "這份報告想要達成什麼？",
      "header": "目的",
      "multiSelect": false,
      "options": [
        {"label": "核准 POC", "description": "請主管核准進行概念驗證"},
        {"label": "申請資源", "description": "申請人力、預算或設備"},
        {"label": "採用方案", "description": "建議採用特定技術方案"},
        {"label": "知會進度", "description": "報告專案進度或成果"}
      ]
    },
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
      "question": "審稿時是否用網路搜尋補充資料？",
      "header": "網路查證",
      "multiSelect": false,
      "options": [
        {"label": "關閉 (預設)", "description": "審稿發現資料不足時，直接詢問使用者補充"},
        {"label": "啟用", "description": "審稿發現資料不足時，先用 WebSearch 查證，再詢問使用者確認"}
      ]
    },
    {
      "question": "需要調整進階設定嗎？",
      "header": "進階",
      "multiSelect": true,
      "options": [
        {"label": "使用預設值 (推薦)", "description": "審稿 5 輪、PPTX Shapes 繪圖、排版審查 2 輪"},
        {"label": "改用 SVG/PNG 繪圖", "description": "圖表更精細但無法在 PPT 中編輯"},
        {"label": "減少審稿輪數 (3 輪)", "description": "加快產出速度"},
        {"label": "啟用 Citation 網路補充", "description": "在 Citation Map 中用 WebSearch 補充背景說明"}
      ]
    }
  ]
}
```

---

## 1.2 技術細節程度詢問

在第一次詢問完成後，使用**第二次** AskUserQuestion 工具詢問技術細節保留程度：

```json
{
  "questions": [
    {
      "question": "您希望報告保留多少技術細節？",
      "header": "技術細節",
      "multiSelect": false,
      "options": [
        {"label": "平衡版 (推薦)", "description": "主報告簡潔易懂，技術細節（執行緒、函數、表格）移到附錄投影片"},
        {"label": "執行版", "description": "主報告極度精簡（國小生能懂），所有技術細節都在附錄"},
        {"label": "技術版", "description": "主報告包含完整技術細節，不產生附錄（適合技術同仁）"}
      ]
    }
  ]
}
```

### 技術細節程度說明

| 選項 | DETAIL_LEVEL 值 | 主報告 | 技術附錄 | 適用對象 |
|------|----------------|--------|---------|---------|
| 平衡版（推薦）| BALANCED | 簡化易懂，結論+推論 | 完整技術細節（執行緒/函數/表格）| 主管 + 技術同仁 |
| 執行版 | EXECUTIVE | 極度精簡，每區塊 2-3 點 | 完整技術細節 | VP/Director 級別 |
| 技術版 | TECHNICAL | 完整技術細節 | 不產生 | 技術同仁 |

**範例差異**：

| 內容 | EXECUTIVE | BALANCED | TECHNICAL |
|------|-----------|----------|-----------|
| 主報告描述 | 「Touch2Photon 降低 81%」| 「Touch2Photon 降低 81%，因減少處理器搬移次數」| 「Touch2Photon 降低 81%，執行緒 InputReader → InputDispatcher → ViewRootImpl → RenderThread...」|
| 技術附錄 | 完整執行緒列表 + 函數呼叫鏈 + 技術表格 | 完整執行緒列表 + 函數呼叫鏈 + 技術表格 | 無（所有細節在主報告）|
| 投影片數量 | 1 (主報告) + 2-3 (技術附錄) + N (附錄圖) + 1 (術語) | 1 (主報告) + 2-3 (技術附錄) + N (附錄圖) + 1 (術語) | 1 (主報告) + N (附錄圖) + 1 (術語) |

---

### 進階設定解析

根據使用者在「進階」問題的選擇：

| 選項 | 對應變數設定 |
|------|-------------|
| 使用預設值 | 全部用預設 |
| 改用 SVG/PNG 繪圖 | `DIAGRAM_METHOD = svg_png` |
| 減少審稿輪數 | `MAX_ITERATIONS = 3` |
| 啟用 Citation 網路補充 | `CITATION_WEB_SEARCH = true` |

## 全域變數

記錄使用者的選擇：

| 變數 | 說明 | 預設值 |
|------|------|--------|
| `PURPOSE` | 報告目的 | - |
| `EVIDENCE` | 佐證強度 | E0 |
| `DETAIL_LEVEL` | 技術細節保留程度 | BALANCED |
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
DETAIL_LEVEL: {DETAIL_LEVEL 的值}
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
