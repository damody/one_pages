# 一頁投影片產生器 (One-Page Report Generator)

> 版本：v3.0（Subagent 架構）
> 作者：Claude Code Skill
> 最後更新：2026-01-17

## 專案簡介

這是一個基於 Claude Code 的智能技能（Skill），可以將各種素材（資料夾、PPTX、PDF、URL）自動轉換成專業的**一頁投影片**與**演講稿**。

本工具支援從素材收集、內容生成、主管審稿、到最終 PowerPoint 輸出的完整工作流程。

### 主要特色

✨ **Subagent 架構（v3.0 新功能）**
- 主 agent 只負責調控，Phase 2-6 全由 subagent 執行
- 每個 Phase 透過 checkpoint 傳遞資料，互不干擾
- 支援平行處理，提升執行效率

🔍 **多輪審稿機制**
- 模擬主管視角檢查內容品質
- 自動識別結論過強、缺少佐證等問題
- 支援網路查證與實驗計畫產出
- Subagent 可直接詢問用戶補充資料

📊 **專業排版輸出**
- 自動產生 PowerPoint 投影片（.pptx）
- 支援圖表自動繪製（SVG/PNG 或 PPTX Shapes）
- **顏色對比度檢查**：確保文字清晰可讀
- 含附錄投影片、術語詞彙表、來源引用

🔄 **斷點續傳機制**
- 每個階段自動儲存 checkpoint
- 支援從任意 Phase 繼續執行
- 可手動修改 checkpoint 檔案後繼續

---

## 架構概述

### Subagent 執行模式（v3.0）

```
┌─────────────────────────────────────────────────────────┐
│                     主 Agent（調控者）                    │
│  - 讀取 SKILL.md                                        │
│  - 執行 Phase 1（設定詢問）                              │
│  - 依序呼叫 Phase 2-6 的 subagent                        │
└─────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│ Phase 2       │     │ Phase 3       │     │ Phase 4       │
│ Subagent      │ ──▶ │ Subagent      │ ──▶ │ Subagent      │
│ 讀取素材       │     │ 產生初稿       │     │ 主管審稿       │
└───────────────┘     └───────────────┘     └───────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
  phase2/               phase3/               phase4/
  checkpoint            checkpoint            checkpoint
```

### 資料流

```
主 agent 執行 Phase 1 → output/phase1/config.md
                              ↓
Phase 2 subagent → output/phase2/materials.md, citation_map.md, terms.md
                              ↓
Phase 3 subagent → output/phase3/one_page.md, diagrams.md, ...
                              ↓
Phase 4 subagent → output/phase4/issues.md（可直接詢問用戶）
                              ↓
Phase 5 subagent → output/phase5/one_page.md, ...
                              ↓
Phase 6 subagent → output/one_page.pptx
```

---

## 安裝需求

### 必要環境

- **Claude Code CLI** (最新版本)
- **Python 3.8+**

### Python 套件

```bash
pip install python-pptx pillow pypdf pymupdf
```

---

## 快速開始

### 基本使用

在 Claude Code CLI 中執行：

```bash
/onepage-report ./your-materials-folder
```

或指定單一檔案：

```bash
/onepage-report ./presentation.pptx
/onepage-report ./document.pdf
/onepage-report https://example.com/article
```

### 執行流程

系統會詢問以下設定：

**Phase 1 設定詢問（共 7 題，分兩次詢問）：**

第一次詢問：
1. **佐證強度**：E0（使用現有數據）/ E1（輕佐證）/ E2（強佐證）
2. **網路查證**：關閉（預設）/ 啟用
3. **審稿次數**：5 / 3 / 1 輪
4. **排版審查次數**：2 / 1 / 0 輪

第二次詢問：
5. **Citation 網路補充**：是 / 否
6. **繪圖方法**：pptx（PPTX Shapes）/ svg（圖表更精細）
7. **技術細節程度**：完整版（預設）/ 自定

完成設定後，系統會自動：
- 讀取素材並建立引用地圖（Phase 2 subagent）
- 產生初稿（Phase 3 subagent）
- 進行多輪審稿與修正（Phase 4-5 subagent）
- 輸出最終 PowerPoint 檔案（Phase 6 subagent）

---

## 執行流程概述

