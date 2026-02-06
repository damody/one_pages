# Phase 4-5：審稿與重寫（v2 - 合併設計）

> **執行者：主 agent 控制 + subagent 審稿+重寫**
> **輸入：** `./output/phase3/`（初稿）
> **輸出：** `./output/phase4/issues.md` + `./output/phase5/`（修正後）
> **優化：** 每輪只呼叫 1 個 subagent（審稿+重寫合併），減少 50% subagent 呼叫

---

## 4.0 架構概述（v2 改進）

```
Phase 4-5 v2 流程（預估每輪 1 分鐘，vs 原本 2 分鐘）：
┌──────────────────────────────────────────────────────────────┐
│ 每輪迭代（最多 3 輪）：                                        │
│                                                              │
│ ┌────────────────────────────────────────────────────────┐   │
│ │ 單一 Subagent：審稿 + 重寫合併                          │   │
│ │ 輸入：one_page.md, diagrams.md, table.md               │   │
│ │ 輸出：                                                  │   │
│ │   - ISSUES（問題清單，或 "PASS"）                       │   │
│ │   - ONE_PAGE.MD（修正後，或 "NO_CHANGE"）               │   │
│ │   - DIAGRAMS.MD（修正後，或 "NO_CHANGE"）               │   │
│ │   - TABLE.MD（修正後，或 "NO_CHANGE"）                  │   │
│ └────────────────────────────────────────────────────────┘   │
│                                                              │
│ 迴圈終止條件：                                                │
│   - ISSUES = "PASS"（審稿通過）                              │
│   - 達到 MAX_ITERATIONS（強制結束）                          │
└──────────────────────────────────────────────────────────────┘
```

**核心改變**：
- ✅ 審稿+重寫合併為 1 個 subagent（vs 原本 2 個）
- ✅ 每輪 context 減少 ~50%（檔案只讀 1 次）
- ✅ 3 輪總計：3 個 subagent（vs 原本 6 個）

---

## 4.1 迭代迴圈

```python
iteration = 1

WHILE iteration <= MAX_ITERATIONS:
    # 讀取當前版本
    IF iteration == 1:
        輸入來源 = "./output/phase3/"
    ELSE:
        輸入來源 = "./output/phase5/"

    # 呼叫合併 subagent
    result = 呼叫 subagent（見 4.2 節）

    # 解析結果
    IF result.issues == "PASS":
        複製當前版本到 phase5（如果尚未存在）
        BREAK  # 審稿通過，進入 Phase 6

    # 寫入結果
    Write "./output/phase4/issues.md"
    Write "./output/phase5/one_page.md"
    Write "./output/phase5/diagrams.md"
    Write "./output/phase5/table.md"

    iteration += 1

IF iteration > MAX_ITERATIONS:
    執行強制保守輸出（見 4.5 節）
```

---

## 4.2 呼叫合併 Subagent

### 步驟 1：主 agent 讀取輸入

```
IF 第 1 輪：
    Read ./output/phase3/one_page.md
    Read ./output/phase3/diagrams.md
    Read ./output/phase3/table.md
ELSE：
    Read ./output/phase5/one_page.md
    Read ./output/phase5/diagrams.md
    Read ./output/phase5/table.md
```

### 步驟 2：呼叫 Subagent

```python
Task(
  description=f"第 {iteration} 輪審稿+重寫",
  subagent_type="general-purpose",
  model="sonnet",  # 審稿需要深度推理
  prompt=f"""
你是一位嚴格的技術主管，正在審查並修正一份技術報告。

## 你的角色
- 你沒有參與這份報告的撰寫，是第一次看到這份內容
- 你會找出問題，**並直接修正**
- 如果沒有問題，直接回報 "PASS"

## ⚠️ 重要：不要使用任何工具
- 不要使用 Read 工具（內容已提供）
- 不要使用 Write 工具（主 agent 會負責寫入）
- 直接分析並回傳結果

## 待審查的報告

### one_page.md
{one_page_content}

### diagrams.md
{diagrams_content}

### table.md
{table_content}

## 審稿檢查清單

1. 結論是否過強？（有沒有證據支持）
2. 條件/範圍是否明確？
3. 行動是否缺前提或風險？
4. 術語是否讓國中生能懂？
5. 說明是否足夠詳細與白話？
6. 邏輯鏈是否完整？
7. 金字塔結構是否成立？

**⚠️ 重要限制：最多只報告 3 個最關鍵的問題。**

## 修正策略

| 問題類型 | 處理方式 |
|----------|----------|
| missing_evidence | 弱化結論，加註「仍需驗證」|
| ambiguity | 明確化表述，加入條件說明 |
| inconsistency | 統一數據，標註來源 |
| undefined_term | 在首次使用處加入解釋 |
| logic_gap | 補充推導過程 |
| not_plain_enough | 用更白話的方式重寫 |

## 輸出格式

### ISSUES
（如果有問題，列出最多 3 個；如果沒問題，寫 "PASS"）

Q1：{問題標題}
- 類型：{類型}
- 問題：{描述}
- 位置：{位置}
- 修正：{如何修正}

### ONE_PAGE_MD
（完整的修正後內容，或 "NO_CHANGE" 如果不需修改）

### DIAGRAMS_MD
（完整的修正後內容，或 "NO_CHANGE" 如果不需修改）

### TABLE_MD
（完整的修正後內容，或 "NO_CHANGE" 如果不需修改）
"""
)
```

