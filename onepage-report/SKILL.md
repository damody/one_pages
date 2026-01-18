---
name: onepage-report
description: 從素材資料夾產生一頁投影片 + 演講稿
arguments: [input_path]
---

# 一頁投影片產生器

> 版本：v4.1（簡化架構 - TECHNICAL 模式 + Yoga 自動排版）

將素材（資料夾/PPTX/URL）轉換成專業的一頁投影片與演講稿。

## 架構說明

**主 agent 只負責調控**，Phase 2-6 全部由 subagent 執行：
- 每個 Phase 的 subagent 讀取上一個 Phase 的 checkpoint 資料
- 每個 Phase 完成後輸出到 `./output/phase{N}/`
- 支援從任意 Phase 繼續執行

**v4.1 簡化：**
- 移除 DETAIL_LEVEL 選項（固定為 TECHNICAL 模式）
- 所有技術細節都放在 one_page.md，不再分流到 technical_appendix.md
- Phase 6 使用 Yoga Layout 自動計算字體大小，確保內容放得下
- 移除字數限制，內容量由 Yoga 自動處理排版

---

## 執行流程概述

| Phase | 說明 | 執行者 | 規範檔案 |
|-------|------|--------|----------|
| 1 | 設定詢問 | **主 agent** | `{skill_dir}/phases/phase1-setup.md` |
| 2 | 讀取素材 | subagent | `{skill_dir}/phases/phase2-input.md` |
| 3 | 產生初稿 | subagent | `{skill_dir}/phases/phase3-draft.md` |
| 4 | 主管審稿 | subagent | `{skill_dir}/phases/phase4-review.md` |
| 5 | 重寫迭代 | subagent | `{skill_dir}/phases/phase5-revise.md` |
| 6 | 渲染輸出 | subagent | `{skill_dir}/phases/phase6-render.md` |

---

## 全域變數

| 變數 | 說明 | 預設值 |
|------|------|--------|
| `PURPOSE` | 報告目的 | - |
| `EVIDENCE` | 佐證強度 | E0 |
| `MAX_ITERATIONS` | 審稿輪數 | 5 |
| `DIAGRAM_METHOD` | 繪圖方式 | pptx_shapes |
| `LAYOUT_ENGINE` | 佈局引擎 | yoga_pywin32 |
| `LAYOUT_REVIEW_ROUNDS` | 排版審查輪數 | 2 |
| `REVIEW_WEB_SEARCH` | 審稿時是否啟用網路查證 | false |
| `CITATION_WEB_SEARCH` | Citation Map 是否啟用網路補充 | false |
| `RESUME_FROM` | 從哪個 Phase 繼續（1-6） | 1 |

### Yoga Layout 字體約束

| 元素類型 | 最小字體 |
|---------|---------|
| 標題 | 14pt |
| 本文 | 10pt |
| 小字註解 | 8pt |

---

## Phase 1：設定詢問（主 agent 執行）

**執行前請讀取：** `Read {skill_dir}/phases/phase1-setup.md`

主 agent 直接執行，使用 AskUserQuestion 工具詢問使用者設定。

---

## Phase 2-6：Subagent 執行

**每個 Phase 都使用 Task tool 呼叫 subagent**，prompt 格式如下：

```
請執行 Phase {N}：{Phase 說明}

**規範檔案：** 請讀取 {skill_dir}/phases/phase{N}-xxx.md

**輸入資料：** 請讀取 ./output/phase{N-1}/ 目錄下的所有檔案

**輸出位置：** ./output/phase{N}/

請嚴格按照規範執行，完成後將結果寫入輸出目錄。
```

---

## Phase 2：讀取素材

**Task tool prompt：**
```
請執行 Phase 2：讀取素材

規範檔案：Read {skill_dir}/phases/phase2-input.md
輸入資料：Read ./output/phase1/config.md
素材路徑：{input_path}

輸出位置：./output/phase2/
```

---

## Phase 3：產生初稿

**Task tool prompt：**
```
請執行 Phase 3：產生初稿

規範檔案：
- Read {skill_dir}/phases/phase3-draft.md
- Read {skill_dir}/templates/one-page-format.md
- Read {skill_dir}/templates/diagrams-spec.md
- Read {skill_dir}/templates/glossary-format.md
- Read {skill_dir}/templates/script-format.md

輸入資料：Read ./output/phase2/ 目錄下所有檔案

輸出位置：./output/phase3/
```

---

## Phase 4：主管審稿

**Task tool prompt：**
```
請執行 Phase 4：主管審稿

規範檔案：Read {skill_dir}/phases/phase4-review.md
輸入資料：Read ./output/phase3/ 目錄下所有檔案

如需詢問用戶補充資料，請直接使用 AskUserQuestion 工具。

輸出位置：./output/phase4/
```

