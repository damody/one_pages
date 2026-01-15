# 一頁投影片產生器 (One-Page Report Generator)

> 版本：v2.8
> 作者：Claude Code Skill
> 最後更新：2026-01-15

## 專案簡介

這是一個基於 Claude Code 的智能技能（Skill），可以將各種素材（資料夾、PPTX、PDF、URL）自動轉換成專業的**一頁投影片**與**演講稿**。

本工具支援從素材收集、內容生成、主管審稿、到最終 PowerPoint 輸出的完整工作流程。

### 主要特色

✨ **智能內容生成**
- 自動從素材中提取關鍵資訊
- 產生符合目標聽眾（Executive/Manager/Technical）的內容
- 支援多種報告模板（Executive、Technical、POC Report）

🔍 **多輪審稿機制**
- 模擬主管視角檢查內容品質
- 自動識別結論過強、缺少佐證等問題
- 支援網路查證與實驗計畫產出

📊 **專業排版輸出**
- 自動產生 PowerPoint 投影片（.pptx）
- 支援圖表自動繪製（SVG/PNG 或 PPTX Shapes）
- 含附錄投影片、術語詞彙表、來源引用

🔄 **斷點續傳機制**
- 每個階段自動儲存 checkpoint
- 支援從任意 Phase 繼續執行
- 可手動修改 checkpoint 檔案後繼續

---

## 安裝需求

### 必要環境

- **Claude Code CLI** (最新版本)
- **Python 3.8+**
- **Node.js 16+** (用於 Mermaid 圖表渲染)

### Python 套件

```bash
pip install python-pptx pillow pypdf pymupdf
```

### Node.js 套件（可選，用於圖表渲染）

```bash
npm install -g @mermaid-js/mermaid-cli
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

系統會依序詢問以下設定：

1. **目標聽眾**：L1 Executive / L2 Manager+Tech / L3 Technical
2. **報告目的**：例如「核准 POC」、「申請加人」、「採用方案 A」
3. **佐證強度**：E0（無需實驗）/ E1（輕佐證）/ E2（強佐證）
4. **報告模板**：Executive / Technical / POC Report
5. **審稿輪數**：1-5 輪（預設 5 輪）

完成設定後，系統會自動：
- 讀取素材並建立引用地圖
- 產生初稿（投影片內容、圖表、演講稿）
- 進行多輪審稿與修正
- 輸出最終 PowerPoint 檔案

---

## 執行流程概述

| Phase | 階段名稱 | 說明 |
|-------|---------|------|
| **Phase 1** | 設定詢問 | 詢問使用者設定（聽眾、目的、佐證強度等） |
| **Phase 2** | 讀取素材 | 從資料夾/PPTX/PDF/URL 讀取內容，建立引用地圖 |
| **Phase 3** | 產生初稿 | 生成投影片內容、圖表規格、術語表、演講稿 |
| **Phase 4** | 主管審稿 | 模擬主管視角檢查內容，產出問題清單 |
| **Phase 5** | 重寫迭代 | 根據審稿意見修正內容，支援多輪迭代 |
| **Phase 6** | 渲染輸出 | 產生 PowerPoint、圖表、演講稿等最終檔案 |

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
│   └── citation_map.md
├── iterations/                  # 多輪迭代版本保留
│   ├── iter1/phase4/, phase5/
│   └── iter2/phase4/, phase5/
├── one_page.pptx                # ⭐ 最終輸出：主投影片
├── speaker_script.md            # ⭐ 演講稿
├── main_diagram.svg/png         # 主圖（如用 svg_png）
├── appendix_diagram_*.svg/png   # 附錄圖
├── citation_map.md              # 來源對照表
├── glossary.md                  # 術語詞彙表
└── render_this.py               # 產生 PPTX 的腳本
```

---

## 專案結構

```
onepage-report/
├── SKILL.md                     # 主要技能規範（入口點）
├── phases/                      # 各階段執行規範
│   ├── phase1-setup.md
│   ├── phase2-input.md
│   ├── phase3-draft.md
│   ├── phase4-review.md
│   ├── phase5-revise.md
│   └── phase6-render.md
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
│   ├── antilag2.md
│   ├── cache_aware.md
│   ├── lavd.md
│   ├── workload_prediction.md
│   └── latency_meter.md
└── scripts/                     # Python 輔助腳本
    ├── extract_pptx.py          # PPTX 內容抽取
    ├── extract_pdf.py           # PDF 內容抽取
    ├── pptx_reference.py        # python-pptx API 參考
    └── requirements.txt
```

---

## 核心設計原則

### 1. 國中生能懂標準
所有內容必須讓沒有技術背景的人也能理解（依目標聽眾調整）。