### 步驟 3：主 agent 解析並寫入

```python
# 解析 subagent 回傳
issues = 提取 "### ISSUES" 到 "### ONE_PAGE_MD" 之間的內容
one_page = 提取 "### ONE_PAGE_MD" 到 "### DIAGRAMS_MD" 之間的內容
diagrams = 提取 "### DIAGRAMS_MD" 到 "### TABLE_MD" 之間的內容
table = 提取 "### TABLE_MD" 之後的內容

# 檢查是否通過
IF "PASS" in issues:
    print("審稿通過")
    # 如果 phase5 不存在，複製 phase3
    BREAK

# 建立目錄
python -c "from pathlib import Path; Path('output/phase4').mkdir(parents=True, exist_ok=True)"
python -c "from pathlib import Path; Path('output/phase5').mkdir(parents=True, exist_ok=True)"

# 寫入 issues
Write "./output/phase4/issues.md" with issues

# 寫入修正後的文件（跳過 NO_CHANGE）
IF one_page != "NO_CHANGE":
    Write "./output/phase5/one_page.md" with one_page
ELSE:
    複製原檔案到 phase5

# 同理處理 diagrams 和 table
```

---

## 4.3 Checkpoint 驗證

```bash
python -c "
from pathlib import Path
files = [
    'output/phase4/issues.md',
    'output/phase5/one_page.md',
    'output/phase5/diagrams.md',
    'output/phase5/table.md'
]
missing = [f for f in files if not Path(f).exists()]
print('missing:', missing)
raise SystemExit(1 if missing else 0)
"
```

---

## 4.4 Phase 4.5：網路查證（如需要）

**觸發條件**：`REVIEW_WEB_SEARCH = true` 且 issues 中有需要網路查證的問題

若 `REVIEW_WEB_SEARCH = false`，跳過此步驟。

### 查證流程

1. 使用 WebSearch 工具搜尋相關資訊
2. 使用 WebFetch 抓取 2-3 個可信來源
3. 整理查證結果到 `./output/phase4/verification.md`
4. 在下一輪迭代中將查證結果加入 subagent prompt

---

## 4.5 強制保守輸出

當達到 MAX_ITERATIONS 但仍有未解決的 Issue 時：

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

### 3. 告知使用者

```
⚠️ 注意：本報告經過 {N} 輪審稿，仍有以下問題未完全解決：
- {Issue 1}
- {Issue 2}

已自動採取保守處理。
```

---

## 4.6 多輪迭代時的版本保留

當迭代輪次 > 1 時，同時複製到：
- `output/iterations/iter{N}/phase4/`
- `output/iterations/iter{N}/phase5/`

---

## 附錄 A：Issue 類型說明

| 類型 | 說明 | 處理方式 |
|------|------|----------|
| `missing_evidence` | 缺少證據 | 弱化結論 |
| `ambiguity` | 表述模糊 | 明確化 |
| `inconsistency` | 資料矛盾 | 統一數據 |
| `decision_risk` | 決策風險 | 加風險說明 |
| `undefined_term` | 術語未定義 | 加解釋 |
| `logic_gap` | 邏輯斷鏈 | 補充推導 |
| `not_plain_enough` | 說明不夠白話 | 重寫 |

---

## 附錄 B：與 v1 的差異

| 項目 | v1（原設計） | v2（新設計） |
|------|-------------|-------------|
| 每輪 subagent | 2 個（審稿 + 重寫分開） | 1 個（合併） |
| 每輪 context | 檔案讀取 2 次 | 檔案讀取 1 次 |
| 3 輪總 subagent | 6 個 | 3 個 |
| 預估每輪時間 | 2 分鐘 | 1 分鐘 |

---

## 附錄 C：bypass 文件說明

- `script.md` 和 `glossary.md` 從 Phase 3 直接傳到 Phase 6
- 不進入審稿迴圈（Phase 4-5 只處理 3 個文件）
- 優化效果：減少 I/O 量，加速審稿迴圈