---

## Phase 5：重寫迭代

**Task tool prompt：**
```
請執行 Phase 5：根據審稿回饋重寫

規範檔案：Read {skill_dir}/phases/phase5-revise.md
輸入資料：
- Read ./output/phase3/ 目錄下所有檔案（原稿）
- Read ./output/phase4/ 目錄下所有檔案（審稿結果）

輸出位置：./output/phase5/
```

### 多輪迭代

當 `MAX_ITERATIONS > 1` 時，主 agent 控制迭代：

```
WHILE 迭代計數 <= MAX_ITERATIONS:
    呼叫 Phase 4 subagent
    IF 審稿通過: BREAK
    IF 達到上限: BREAK
    呼叫 Phase 5 subagent
```

---

## Phase 6：渲染輸出

**Task tool prompt：**
```
請執行 Phase 6：渲染輸出

規範檔案：Read {skill_dir}/phases/phase6-render.md
輸入資料：Read ./output/phase5/ 目錄下所有檔案

輸出位置：./output/
```

---

## 輸出檔案

```
./output/
├── phase1/                      # Phase 1 checkpoint
│   └── config.md
├── phase2/                      # Phase 2 checkpoint
│   ├── materials.md
│   ├── citation_map.md
│   └── terms.md
├── phase3/                      # Phase 3 checkpoint
│   ├── one_page.md              # 包含所有技術細節
│   ├── diagrams.md
│   ├── table.md
│   ├── glossary.md
│   └── script.md
├── phase4/                      # Phase 4 checkpoint
│   ├── issues.md
│   ├── verification.md
│   └── user_answers.md
├── phase5/                      # Phase 5 checkpoint
│   ├── one_page.md              # 包含所有技術細節
│   ├── diagrams.md
│   ├── table.md
│   ├── glossary.md
│   ├── script.md
│   └── citation_map.md
├── iterations/                  # 多輪迭代版本保留
│   ├── iter1/phase4/, phase5/
│   └── iter2/phase4/, phase5/
├── final.pptx                   # 最終輸出：主投影片
├── script.txt                   # 演講稿
├── citation_map.md              # 來源對照表
└── glossary.md                  # 術語詞彙表
```

---

## 錯誤處理

**執行前請讀取：** `Read {skill_dir}/reference/error-handling.md`

---

## 檔案結構（v4.1 簡化）

```
onepage-report/
├── SKILL.md                     # 本檔案（主入口）
├── phases/                      # 執行階段規範
│   ├── phase1-setup.md
│   ├── phase2-input.md
│   ├── phase3-draft.md          # 簡化：移除 DETAIL_LEVEL 分支
│   ├── phase4-review.md
│   ├── phase5-revise.md
│   ├── phase6-render.md         # Yoga Layout + pywin32
│   ├── phase6-render-pptx-shapes.md  # 備選渲染方式
│   ├── phase6-render-svg.md     # 備選渲染方式
│   └── appendix/                # 附錄檔案（按需載入）
│       ├── phase4-checklist-detail.md          # 審稿檢查清單詳解
│       └── phase5-content-recovery.md          # 內容恢復流程
├── templates/                   # 輸出模板與格式規範
│   ├── one-page-format.md       # 簡化：移除字數限制
│   ├── diagrams-spec.md
│   ├── glossary-format.md
│   ├── script-format.md
│   ├── experiment-plan.md
│   └── appendix/                # 模板附錄
│       └── diagrams-spec-types.md  # 圖表類型詳細規範
├── reference/                   # 技術參考文件
│   ├── render_pywin32.py        # pywin32 渲染器
│   ├── modules_pywin32/         # pywin32 圖表模組
│   ├── svg-generation.md
│   ├── pptx-shapes.md
│   └── error-handling.md
└── scripts/                     # Python 腳本
    ├── extract_pptx.py
    ├── extract_pdf.py
    └── pptx_reference.py
```

---

## 核心原則提醒

1. **國中生能懂標準**：所有內容必須讓沒有技術背景的人也能理解
2. **內容完整性**：絕對禁止刪減內容，由 Yoga Layout 自動處理排版
3. **Sub Agent 審稿**：每輪審稿必須使用獨立的 Sub Agent
4. **完整輸出**：每輪重寫都要輸出完整的 Markdown 文件
5. **Citation 追溯**：所有論述都要能追溯到素材來源
6. **Yoga 自動排版**：內容量不限制，Phase 6 自動計算字體大小（最小 10pt，小字 8pt）