| Phase | 階段名稱 | 執行者 | 輸入 | 輸出 |
|-------|---------|--------|------|------|
| **1** | 設定詢問 | **主 agent** | 用戶輸入 | `phase1/config.md` |
| **2** | 讀取素材 | subagent | phase1 + 素材路徑 | `phase2/materials.md`, `citation_map.md`, `terms.md` |
| **3** | 產生初稿 | subagent | phase2 | `phase3/one_page.md`, `diagrams.md`, `glossary.md`, `script.md` |
| **4** | 主管審稿 | subagent | phase3 | `phase4/issues.md`, `user_answers.md` |
| **5** | 重寫迭代 | subagent | phase3 + phase4 | `phase5/one_page.md`, ... |
| **6** | 渲染輸出 | subagent | phase5 | `final.pptx`, `script.txt` |

每個 Phase 完成後會自動儲存 checkpoint 到 `./output/phase{N}/`，支援中斷後繼續執行。

---

## 輸出檔案結構

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
│   ├── citation_map.md
│   └── technical_appendix.md
├── iterations/                  # 多輪迭代版本保留
│   ├── iter1/phase4/, phase5/
│   └── iter2/phase4/, phase5/
├── final.pptx                   # ⭐ 最終輸出：主投影片
├── script.txt                   # ⭐ 演講稿
├── diagrams.md                  # 圖表規格
├── render_this.py               # 產生 PPTX 的腳本
├── citation_map.md              # 來源對照表
└── glossary.md                  # 術語詞彙表
```

---

## 專案結構

```
onepage-report/
├── SKILL.md                     # 主要技能規範（入口點）v3.0
├── phases/                      # 各階段執行規範
│   ├── phase1-setup.md          # 主 agent 執行
│   ├── phase2-input.md          # subagent 執行
│   ├── phase3-draft.md          # subagent 執行
│   ├── phase4-review.md         # subagent 執行
│   ├── phase5-revise.md         # subagent 執行
│   └── phase6-render.md         # subagent 執行
├── templates/                   # 輸出模板與格式規範
│   ├── one-page-format.md
│   ├── diagrams-spec.md
│   ├── glossary-format.md
│   ├── script-format.md
│   └── experiment-plan.md
├── reference/                   # 技術參考文件
│   ├── svg-generation.md
│   ├── pptx-shapes.md
│   ├── error-handling.md
│   └── render_example.py        # 完整繪圖函數範例
└── scripts/                     # Python 輔助腳本
    ├── extract_pptx.py          # PPTX 內容抽取
    ├── extract_pdf.py           # PDF 內容抽取
    └── pptx_reference.py        # python-pptx API 參考
