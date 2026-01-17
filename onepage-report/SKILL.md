---
name: onepage-report
description: 從素材資料夾產生一頁投影片 + 演講稿
arguments: [input_path]
---

# 一頁投影片產生器

> 版本：v3.0（Subagent 架構）

將素材（資料夾/PPTX/URL）轉換成專業的一頁投影片與演講稿。

## 架構說明

**主 agent 只負責調控**，Phase 2-6 全部由 subagent 執行：
- 每個 Phase 的 subagent 讀取上一個 Phase 的 checkpoint 資料
- 每個 Phase 完成後輸出到 `./output/phase{N}/`
- 支援從任意 Phase 繼續執行

---

## 執行流程概述

| Phase | 說明 | 執行者 | 輸入 | 規範檔案 |
|-------|------|--------|------|----------|
| 1 | 設定詢問 | **主 agent** | 用戶輸入 | `{skill_dir}/phases/phase1-setup.md` |
| 2 | 讀取素材 | subagent | phase1 checkpoint | `{skill_dir}/phases/phase2-input.md` |
| 3 | 產生初稿 | subagent | phase2 checkpoint | `{skill_dir}/phases/phase3-draft.md` |
| 4 | 主管審稿 | subagent | phase3 checkpoint | `{skill_dir}/phases/phase4-review.md` |
| 5 | 重寫迭代 | subagent | phase4 checkpoint | `{skill_dir}/phases/phase5-revise.md` |
| 6 | 渲染輸出 | subagent | phase5 checkpoint | `{skill_dir}/phases/phase6-render.md` |

---

## 全域變數

| 變數 | 說明 | 預設值 |
|------|------|--------|
| `PURPOSE` | 報告目的 | - |
| `EVIDENCE` | 佐證強度 | E0 |
| `DETAIL_LEVEL` | 技術細節保留程度 | BALANCED |
| `MAX_ITERATIONS` | 審稿輪數 | 5 |
| `DIAGRAM_METHOD` | 繪圖方式 | pptx_shapes |
| `LAYOUT_REVIEW_ROUNDS` | 排版審查輪數 | 2 |
| `REVIEW_WEB_SEARCH` | 審稿時是否啟用網路查證 | false |
| `CITATION_WEB_SEARCH` | Citation Map 是否啟用網路補充 | false |
| `RESUME_FROM` | 從哪個 Phase 繼續（1-6） | 1 |

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

## Phase 2：讀取素材（subagent）

**Task tool prompt：**
```
請執行 Phase 2：讀取素材

規範檔案：Read {skill_dir}/phases/phase2-input.md
輸入資料：Read ./output/phase1/config.md
素材路徑：{input_path}

輸出位置：./output/phase2/
```

---

## Phase 3：產生初稿（subagent）

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

## Phase 4：主管審稿（subagent）

**Task tool prompt：**
```
請執行 Phase 4：主管審稿

規範檔案：Read {skill_dir}/phases/phase4-review.md
輸入資料：Read ./output/phase3/ 目錄下所有檔案

如需詢問用戶補充資料，請直接使用 AskUserQuestion 工具。

輸出位置：./output/phase4/
```

---

## Phase 5：重寫迭代（subagent）

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

## Phase 6：渲染輸出（subagent）

**Task tool prompt：**
```
請執行 Phase 6：渲染輸出

規範檔案：
- Read {skill_dir}/phases/phase6-render.md
- Read {skill_dir}/reference/pptx-shapes.md（或 svg-generation.md）

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
│   ├── one_page.md
│   ├── diagrams.md
│   ├── table.md
│   ├── glossary.md
│   └── script.md
├── phase4/                      # Phase 4 checkpoint
│   ├── issues.md
│   ├── verification.md
│   └── user_answers.md
├── phase5/                      # Phase 5 checkpoint
│   ├── one_page.md
│   ├── diagrams.md
│   ├── table.md
│   ├── glossary.md
│   ├── script.md
│   └── citation_map.md
├── iterations/                  # 多輪迭代版本保留
│   ├── iter1/phase4/, phase5/
│   └── iter2/phase4/, phase5/
├── one_page.pptx                # 最終輸出：主投影片
├── speaker_script.md            # 演講稿
├── main_diagram.svg/png         # 主圖（如用 svg_png）
├── appendix_diagram_*.svg/png   # 附錄圖
├── citation_map.md              # 來源對照表
├── glossary.md                  # 術語詞彙表
└── render_this.py               # 產生 PPTX 的腳本
```

---

## 錯誤處理

**執行前請讀取：** `Read {skill_dir}/reference/error-handling.md`

---

## 檔案結構

```
onepage-report/
├── SKILL.md              # 本檔案（主入口）
├── phases/               # 執行階段規範
│   ├── phase1-setup.md
│   ├── phase2-input.md
│   ├── phase3-draft.md
│   ├── phase4-review.md
│   ├── phase5-revise.md
│   └── phase6-render.md
├── templates/            # 輸出模板與格式規範
│   ├── one-page-format.md
│   ├── diagrams-spec.md
│   ├── glossary-format.md
│   ├── script-format.md
│   └── experiment-plan.md
├── reference/            # 技術參考文件
│   ├── svg-generation.md
│   ├── pptx-shapes.md
│   └── error-handling.md
└── scripts/              # Python 腳本
    ├── extract_pptx.py
    ├── extract_pdf.py
    └── pptx_reference.py
```

---

## 核心原則提醒

1. **國中生能懂標準**：所有內容必須讓沒有技術背景的人也能理解
2. **內容完整性**：絕對禁止刪減內容，寧可調小字體或分頁
3. **Sub Agent 審稿**：每輪審稿必須使用獨立的 Sub Agent
4. **完整輸出**：每輪重寫都要輸出完整的 Markdown 文件
5. **Citation 追溯**：所有論述都要能追溯到素材來源
