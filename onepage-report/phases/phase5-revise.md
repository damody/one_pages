# Phase 5：根據回饋重寫

> **執行者：主 agent 控制 + subagent 重寫**
> **輸入：** `./output/phase3/`（原稿）+ `./output/phase4/`（審稿結果）
> **輸出：** `./output/phase5/`（只需 3 個文件）
> **優化：** 主 agent 負責所有 I/O，subagent 只做純重寫（無工具呼叫）
>
> **bypass 文件：** script.md, glossary.md 從 Phase 3 直接傳到 Phase 6，不進入審稿迴圈

---

## 5.0 入口檢查

**IF `RESUME_FROM` > 5：**
1. 從 `./output/phase5/` 讀取 checkpoint，跳過本 Phase
2. 直接進入 Phase 6

**IF 審稿通過（Phase 4 issues.md 顯示「審稿通過，無需修改」）：**
1. 直接複製 Phase 3 的文件到 Phase 5
2. 跳過重寫，進入 Phase 6

**ELSE：** 正常執行下方流程

---

## 為什麼要用 Sub Agent

- 獨立的上下文，可以專注於修正任務
- 避免主 agent 上下文過長影響效能
- 但由主 agent 負責 I/O，減少 subagent 工具呼叫開銷

---

## 執行流程（主 agent 負責 I/O）

### 步驟 1：主 agent 讀取輸入檔案

```
使用 Read 工具讀取以下 4 個檔案：
- ./output/phase3/one_page.md
- ./output/phase3/diagrams.md
- ./output/phase3/table.md
- ./output/phase4/issues.md
```

### 步驟 2：主 agent 呼叫 subagent 重寫

將讀取的內容直接嵌入 prompt，subagent **不使用任何工具**，只做純重寫：

```
Task(
  description="根據審稿回饋重寫報告（純重寫）",
  subagent_type="general-purpose",
  prompt="""
你是一位專業的技術寫作者，正在根據主管的審稿回饋修正報告。

## 你的角色
- 你要根據 issues.md 中列出的問題，修正報告內容
- 你必須輸出**完整的**修正後文件，不是只有差異

## ⚠️ 重要：不要使用任何工具
- 不要使用 Read 工具（內容已提供）
- 不要使用 Write 工具（主 agent 會負責寫入）
- 直接分析下方內容，然後回傳修正後的完整文件

## 審稿發現的問題

{主 agent 貼上完整的 issues.md 內容}

## 原始報告（需修正）

### one_page.md
{主 agent 貼上完整的 one_page.md 內容}

### diagrams.md
{主 agent 貼上完整的 diagrams.md 內容}

### table.md
{主 agent 貼上完整的 table.md 內容}

## 修正策略

| 問題類型 | 處理方式 |
|----------|----------|
| missing_evidence | 弱化結論，加註「仍需驗證」|
| ambiguity | 明確化表述，加入條件說明 |
| inconsistency | 統一數據，標註來源 |
| decision_risk | 加入風險說明 |
| undefined_term | 在首次使用處加入解釋 |
| logic_gap | 補充推導過程 |
| pyramid_violation | 調整結構順序 |
| one_page_logic_gap | 重寫相關段落 |
| not_plain_enough | 用更白話的方式重寫 |

## 禁止事項

- ✗ 不可硬撐沒有證據的結論
- ✗ 不可隱藏矛盾
- ✗ 不可在沒數字時寫具體百分比
- ✗ 不可忽略審稿指出的問題

## 輸出格式（直接回傳，不要用工具）

請依序輸出三個完整的文件：

### ONE_PAGE_MD_START
{完整的修正後 one_page.md 內容}
### ONE_PAGE_MD_END

### DIAGRAMS_MD_START
{完整的修正後 diagrams.md 內容}
### DIAGRAMS_MD_END

### TABLE_MD_START
{完整的修正後 table.md 內容}
### TABLE_MD_END

請直接輸出結果，不要使用任何工具。
"""
)
```

### 步驟 3：主 agent 解析並寫入結果

收到 subagent 的回傳後，主 agent 執行：

```
1. 解析 subagent 回傳的內容：
   - 提取 ONE_PAGE_MD_START 和 ONE_PAGE_MD_END 之間的內容
   - 提取 DIAGRAMS_MD_START 和 DIAGRAMS_MD_END 之間的內容
   - 提取 TABLE_MD_START 和 TABLE_MD_END 之間的內容

2. 建立目錄：
   python -c "from pathlib import Path; Path('output/phase5').mkdir(parents=True, exist_ok=True)"

3. 使用 Write 工具寫入：
   - ./output/phase5/one_page.md
   - ./output/phase5/diagrams.md
   - ./output/phase5/table.md

4. 驗證：
   python -c "from pathlib import Path; files=['output/phase5/one_page.md','output/phase5/diagrams.md','output/phase5/table.md']; missing=[f for f in files if not Path(f).exists() or Path(f).stat().st_size==0]; print('phase5_ok', not missing); raise SystemExit(1 if missing else 0)"
```

---

## Phase 5.5：多輪審稿迭代

當 `MAX_ITERATIONS > 1` 時，重複 Phase 4 → Phase 5 流程。

### 關鍵原則：每輪審稿必須使用 Sub Agent

**為什麼每輪都要用 Sub Agent？**
- AI 傾向認為自己寫的內容是正確的
- 容易忽略自己剛才犯的錯誤
- 缺乏獨立的批判視角

### 迭代邏輯

```
迭代計數 = 1

WHILE 迭代計數 <= MAX_ITERATIONS:
    【必須用 Task tool 呼叫 sub agent】執行 Phase 4（審稿）

    IF 審稿通過（無 Issue 或全部為 minor）:
        BREAK  # 進入 Phase 6

    IF 迭代計數 == MAX_ITERATIONS:
        強制保守輸出
        BREAK

    執行 Phase 4.5~4.7（查證/實驗/詢問）
    執行 Phase 5（重寫）
    迭代計數 += 1
```

---

## 強制保守輸出（達到 MAX_ITERATIONS 仍有問題時）

當達到最大迭代次數但仍有未解決的 Issue 時：

### 1. 弱化所有未解決的宣稱
- 標題加「初步」「在特定條件下」
- 數字加「約」「估計」
- 結論加「仍需驗證」

### 2. 加入風險註記

```markdown
## 風險與限制
- {未解決 Issue 1}：{風險說明}
- {未解決 Issue 2}：{風險說明}
```

### 3. 調整行動建議
- 「全面採用」→「建議先做 POC 驗證」
- 「立即執行」→「待補充佐證後再決定」

### 4. 告知使用者

```
⚠️ 注意：本報告經過 {N} 輪審稿，仍有以下問題未完全解決：
- {Issue 1}
- {Issue 2}

已自動採取保守處理，建議：
1. 補充更多佐證後再報告
2. 或以目前保守版本先行報告，說明後續會補充
```

---

## 多輪迭代時的版本保留

當迭代輪次 > 1 時，同時複製到 `output/iterations/iter{N}/phase5/`。
