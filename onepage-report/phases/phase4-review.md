# Phase 4：主管審稿

> **執行者：subagent**
> **輸入：** `./output/phase3/`（初稿）
> **輸出：** `./output/phase4/`
> **注意：** 如需詢問用戶補充資料，可直接使用 AskUserQuestion

---

## 4.0 入口檢查

**IF `RESUME_FROM` > 4：**
1. 從 `./output/phase4/` 讀取 checkpoint（必須存在且非空）：
   - `issues.md` → Issue List
   - `verification.md` → 查證結果（如有）
   - `user_answers.md` → 使用者回答（如有）
2. **強制驗證（缺檔直接中止）**：若任一檔案不存在或為空，代表 Phase 4 中繼檔未正確產生，必須停止並回報錯誤，要求重跑/修 prompt。
3. 驗證通過後，跳過本 Phase，直接進入 Phase 5

**ELSE：**
- 正常執行下方流程


---

## 為什麼要用 Sub Agent

為什麼要用 sub agent：
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

### technical_appendix.md ⭐ 新增
{貼上完整的 technical_appendix.md 內容，如無則標註「# 無技術附錄（DETAIL_LEVEL = TECHNICAL 或無技術細節需移到附錄）」}

## 原始素材（用於素材完整性檢查）⭐ 新增

### materials.md
{貼上完整的 materials.md 內容，包含所有 Citation}

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

### ⭐ 新增：素材完整性檢查（關鍵）

10. **技術細節完整性**：materials.md 中的技術實體（執行緒名稱、函數名稱、技術表格）是否有出現在 one_page.md 或 technical_appendix.md？
11. **Citation 覆蓋率**：materials.md 的每個 Citation 是否都有被引用？
12. **附錄與主報告一致性**：one_page.md 的簡化描述與 technical_appendix.md 的完整內容是否矛盾？

## 輸出格式

請輸出 Issue List，格式如下：

### Q1：{問題標題}
- **類型**：{missing_evidence | ambiguity | inconsistency | decision_risk | undefined_term | logic_gap | pyramid_violation | script_logic_gap | not_plain_enough}
- **問題**：{具體描述問題}
- **位置**：{標題/證據/影響/行動/圖表/演講稿/glossary}
- **白話分析**（如為 not_plain_enough）：
  - 原文：「{原本的寫法}」
  - 問題：{哪裡國中生看不懂}
  - 建議改為：「{具體的白話文改寫}」
- **處理**：{material | web_research | experiment | user_input | rewrite}
- **建議**：{修正方向}

如果沒有發現問題，請明確說明「審稿通過，無需修改」。

---

## ✅ Phase4 Checkpoint（必須在 subagent 內完成）

你的輸出不只要回覆在對話中，還必須**實際寫出 checkpoint 檔案**，避免主 agent 漏寫導致 Phase4 中繼檔缺失。

### 1) 建立目錄（跨平台）

使用 Bash 工具執行（不要用 shell 的 `mkdir`/`cp`，Windows 容易失敗）：

```bash
python -c "from pathlib import Path; Path('output/phase4').mkdir(parents=True, exist_ok=True)"
```

### 2) 寫入檔案（使用 Write 工具）

- `./output/phase4/issues.md`：寫入完整 Issue List（即使審稿通過也要寫，內容為 `審稿通過，無需修改`）
- `./output/phase4/verification.md`：如無查證寫入 `# 無查證`
- `./output/phase4/user_answers.md`：如無需詢問寫入 `# 無需詢問`

### 3) 存在性驗證（必須）

用 Bash 工具執行下列檢查，確保檔案真的存在且非空：

```bash
python -c "from pathlib import Path; files=['output/phase4/issues.md','output/phase4/verification.md','output/phase4/user_answers.md'];
missing=[f for f in files if not Path(f).exists() or Path(f).stat().st_size==0];
print('missing_or_empty',missing); raise SystemExit(1 if missing else 0)"
```

"""
)
```

---

## 審稿檢查清單詳解

### 1. 結論是否過強？
- 標題的宣稱是否有足夠證據支持？
- 例：說「降低 80%」但素材只說「預估可降低」
- 修正方向：加上「預估」「初步測試顯示」「在特定條件下」

### 2. 數字是否有來源？
- 證據中的數字在素材中有明確提到嗎？
- 如果是推算的，有說明計算方式嗎？
- 修正方向：標注來源或說明計算

### 3. 條件/範圍是否明確？
- 適用於什麼場景？什麼情況下有效？
- 有什麼前提條件或限制？
- 修正方向：補充適用範圍

### 4. 行動是否缺前提或風險？
- 直接「全面採用」還是應該「先做 POC」？
- 有沒有潛在風險沒提到？
- 修正方向：加上前提條件或風險說明

### 5. 術語是否讓國中生能懂？
- 任何可能讓國中生看不懂的術語，都要加 `[[術語]]` 標記
- 標記的術語會自動連結到附錄的解釋和圖解
- 如果術語太多，考慮用白話文改寫

### 5.5 說明是否足夠詳細與白話？（國中生能懂標準）

這是最容易被忽略的問題。即使沒有專業術語，**說明本身也可能太簡略或太技術化**。

**檢查原則：**
- 想像一個國中生在讀這份報告
- 每一句話，他能理解「這是什麼意思」嗎？
- 每一個數字，他知道「這代表好還是壞」嗎？
- 每一個結論，他明白「為什麼是這樣」嗎？

**常見「不夠白話」的問題：**

| 問題類型 | 原本寫法（不好） | 修改建議（好） |
|----------|------------------|----------------|
| 太簡略 | 「減少 migration」 | 「減少程式在不同處理器核心之間的搬移次數。每次搬移都要重新載入資料，很浪費時間」 |
| 假設讀者懂 | 「L2 cache miss 率下降」 | 「處理器旁邊的高速暫存記憶體命中率提升，代表資料不用跑遠路去拿，速度變快了」 |
| 數字沒意義 | 「延遲從 16ms 降到 8ms」 | 「延遲從 16 毫秒降到 8 毫秒。人眼能感覺到的延遲大約是 10 毫秒，所以這個改善會讓玩家明顯感覺更順暢」 |
| 因果不明 | 「導入方案後效能提升」 | 「導入這個方案後，因為減少了不必要的資料搬移，處理器不用一直等資料，所以跑得更快了」 |

### 6. 關鍵術語是否有解釋？
- 報告中出現的專有名詞，讀者能理解它「是什麼」和「為何重要」嗎？
- 數字或指標有說明「代表什麼意義」嗎？
- 檢查 glossary.md 是否涵蓋所有 `[[術語]]` 標記

### 7. 邏輯鏈是否完整？（最重要）
- 從「已驗證成功要素」到「結論/行動」，每一步推論是否都有明確依據？
- 是否有「跳躍式結論」？
- 是否有「隱藏假設」？

**常見邏輯斷鏈模式：**

| 斷鏈模式 | 範例 | 修正方向 |
|----------|------|----------|
| 類比跳躍 | 「PC 上有效 → 手機也會有效」 | 補充「因為 X 機制相同」或「需 POC 驗證」 |
| 數據跳躍 | 「測試 A 改善 20% → 全面採用」 | 補充「A 場景代表性」或「需更多場景驗證」 |
| 因果混淆 | 「同時發生 → 所以是原因」 | 補充因果機制說明或降級為「相關性」 |

### 8. 金字塔結構是否成立？
- 報告中的所有內容，是否都指向標題宣稱的結論？
- 有沒有「離題內容」？
- 有沒有「重複論點」？
- 有沒有「缺漏論點」？

### 9. 演講稿邏輯是否一步接一步？
- 每一句話都承接上一句,聽眾能跟上思路
- 沒有「跳躍式敘述」
- 結論是前面所有段落的邏輯總結

### 10. 技術細節完整性（素材完整性檢查）

**目的**：確保 materials.md 中的重要技術實體沒有在報告過程中遺失。

**檢查方法**：

**步驟 1：識別 materials.md 中的「技術實體」**
- 執行緒名稱（如 InputReader, SurfaceFlinger, RenderThread）
- 函數名稱（如 notifyMotion(), scheduleTraversals(), dequeueBuffer()）
- 技術表格（如時序分析表、引擎差異對比表、效能測試表）
- 系統架構中的模組名稱（如 BufferQueue, HWComposer）
- 程式碼片段或 API 呼叫序列

**步驟 2：檢查這些技術實體是否出現在以下任一位置**
- ✓ one_page.md（主報告）
- ✓ technical_appendix.md（技術附錄）
- ✓ diagrams.md（圖表節點或標籤）

**步驟 3：標記「完全遺失」的技術實體**
- 如果某個技術實體在 materials.md 中佔有重要篇幅（例如完整的執行緒列表、詳細的函數呼叫鏈），但在上述三個位置都找不到，則標註為 Issue。

**Issue 範例**：
```markdown
### Q10：Android 完整流程的執行緒名稱遺失

- **類型**：missing_technical_detail
- **問題**：materials.md [C6] 提到完整的執行緒列表（InputReader → InputDispatcher → ViewRootImpl → RenderThread），但在 one_page.md、technical_appendix.md、diagrams.md 中都沒有出現
- **位置**：技術附錄
- **影響**：技術同仁無法理解完整的系統流程，無法據此進行實作或除錯
- **處理**：material
- **建議**：在 technical_appendix.md 新增「Android Touch2Photon 完整流程」章節，列出執行緒列表和函數呼叫鏈，保留 Citation [C6]
```

**判斷原則**：
- **需標註 Issue**：重要技術細節（如核心流程的執行緒、關鍵函數、技術總結表）完全遺失
- **不需標註**：次要細節（如某個執行緒的優先級數值）或已在圖表中以視覺方式呈現

### 11. Citation 覆蓋率

**目的**：確保 materials.md 中的每個 Citation (C1, C2, C3...) 都有被使用，避免重要資訊遺漏。

**檢查方法**：

**步驟 1：列出所有 Citation ID**
- 從 materials.md 中抽取所有 Citation ID（例如 [C1], [C2], ... [C12]）

**步驟 2：檢查每個 Citation 是否被引用**
- 在 one_page.md、technical_appendix.md、diagrams.md、script.md、glossary.md 中搜尋每個 Citation ID

**步驟 3：標記未使用的 Citation**
- 如果某個 Citation 在所有輸出檔案中都沒有出現，標註為 Issue

**Issue 範例**：
```markdown
### Q11：Citation C11, C12 未使用

- **類型**：unused_citation
- **問題**：materials.md [C11][C12] 包含「Unity vs Unreal 引擎差異分析」的重要資訊，但在所有輸出檔案中都沒有引用
- **位置**：技術附錄
- **影響**：遺漏了不同引擎導致延遲差異的關鍵分析，可能誤導 POC 設計
- **處理**：material
- **建議**：在 technical_appendix.md 新增「引擎差異分析」章節，說明 Unity Double Buffering 與 Unreal Pipelined 的延遲特性差異
```

**判斷原則**：
- **需標註 Issue**：Citation 包含核心證據、技術分析、或與結論相關的資訊
- **不需標註**：Citation 為補充性質（如歷史背景、相關但非核心的資訊）且確實不影響報告完整性

### 12. 附錄與主報告一致性

**目的**：確保 one_page.md 的簡化描述與 technical_appendix.md 的完整內容不矛盾。

**檢查項目**：

1. **數字一致性**：主報告提到的數字（改善百分比、延遲時間）與附錄的詳細數據是否一致？
2. **結論一致性**：主報告的結論是否與附錄的詳細分析支持？
3. **適用範圍一致性**：主報告說「適用於所有場景」，但附錄說「僅在特定條件下有效」？

**Issue 範例**：
```markdown
### Q12：主報告與附錄的改善數字不一致

- **類型**：inconsistency
- **問題**：one_page.md 說「Touch2Photon 降低 81%」，但 technical_appendix.md 的詳細表格顯示「Unity 降低 81%，Unreal 降低 45%」
- **位置**：證據區塊
- **影響**：主報告過度簡化導致誤導，讓人以為所有引擎都有 81% 改善
- **處理**：rewrite
- **建議**：主報告改為「Touch2Photon 降低 45-81%（視引擎而定）」，並註明「詳見技術附錄」
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
| `missing_technical_detail` | 技術細節遺失（執行緒、函數、表格） | material（從 materials.md 恢復到 technical_appendix.md）|
| `unused_citation` | Citation 未使用（重要資訊遺漏） | material（補充到 technical_appendix.md 或 one_page.md）|

---

## Issue List 輸出格式

```markdown
## 審稿結果

我以主管角度審視了初稿，發現以下需要確認的問題：

### Q1：{問題標題}
- **類型**：{類型}
- **問題**：{具體描述問題}
- **位置**：{標題/證據/影響/行動/圖表/演講稿/glossary}
- **斷鏈分析**（如為 logic_gap 或 script_logic_gap）：
  - 推論鏈：{A} → {B} → {C}
  - 斷鏈處：{B} → {C}
  - 缺失：{缺少什麼才能連上}
- **白話分析**（如為 not_plain_enough）：
  - 原文：「{原本的寫法}」
  - 問題：{哪裡國中生看不懂}
  - 建議改為：「{具體的白話文改寫}」
- **素材完整性分析**（如為 missing_technical_detail）：
  - 遺失內容：{哪些技術實體（執行緒/函數/表格）遺失}
  - 原始位置：materials.md [{Citation ID}]
  - 影響：{技術同仁無法理解什麼}
  - 恢復位置：{one_page.md | technical_appendix.md | diagrams.md}
- **Citation 分析**（如為 unused_citation）：
  - 未使用的 Citation：[{Citation ID list}]
  - 內容摘要：{這些 Citation 包含什麼資訊}
  - 重要性：{為何這些資訊不應遺漏}
- **處理**：{material | web_research | experiment | user_input | rewrite}
- **建議**：{修正方向}

### Q2：...
```

---

## 處理方式分類

| 處理方式 | 說明 | 動作 |
|----------|------|------|
| material | 素材內可回答 | 直接引用素材修正 |
| web_research | 需網路查證 | 進入 Phase 4.5 |
| experiment | 需實驗佐證 | 產出 Experiment Plan |
| user_input | 需使用者補充 | 詢問使用者 |

如果有 `web_research` 類型的 Issue，先進入 Phase 4.5。

---

## Phase 4.5：網路查證（如需要）

**觸發條件**：`REVIEW_WEB_SEARCH = true` 且有 `web_research` 類型的 Issue

若 `REVIEW_WEB_SEARCH = false`，跳過此步驟，將 `web_research` 類型的 Issue 改為 `user_input` 處理。

---

當有 Issue 需要網路查證時執行此步驟。

### 查證流程

1. 使用 WebSearch 工具搜尋相關資訊
2. 使用 WebFetch 抓取 2-3 個可信來源的內容
3. 整理查證結果

### 查證結果格式

```markdown
## 網路查證結果

### {Issue Q1 關鍵字}

#### 來源 1：{source_title}
- **網址**：{url}
- **摘要**：{重點摘要}

#### 來源 2：{source_title}
- **網址**：{url}
- **摘要**：{重點摘要}

#### 結論
- **可信度**：support | conflict | unclear
- **說明**：{一致/衝突點說明}
- **建議處理**：{如何修正內容}
```

### 查證結果使用規則

| 可信度 | 處理方式 |
|--------|----------|
| support | 可用於加強證據說明，但仍標注「業界資料顯示」 |
| conflict | 弱化結論，加註「有不同看法」或「仍需驗證」 |
| unclear | 保守處理，建議「先做 POC」驗證 |

**重要**：網路查證結果不能直接當作新證據，只能用於弱化/加條件、建議使用者補充、調整行動建議。

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

### Q2：...
```

等待使用者回答後，進入 Phase 5。

---

## 4.8 Checkpoint 寫入

Phase 4 完成後，將所有輸出儲存到 checkpoint：

1. 建立目錄（跨平台）：

   ```bash
   python -c "from pathlib import Path; Path('output/phase4').mkdir(parents=True, exist_ok=True)"
   ```

2. 使用 Write 工具寫入以下檔案（即使內容為「無」也要寫出檔案）：


**./output/phase4/issues.md**
```markdown
# Issue List

{Sub Agent 產生的 Issue List}
```

**./output/phase4/verification.md**
```markdown
# 網路查證結果

{Phase 4.5 的查證結果，如無則寫入「# 無查證」}
```

**./output/phase4/user_answers.md**
```markdown
# 使用者回答

{Phase 4.7 的使用者回答，如無則寫入「# 無需詢問」}
```

---

## 4.8.1 Checkpoint 驗證（強制；失敗即中止）

完成 Write 後，必須用 Bash 工具驗證檔案存在且非空：

```bash
python -c "from pathlib import Path; files=['output/phase4/issues.md','output/phase4/verification.md','output/phase4/user_answers.md']; missing=[f for f in files if not Path(f).exists() or Path(f).stat().st_size==0]; print('missing_or_empty',missing); raise SystemExit(1 if missing else 0)"
```

若驗證失敗，代表 checkpoint 未落盤或寫入失敗，必須停止流程並修正。


### 多輪迭代時的版本保留

當迭代輪次 > 1 時，同時複製到 iterations 目錄：

```bash
python -c "from pathlib import Path; import shutil; n='{N}'; dst=Path(f'output/iterations/iter{n}/phase4'); dst.mkdir(parents=True, exist_ok=True);
for name in ['issues.md','verification.md','user_answers.md']:
    shutil.copy2(Path('output/phase4')/name, dst/name)"
```

