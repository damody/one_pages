# Phase 4：主管審稿

> **執行者：subagent**
> **輸入：** `./output/phase3/`（初稿）
> **輸出：** `./output/phase4/`
> **注意：** 如需詢問用戶補充資料，可直接使用 AskUserQuestion

---

## 4.0 入口檢查

**IF `RESUME_FROM` > 4：**
1. 從 `./output/phase4/` 讀取 checkpoint
2. 驗證 `issues.md`, `verification.md`, `user_answers.md` 存在
3. 跳過本 Phase，直接進入 Phase 5

**ELSE：** 正常執行下方流程

---

## 為什麼要用 Sub Agent

- 獨立的上下文，不受之前生成內容的偏見影響
- 真正以「主管視角」審查，而不是自己審自己
- 避免「審跟沒審一樣」的問題

---

## Task 工具調用方式

```
Task(
  description="主管視角審稿",
  subagent_type="general-purpose",
  prompt="""
你是一位嚴格的技術主管（VP/Director 級別），正在審查一份技術報告。

## 你的角色
- 你沒有參與這份報告的撰寫，是第一次看到這份內容
- 你的目標是找出所有可能的問題，確保報告經得起質疑
- 你會用國中生的視角檢查：內容是否讓沒有技術背景的人也能看懂

## 待審查的報告

### one_page.md
{貼上完整的 one_page.md 內容}

### diagrams.md
{貼上完整的 diagrams.md 內容}

### script.md
{貼上完整的 script.md 內容}

### glossary.md
{貼上完整的 glossary.md 內容}

## 原始素材（用於素材完整性檢查）

### materials.md
{貼上完整的 materials.md 內容}

## 審稿檢查清單

請逐一檢查以下項目，產出 Issue List：

1. 結論是否過強？（有沒有證據支持）
2. 數字是否有來源？
3. 條件/範圍是否明確？
4. 行動是否缺前提或風險？
5. 術語是否讓國中生能懂？
5.5 說明是否足夠詳細與白話？
6. 關鍵術語是否有解釋？
7. 邏輯鏈是否完整？
8. 金字塔結構是否成立？
9. 演講稿邏輯是否一步接一步？
10. 技術細節完整性（one_page.md 是否包含所有執行緒/函數）
11. Citation 覆蓋率（所有 Citation 是否都有使用）

**⚠️ 如需詳細的檢查方法，請讀取：** `{skill_dir}/phases/appendix/phase4-checklist-detail.md`

## 輸出格式

### Q1：{問題標題}
- **類型**：{missing_evidence | ambiguity | inconsistency | decision_risk | undefined_term | logic_gap | pyramid_violation | script_logic_gap | not_plain_enough | missing_technical_detail | unused_citation}
- **問題**：{具體描述問題}
- **位置**：{標題/證據/影響/行動/圖表/演講稿/glossary}
- **處理**：{material | web_research | experiment | user_input | rewrite}
- **建議**：{修正方向}

如果沒有發現問題，請明確說明「審稿通過，無需修改」。

## Checkpoint（必須在 subagent 內完成）

1. 建立目錄：
   ```bash
   python -c "from pathlib import Path; Path('output/phase4').mkdir(parents=True, exist_ok=True)"
   ```

2. 寫入檔案（使用 Write 工具）：
   - `./output/phase4/issues.md`：完整 Issue List
   - `./output/phase4/verification.md`：如無查證寫入「# 無查證」
   - `./output/phase4/user_answers.md`：如無需詢問寫入「# 無需詢問」

3. 驗證：
   ```bash
   python -c "from pathlib import Path; files=['output/phase4/issues.md','output/phase4/verification.md','output/phase4/user_answers.md']; missing=[f for f in files if not Path(f).exists() or Path(f).stat().st_size==0]; print('missing_or_empty',missing); raise SystemExit(1 if missing else 0)"
   ```
"""
)
```

---

## Issue 類型說明

| 類型 | 說明 | 處理方式 |
|------|------|----------|
| `missing_evidence` | 缺少證據 | material / web_research / experiment |
| `ambiguity` | 表述模糊 | user_input |
| `inconsistency` | 資料矛盾 | user_input |
| `decision_risk` | 決策風險 | user_input |
| `undefined_term` | 術語未定義 | 加入 glossary |
| `logic_gap` | 邏輯斷鏈 | 補充說明 / 弱化結論 |
| `pyramid_violation` | 金字塔結構問題 | 調整結構 |
| `script_logic_gap` | 演講稿邏輯問題 | 重寫演講稿 |
| `not_plain_enough` | 說明不夠白話 | 提供具體改寫建議 |
| `missing_technical_detail` | 技術細節遺失 | material |
| `unused_citation` | Citation 未使用 | material |

---

## 處理方式分類

| 處理方式 | 說明 | 動作 |
|----------|------|------|
| material | 素材內可回答 | 直接引用素材修正 |
| web_research | 需網路查證 | 進入 Phase 4.5 |
| experiment | 需實驗佐證 | 產出 Experiment Plan |
| user_input | 需使用者補充 | 詢問使用者 |

---

## Phase 4.5：網路查證（如需要）

**觸發條件**：`REVIEW_WEB_SEARCH = true` 且有 `web_research` 類型的 Issue

若 `REVIEW_WEB_SEARCH = false`，跳過此步驟，將 `web_research` 類型改為 `user_input`。

### 查證流程

1. 使用 WebSearch 工具搜尋相關資訊
2. 使用 WebFetch 抓取 2-3 個可信來源
3. 整理查證結果到 `./output/phase4/verification.md`

### 查證結果使用規則

| 可信度 | 處理方式 |
|--------|----------|
| support | 可用於加強證據說明 |
| conflict | 弱化結論，加註「有不同看法」|
| unclear | 保守處理，建議「先做 POC」|

---

## Phase 4.7：詢問使用者

將需要使用者回答的問題整理後詢問：

```markdown
## 需要您確認的問題

### Q1：{問題標題}
- **問題**：{具體描述問題}
- **建議**：{修正方向}

請回答：
1. 同意修正建議
2. 提供補充資訊：{你的補充}
3. 維持原樣，原因：{你的原因}
```

等待使用者回答後，進入 Phase 5。

---

## Checkpoint 寫入

Phase 4 完成後，確保以下檔案已寫入：

- `./output/phase4/issues.md`：完整 Issue List
- `./output/phase4/verification.md`：網路查證結果
- `./output/phase4/user_answers.md`：使用者回答

### 多輪迭代時的版本保留

當迭代輪次 > 1 時，同時複製到 `output/iterations/iter{N}/phase4/`。