```

---

## 核心設計原則

### 1. 國中生能懂標準
所有內容必須讓沒有技術背景的人也能理解。

### 2. 內容完整性
絕對禁止刪減內容，寧可調小字體或分頁。

### 3. Subagent 執行
Phase 2-6 全由獨立 subagent 執行，確保 context 不會爆掉。

### 4. 完整輸出
每輪重寫都要輸出完整的 Markdown 文件，不可省略任何區塊。

### 5. Citation 追溯
所有論述都要能追溯到素材來源，標註 [C1]、[C2] 等引用編號。

### 6. 顏色對比度
確保文字顏色與背景顏色有足夠對比，避免白底白字。

---

## 全域變數設定

| 變數 | 說明 | 預設值 |
|------|------|--------|
| `PURPOSE` | 報告目的 | - |
| `EVIDENCE` | 佐證強度 | E0 |
| `DETAIL_LEVEL` | 技術細節保留程度 | FULL_DETAIL |
| `MAX_ITERATIONS` | 審稿輪數 | 5 |
| `DIAGRAM_METHOD` | 繪圖方式 | pptx_shapes |
| `LAYOUT_REVIEW_ROUNDS` | 排版審查輪數 | 2 |
| `REVIEW_WEB_SEARCH` | 審稿時是否啟用網路查證 | false |
| `CITATION_WEB_SEARCH` | Citation Map 是否啟用網路補充 | false |
| `RESUME_FROM` | 從哪個 Phase 繼續（1-6） | 1 |

---

## 排版審查功能

Phase 6 會執行排版審查，檢查項目包括：

| 檢查項目 | 說明 |
|---------|------|
| 圖表完整性 | diagrams.md 的每個圖表都有對應的 draw_* 呼叫 |
| 內部流程節點 | 所有描述的節點都有繪製 |
| 箭頭標籤 | 所有描述的箭頭標籤都有繪製 |
| 技術附錄章節 | 每個章節都有對應投影片 |
| **顏色對比度** | 文字與背景有足夠對比（淺背景用深字，深背景用白字）|

### 顏色對比度規則

| 背景類型 | 文字顏色 |
|---------|---------|
| 淺色背景（RGB > 200）| 深色字（#333333）|
| 深色背景（RGB < 100）| 白色字（#FFFFFF）|
| 彩色背景 | 白色字或對比色 |

---

## 使用範例

### 範例 1：從資料夾產生報告

```bash
/onepage-report ./framepacing-notes
```

選擇設定：
- 佐證：E0（使用現有數據）
- 審稿輪數：3 輪
- 技術細節：完整版

輸出：
- `./output/final.pptx` - 完整的一頁報告
- `./output/script.txt` - 演講稿
- `./output/citation_map.md` - 所有數據的來源引用

### 範例 2：從 PPTX 產生簡報

```bash
/onepage-report ./technical-presentation.pptx
```

系統會先列出投影片清單，讓你選擇要抽取的範圍。

---

## 版本歷史

### v3.0（2026-01-17）
- ✅ **Subagent 架構重構**：Phase 2-6 全由 subagent 執行
- ✅ **主 agent 只負責調控**：透過 checkpoint 傳遞資料
- ✅ **簡化設定選項**：技術細節程度改為「完整版/自定」
- ✅ **新增顏色對比度檢查**：避免白底白字問題
- ✅ 移除過時的「進階設定解析」區塊
- ✅ 各 Phase 檔案加入執行者、輸入、輸出說明

### v2.8（2026-01-15）
- ✅ 支援從中間 Phase 繼續執行（斷點續傳）
- ✅ 新增排版審查功能（Layout Review）
- ✅ 強化 Phase 6 render_this.py 產生流程
- ✅ 新增網路搜尋開關設定

### v2.2（先前版本）
- 重構：拆分 SKILL.md 為模組化結構
- 新增多輪審稿迭代機制
- 支援實驗計畫產出（E1/E2）
- 強化 Citation Map 追溯功能

---

## 技術特色

### 1. Subagent 架構
主 agent 只負責調控，Phase 2-6 由獨立 subagent 執行，避免 context 爆掉。

### 2. Checkpoint 機制
每個 Phase 完成後自動儲存狀態，支援中斷後繼續執行或手動調整。

### 3. 智能佈局決策
根據內容量動態調整投影片佈局：
- 節點數量 > 6 自動切換縱向排列
- 文字過長自動換行或縮小字體

### 4. 顏色對比度檢查
自動判斷背景亮度，選擇適當的文字顏色：
```python
brightness = (R * 299 + G * 587 + B * 114) / 1000
text_color = "#333333" if brightness > 180 else "#FFFFFF"
```

### 5. 完整性驗證
Phase 6 使用 Sub Agent 驗證內容完整性，確保沒有遺漏關鍵資訊。

---

## 錯誤處理

詳細的錯誤處理規範請參閱：[reference/error-handling.md](onepage-report/reference/error-handling.md)

常見問題：
- **PPTX 產生失敗**：檢查 `python-pptx` 套件版本
- **素材抽取失敗**：確認檔案路徑正確且有讀取權限
- **PermissionError**：關閉 PowerPoint 後重試

---

## 適用場景

✅ **技術 POC 申請**
自動產生完整邏輯鏈：業界驗證 → 現況問題 → 為何可行 → 實驗設計 → 判定準則

✅ **高層決策報告**
精簡版本，只保留決策所需的關鍵資訊與量化效益

✅ **技術審查簡報**
資訊密集版本，包含背景、方案、證據、影響、行動

✅ **預算申請提案**
含成本效益分析、風險評估、明確的投資回報

---

## 貢獻指南

本專案採用模組化設計，歡迎貢獻：

- **改進審稿邏輯**：修改 `phases/phase4-review.md`
- **新增圖表類型**：擴充 `templates/diagrams-spec.md`
- **優化排版算法**：改進 `reference/pptx-shapes.md`
- **新增繪圖函數**：擴充 `reference/render_example.py`

---

## 授權

本專案由 Claude Code 驅動，僅供學習與研究使用。

---

## 聯絡與支援

- **技術文件**：詳見 `onepage-report/SKILL.md`
- **範例參考**：`onepage-report/reference/` 目錄

---

**立即開始使用** 👉 `/onepage-report ./your-materials`
