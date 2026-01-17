---
name: onepage-report
description: 從素材資料夾產生一頁投影片 + 演講稿
arguments: [input_path]
---

# 一頁投影片產生器

> 版本：v2.8（支援從中間繼續）

將素材（資料夾/PPTX/URL）轉換成專業的一頁投影片與演講稿。

**新功能：支援從中間 Phase 繼續執行**
- 每個 Phase 完成後會自動儲存 checkpoint 到 `./output/phase{N}/`
- 出錯或中斷後可以從任意 Phase 繼續，不需從頭開始
- 使用者可以手動修改 checkpoint 檔案，然後繼續執行

---

## 執行流程概述

本技能按以下順序執行，每個階段的詳細規範請讀取對應檔案：

| Phase | 說明 | 規範檔案 |
|-------|------|----------|
| 1 | 設定詢問 | `{skill_dir}/phases/phase1-setup.md` |
| 2 | 讀取素材 | `{skill_dir}/phases/phase2-input.md` |
| 3 | 產生初稿 | `{skill_dir}/phases/phase3-draft.md` |
| 4 | 主管審稿 | `{skill_dir}/phases/phase4-review.md` |
| 5 | 重寫迭代 | `{skill_dir}/phases/phase5-revise.md` |
| 6 | 渲染輸出 | `{skill_dir}/phases/phase6-render.md` |

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

## Phase 1：設定詢問

**執行前請讀取：** `Read {skill_dir}/phases/phase1-setup.md`

使用 AskUserQuestion 工具詢問使用者設定，記錄到全域變數。

---

## Phase 2：讀取素材

**執行前請讀取：** `Read {skill_dir}/phases/phase2-input.md`

根據 `{input_path}` 判斷輸入類型並處理：
- 資料夾：掃描 .txt/.md/.pptx/.pdf 檔案
- PPTX 檔案：使用 extract_pptx.py 抽取
- PDF 檔案：使用 extract_pdf.py 抽取
- URL：使用 WebFetch 抓取

完成後建立 Citation Map 和術語清單。

---

## Phase 3：產生初稿

**執行前請讀取：**
**必須使用 Task tool 調用 Sub Agent 產生初稿**

1. `Read {skill_dir}/phases/phase3-draft.md` - 初稿生成流程
2. `Read {skill_dir}/templates/one-page-format.md` - 報告格式
3. `Read {skill_dir}/templates/diagrams-spec.md` - 圖表規範
4. `Read {skill_dir}/templates/glossary-format.md` - 術語格式
5. `Read {skill_dir}/templates/script-format.md` - 演講稿格式

產生以下文件：
- `one_page.md`：主報告內容
- `diagrams.md`：圖表規格
- `table.md`：數據比較表（如有）
- `glossary.md`：術語詞彙表
- `script.md`：演講稿

---

## Phase 4：主管審稿

**執行前請讀取：** `Read {skill_dir}/phases/phase4-review.md`
**必須使用 Task tool 調用 Sub Agent 執行審查**，產出 Issue List。

如有 Issue 需要網路查證，進入 Phase 4.5。
如有 Issue 需要實驗佐證，讀取 `{skill_dir}/templates/experiment-plan.md` 產出實驗計畫。
如有 Issue 需要使用者補充，進入 Phase 4.7 詢問使用者。

---

## Phase 5：根據回饋重寫

**執行前請讀取：** `Read {skill_dir}/phases/phase5-revise.md`

根據使用者對 Issue List 的回答修正初稿。

**重要：每輪都必須輸出完整的 Markdown 文件**

### 多輪迭代

當 `MAX_ITERATIONS > 1` 時，重複 Phase 4 → Phase 5：

```
WHILE 迭代計數 <= MAX_ITERATIONS:
    【必須用 Task tool 呼叫 sub agent】執行 Phase 4
    IF 審稿通過: BREAK
    IF 達到上限: 強制保守輸出, BREAK
    執行 Phase 5
```

---

## Phase 6：渲染輸出

**執行前請讀取：** `Read {skill_dir}/phases/phase6-render.md`

根據 `DIAGRAM_METHOD` 決定圖表產生方式：

| DIAGRAM_METHOD | 額外讀取 |
|----------------|----------|
| `svg_png` | `Read {skill_dir}/reference/svg-generation.md` |
| `pptx_shapes` | `Read {skill_dir}/reference/pptx-shapes.md` |

**步驟：**
1. 建立輸出目錄 `./output`
2. 產生圖表（SVG/PNG 或 PPTX Shapes）
3. **使用 Sub Agent 驗證內容完整性**
4. 產生 PPTX（含附錄投影片）
5. 執行排版審查（如 `LAYOUT_REVIEW_ROUNDS > 0`）
6. 輸出演講稿和其他檔案

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
