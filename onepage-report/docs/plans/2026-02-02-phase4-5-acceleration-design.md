# Phase 4-5 加速設計

> 目標：讓 Phase 4-5 執行時間 < 30 秒

## 問題分析

原本的瓶頸：
- Phase 4 審稿要讀取 5+ 個文件
- Phase 5 要輸出 6 個完整文件（即使沒修改）
- 審稿檢查項目 11 項過多
- citation_map.md 不必要

## 設計方案

### 1. 精簡審稿範圍

**Phase 4 只審 3 個文件：**
- `one_page.md`
- `diagrams.md`
- `table.md`

**bypass 到 Phase 6（不進審稿迴圈）：**
- `script.md`
- `glossary.md`

**移除：**
- `citation_map.md`

### 2. 精簡審稿檢查項目

**保留 7 項：**
1. 結論是否過強？（有沒有證據支持）
2. 條件/範圍是否明確？
3. 行動是否缺前提或風險？
4. 術語是否讓國中生能懂？
5. 說明是否足夠詳細與白話？
6. 邏輯鏈是否完整？
7. 金字塔結構是否成立？

**移除 4 項：**
- ~~數字是否有來源~~
- ~~演講稿邏輯~~
- ~~技術細節完整性~~
- ~~Citation 覆蓋率~~

### 3. Issue 類型修改

**移除：**
- `missing_technical_detail`
- `unused_citation`
- `script_logic_gap` → 改名為 `one_page_logic_gap`

### 4. 迭代設定

- 預設 `MAX_ITERATIONS = 1`（一輪審稿）
- 進階使用者可選多輪

### 5. 新架構流程圖

```
Phase 3 輸出：
├── one_page.md  ──┐
├── diagrams.md  ──┼── 進入 Phase 4-5 審稿
├── table.md     ──┘
├── script.md    ────── bypass → Phase 6
└── glossary.md  ────── bypass → Phase 6

Phase 4：讀 3 個文件，7 項檢查 → issues.md
Phase 5：修正 3 個文件 → one_page.md, diagrams.md, table.md

Phase 6 接收：
├── one_page.md   （來自 Phase 5）
├── diagrams.md   （來自 Phase 5）
├── table.md      （來自 Phase 5）
├── script.md     （來自 Phase 3）
└── glossary.md   （來自 Phase 3）
```

## 預估效果

| 項目 | 原本 | 優化後 | 減少 |
|------|------|--------|------|
| Phase 4 讀取文件 | 5+ | 3 | -40% |
| Phase 5 輸出文件 | 6 | 3 | -50% |
| 審稿檢查項目 | 11 | 7 | -36% |
| 讀取資料量 | ~26KB | ~13KB | -50% |

## 需要修改的文件

1. `phases/phase4-review.md` - 精簡審稿範圍和檢查項目
2. `phases/phase5-revise.md` - 精簡輸出文件、更新流程
3. `phases/appendix/phase4-checklist-detail.md` - 移除不需要的檢查細節
4. 可能需要修改 Phase 6 來接收 bypass 文件