### 2. 內容完整性
絕對禁止刪減內容，寧可調小字體或分頁。

### 3. Sub Agent 審稿
每輪審稿必須使用獨立的 Sub Agent，確保客觀性。

### 4. 完整輸出
每輪重寫都要輸出完整的 Markdown 文件，不可省略任何區塊。

### 5. Citation 追溯
所有論述都要能追溯到素材來源，標註 [C1]、[C2] 等引用編號。

---

## 全域變數設定

| 變數 | 說明 | 預設值 |
|------|------|--------|
| `PURPOSE` | 報告目的 | - |
| `EVIDENCE` | 佐證強度 | E0 |
| `MAX_ITERATIONS` | 審稿輪數 | 5 |
| `DIAGRAM_METHOD` | 繪圖方式 | pptx_shapes |
| `LAYOUT_REVIEW_ROUNDS` | 排版審查輪數 | 2 |
| `RESUME_FROM` | 從哪個 Phase 繼續（1-6） | 1 |

---

## 報告模板類型

### Executive 模板（簡潔版）
- **區塊**：標題 + 關鍵要點（3點）+ 預期效益 + 行動
- **特色**：大字、少文字、重點突出
- **適用**：高層主管、快速決策

### Technical 模板（技術版）
- **區塊**：標題 + 背景/問題 + 技術方案 + 證據/數據 + 影響 + 行動
- **特色**：資訊密集、多區塊、詳細說明
- **適用**：技術審查、架構討論

### POC Report 模板（POC 報告）
- **區塊**：標題 + 已驗證成功要素 + 現況問題 + 技術關鍵點 + 對照表 + POC 設計 + 成功判定準則 + 行動
- **特色**：完整邏輯鏈、實驗設計、判定標準
- **適用**：POC 申請、技術驗證

---

## 使用範例

### 範例 1：從資料夾產生 POC 報告

```bash
/onepage-report ./framepacing-notes
```

選擇設定：
- 聽眾：L2 Manager+Tech
- 目的：核准 POC
- 佐證：E1（需要 1-2 個關鍵指標）
- 模板：POC Report
- 審稿輪數：3 輪

輸出：
- `./output/one_page.pptx` - 包含完整邏輯鏈的 POC 報告
- `./output/speaker_script.md` - 5 分鐘演講稿
- `./output/citation_map.md` - 所有數據的來源引用

### 範例 2：從 PPTX 產生高層簡報

```bash
/onepage-report ./technical-presentation.pptx
```

選擇設定：
- 聽眾：L1 Executive
- 目的：核准預算
- 佐證：E0（使用現有數據）
- 模板：Executive
- 審稿輪數：5 輪

輸出：
- 精簡的一頁投影片，只保留決策所需資訊
- 3 個關鍵要點 + 量化效益 + 明確行動建議

---

## 版本歷史

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

### 1. 模組化架構
採用 Phase-based 設計，每個階段職責單一、可獨立執行。

### 2. Sub Agent 審稿
使用 Task tool 調用獨立的 Sub Agent 進行審稿，避免主 Agent 的確認偏誤。

### 3. Checkpoint 機制
每個 Phase 完成後自動儲存狀態，支援中斷後繼續執行或手動調整。

### 4. 智能佈局決策
根據內容量動態調整投影片佈局，不使用固定模板。

### 5. 完整性驗證
Phase 6 使用 Sub Agent 驗證內容完整性，確保沒有遺漏關鍵資訊。

---

## 錯誤處理

詳細的錯誤處理規範請參閱：[reference/error-handling.md](onepage-report/reference/error-handling.md)

常見問題：
- **Mermaid 渲染失敗**：檢查 `@mermaid-js/mermaid-cli` 是否安裝
- **PPTX 產生失敗**：檢查 `python-pptx` 套件版本
- **素材抽取失敗**：確認檔案路徑正確且有讀取權限

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

- **新增模板**：在 `templates/` 目錄新增新的報告格式
- **改進審稿邏輯**：修改 `phases/phase4-review.md`
- **新增圖表類型**：擴充 `templates/diagrams-spec.md`
- **優化排版算法**：改進 `reference/pptx-shapes.md`

---

## 授權

本專案由 Claude Code 驅動，僅供學習與研究使用。

---

## 聯絡與支援

- **GitHub Issues**：回報問題或建議新功能
- **技術文件**：詳見 `onepage-report/SKILL.md`
- **範例參考**：`onepage-report/reference/` 目錄

---

## 致謝

感謝 Claude Code 團隊提供強大的 AI 輔助開發平台，讓複雜的文件產生工作變得簡單高效。

---

**立即開始使用** 👉 `/onepage-report ./your-materials`
