# Phase 1：設定詢問

## 0.1 MCP Yoga Layout 可用性檢查（最優先）

**在開始任何設定之前，必須先確認 mcp-yogalayout 是否可用：**

### 檢查步驟

1. 使用 Bash 執行：`claude mcp list`
2. 確認輸出中包含 `mcp-yogalayout` 且狀態為 `✓ Connected`

### 如果 MCP 未配置或連接失敗

告知使用者並**停止執行**：

```
⚠️ MCP Yoga Layout 未配置或無法連接。

請依序執行以下步驟：

1. 確認 mcp-yogalayout 已編譯：
   cd D:\mcp-yogalayout && cargo build --release

2. 配置 MCP server（全域可用）：
   claude mcp add --scope user --transport stdio mcp-yogalayout -- "D:\mcp-yogalayout\target\release\mcp-yogalayout.exe"

3. 重新啟動 Claude Code

4. 驗證連接：
   claude mcp list
   （應看到 mcp-yogalayout: ... ✓ Connected）

5. 重新執行此 skill
```

### 如果 MCP 已連接

繼續執行下方流程。

---

## 1.0 繼續執行檢測

**檢查是否有之前的執行記錄：**

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
      "question": "審稿次數",
      "header": "進階",
      "multiSelect": false,
      "options": [
        {"label": "5", "description": "審稿 5 輪"},
        {"label": "3", "description": "審稿 3 輪"},
        {"label": "1", "description": "加快產出速度"},
      ]
    },
    {
      "question": "排版審查次數",
      "header": "進階",
      "multiSelect": false,
      "options": [
        {"label": "2", "description": "排版審查次數 5 輪"},
        {"label": "1", "description": "排版審查次數 3 輪"},
        {"label": "0", "description": "加快產出速度"},
      ]
    }
  ]
}
```

---

## 1.2 進階設定詢問

在第一次詢問完成後，使用**第二次** AskUserQuestion 工具詢問進階設定：

```json
{
  "questions": [
    {
      "question": "啟用 Citation 網路補充",
      "header": "Citation",
      "multiSelect": false,
      "options": [
        {"label": "否 (預設)", "description": "關閉 Citation 網路補充"},
        {"label": "是", "description": "啟用 Citation 網路補充"}
      ]
    },
    {
      "question": "渲染引擎",
      "header": "渲染",
      "multiSelect": false,
      "options": [
        {"label": "yoga_pywin32 (推薦)", "description": "Yoga Layout + pywin32，自動排版，支援原生 Chart"},
        {"label": "pptx_shapes", "description": "python-pptx Shapes API，跨平台"},
        {"label": "svg_png", "description": "SVG 生成轉 PNG，圖表精細但無法編輯"}
      ]
    }
  ]
}
```

---

## 全域變數

記錄使用者的選擇：

| 變數 | 說明 | 預設值 |
|------|------|--------|
| `PURPOSE` | 報告目的 | - |
| `EVIDENCE` | 佐證強度 | E0 |
| `MAX_ITERATIONS` | 審稿輪數 | 5 |
| `LAYOUT_ENGINE` | 渲染引擎 | yoga_pywin32 |
| `LAYOUT_REVIEW_ROUNDS` | 排版審查輪數 | 2（0 = 關閉）|
| `REVIEW_WEB_SEARCH` | 審稿時是否啟用網路查證 | false |
| `CITATION_WEB_SEARCH` | Citation Map 是否啟用網路補充 | false |
| `RESUME_FROM` | 從哪個 Phase 繼續 | 1 |

---

## 1.3 Checkpoint 寫入

設定完成後，將全域變數儲存到 checkpoint：

1. 建立目錄（跨平台，必須成功）：

   ```bash
   python -c "from pathlib import Path; Path('output/phase1').mkdir(parents=True, exist_ok=True)"
   ```

2. 使用 Write 工具寫入 `./output/phase1/config.md`（即使值為空也要寫出檔案）：


```markdown
# Phase 1 設定

PURPOSE: {PURPOSE 的值}
EVIDENCE: {EVIDENCE 的值}
MAX_ITERATIONS: {MAX_ITERATIONS 的值}
LAYOUT_ENGINE: {LAYOUT_ENGINE 的值}
LAYOUT_REVIEW_ROUNDS: {LAYOUT_REVIEW_ROUNDS 的值}
REVIEW_WEB_SEARCH: {REVIEW_WEB_SEARCH 的值}
CITATION_WEB_SEARCH: {CITATION_WEB_SEARCH 的值}
INPUT_PATH: {input_path 的值}
```

---

## 1.3.1 Checkpoint 驗證（強制；失敗即中止）

完成 Write 後，必須用 Bash 工具驗證檔案存在且非空：

```bash
python -c "from pathlib import Path; p=Path('output/phase1/config.md'); ok=p.exists() and p.stat().st_size>0; print('phase1_config_ok',ok); raise SystemExit(0 if ok else 1)"
```

若驗證失敗，代表 checkpoint 未落盤或寫入失敗，必須停止流程並修正。

---

## 1.4 Checkpoint 讀取格式


當 `RESUME_FROM > 1` 時，從 `./output/phase1/config.md` 讀取並解析：

- 每行格式為 `變數名: 值`
- 將值還原到對應的全域變數
