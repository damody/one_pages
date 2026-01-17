# Phase 5：根據回饋重寫

> **執行者：subagent**
> **輸入：** `./output/phase3/`（原稿）+ `./output/phase4/`（審稿結果）
> **輸出：** `./output/phase5/`

---

## 5.0 入口檢查

**IF `RESUME_FROM` > 5：**
1. 從 `./output/phase5/` 讀取 checkpoint：
   - `one_page.md` → 修正後主報告
   - `diagrams.md` → 修正後圖表規格
   - `table.md` → 修正後數據表
   - `glossary.md` → 修正後術語詞彙表
   - `script.md` → 修正後演講稿
   - `citation_map.md` → 來源對照表
2. 跳過本 Phase，直接進入 Phase 6

**ELSE：**
- 正常執行下方流程

---

根據使用者對 Issue List 的回答，修正初稿。

---

## 修正策略

| 使用者回答 | 處理方式 |
|------------|----------|
| 同意修正 | 按建議修改 |
| 提供補充 | 整合新資訊後修改 |
| 維持原樣 | 保留，但考慮是否需加註條件 |

---

## 禁止事項

- 不可硬撐沒有證據的結論
- 不可隱藏矛盾
- 不可在沒數字時寫具體百分比
- 不可忽略使用者提供的補充資訊

---

## 內容恢復流程（處理素材完整性 Issue）

當 Phase 4 審稿發現 `missing_technical_detail` 或 `unused_citation` Issue 時，需要從 materials.md 恢復遺失的技術細節。

### 適用 Issue 類型

| Issue 類型 | 說明 | 恢復目標 |
|-----------|------|---------|
| `missing_technical_detail` | 技術實體（執行緒、函數、表格）遺失 | 從 materials.md 恢復到 technical_appendix.md 或 one_page.md |
| `unused_citation` | Citation 未使用 | 檢查 Citation 內容，決定恢復到哪個檔案 |

### 恢復步驟

#### 步驟 1：定位原始素材

從 Issue 中提取 Citation ID，然後從 materials.md 讀取對應內容。

**範例**：
```
Issue: "Q10：Android 完整流程的執行緒名稱遺失 [C6]"
→ 提取 Citation ID: C6
→ 從 ./output/phase2/materials.md 讀取 [C6] 區塊的內容
→ 從 ./output/phase2/citation_map.md 讀取 [C6] 的補充說明（如有）
```

#### 步驟 2：判斷恢復目標位置

根據 DETAIL_LEVEL 和 Issue 類型，決定將內容恢復到哪個檔案：

| DETAIL_LEVEL | Issue 類型 | 恢復位置 |
|--------------|-----------|---------|
| BALANCED | missing_technical_detail | technical_appendix.md |
| BALANCED | unused_citation（技術細節）| technical_appendix.md |
| BALANCED | unused_citation（核心證據）| one_page.md + technical_appendix.md |
| TECHNICAL | missing_technical_detail | one_page.md（主報告包含所有細節）|
| TECHNICAL | unused_citation | one_page.md |
| EXECUTIVE | missing_technical_detail | technical_appendix.md |
| EXECUTIVE | unused_citation | technical_appendix.md（主報告極簡）|

**如何區分「技術細節」與「核心證據」**：
- **核心證據**：直接支持標題結論的數字、測試結果、效能改善數據
- **技術細節**：實作機制、執行緒列表、函數呼叫鏈、引擎差異分析

#### 步驟 3：內容整合

**恢復到 technical_appendix.md 的格式**：

```markdown
## {主題名稱} [{Citation ID}]

{從 materials.md [{Citation ID}] 抽取的完整內容}

### 執行緒列表
1. **{執行緒名稱}**：{說明}
   - 執行位置：{程序名稱}
   - 優先級：{優先級}

2. **{執行緒名稱}**：{說明}
   ...

### 函數呼叫鏈
```
{函數名稱1}()
  → {函數名稱2}()
    → {函數名稱3}()
```

### 技術總結表
| 階段 | 執行緒 | 函數 | 同步機制 | 耗時 |
|------|--------|------|---------|------|
| {階段1} | {執行緒} | {函數} | {機制} | {時間} |
| ... | ... | ... | ... | ... |

（來源：materials.md [{Citation ID}]）
```

**恢復到 one_page.md 的格式**：

```markdown
## 證據

### {證據點標題}

{簡化摘要}。在 Android Touch2Photon 流程中，觸控事件經過以下執行緒處理：InputReader → InputDispatcher → ViewRootImpl → RenderThread。詳細的函數呼叫鏈和時序分析見技術附錄頁 2。[C6]

（如 DETAIL_LEVEL = TECHNICAL，則直接展開完整內容，不使用「詳見附錄」）
```

#### 步驟 4：篇幅控制

**one_page.md 篇幅限制**：
- 如果恢復內容後超過篇幅（約 1500-2000 字），將詳細流程移到 technical_appendix.md
- 主報告保留摘要 + 引用附錄頁碼：「詳見技術附錄頁 X」

**technical_appendix.md 篇幅建議**：
- 單一主題章節不超過 1 頁（約 500-700 字 + 1-2 個表格/圖）
- 如內容過多，拆分為多個子章節

#### 步驟 5：保留 Citation 追溯性

**關鍵原則**：
- ✓ 所有恢復的內容都必須標註 Citation ID
- ✓ 保留原始 materials.md 的引用來源
- ✗ 禁止憑空生成不在 materials.md 中的技術細節
- ✗ 禁止修改原始數字或結論
- ✗ 禁止將不同 Citation 混合而無法追溯

**範例**：

```markdown
✓ 正確：
## Android Touch2Photon 完整流程 [C6]
InputReader 執行緒負責讀取觸控事件，優先級為 Real-time。[C6]

✗ 錯誤：
## Android Touch2Photon 完整流程
InputReader 執行緒負責讀取觸控事件（優先級為 -8，這是標準配置）。
（問題：優先級 -8 不在 materials.md [C6] 中，是憑空生成的）
```

### 多個 Citation 同時遺失的處理

當 Issue 指出多個 Citation 未使用（例如 [C11][C12]）：

1. **檢查內容相關性**：這些 Citation 是否描述同一主題？
2. **合併或分開**：
   - 同一主題（如 C11、C12 都是引擎差異分析）→ 合併為一個章節
   - 不同主題 → 分開為不同章節
3. **保留所有 Citation ID**：
   ```markdown
   ## Unity vs Unreal 引擎差異分析 [C11][C12]

   Unity 採用 Double Buffering 架構... [C11]

   Unreal 採用 Pipelined 架構... [C12]
   ```

### 內容恢復的驗證

恢復內容後，必須檢查：

| 檢查項目 | 驗證方法 |
|---------|---------|
| 完整性 | Issue 提到的所有技術實體（執行緒/函數/表格）都已恢復？|
| 追溯性 | 每段恢復的內容都有 Citation ID？|
| 一致性 | 恢復的內容與 materials.md 原文一致？沒有憑空生成？|
| 位置正確 | 根據 DETAIL_LEVEL 恢復到正確檔案（one_page.md 或 technical_appendix.md）？|
| 引用連結 | one_page.md 有「詳見技術附錄頁 X」的引用？|

---

## 重要：每一輪都必須輸出完整的 Markdown 文件

每次重寫時，必須輸出**完整的**文件內容，不要只輸出差異或修改的部分：

```
✗ 錯誤做法：「將第 3 點改為...」「在技術關鍵點後加入...」
✓ 正確做法：輸出完整的 one_page.md、diagrams.md、script.md、glossary.md
```

**原因：**
- 每一輪的輸出必須是獨立完整的，不依賴上下文
- 避免累積錯誤或遺漏
- 方便使用者直接複製使用

### 每輪必須完整輸出的文件

| 文件 | 說明 |
|------|------|
| `one_page.md` | 完整報告內容（每輪都要全部重新輸出）|
| `diagrams.md` | 完整圖表規格（每輪都要全部重新輸出）|
| `script.md` | 完整演講稿（每輪都要全部重新輸出）|
| `glossary.md` | 完整術語表（每輪都要全部重新輸出）|
| `citation_map.md` | 完整來源對照表（每輪都要全部重新輸出）|
| `technical_appendix.md` | 完整技術附錄（DETAIL_LEVEL = BALANCED 或 EXECUTIVE 時，每輪都要全部重新輸出）|

即使某個文件沒有修改，也要完整輸出，確保每一輪的結果都是獨立可用的。

---

## Phase 5.5：多輪審稿迭代（如 MAX_ITERATIONS > 1）

當使用者設定多輪審稿時，重複 Phase 4 → Phase 5 流程。

### 關鍵原則：每輪審稿必須使用 Sub Agent

**為什麼每輪都要用 Sub Agent？**

如果同一個 AI 既寫又審，會產生「審跟沒審一樣」的問題：
- AI 傾向認為自己寫的內容是正確的
- 容易忽略自己剛才犯的錯誤
- 缺乏獨立的批判視角

每輪迭代的 Phase 4 審稿，都必須呼叫 Task tool 啟動獨立的 sub agent。

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
    執行 Phase 5（重寫） - 輸出完整 markdown
    迭代計數 += 1
```

### 每輪審稿的 Task Tool 呼叫方式

```
Task tool 參數：
- subagent_type: "general-purpose"
- prompt: |
    你是獨立審稿人，請審查以下一頁報告草稿。

    ## 審稿標準（必須全部檢查）
    1. 數據真實性：每個數字都有來源嗎？
    2. 對比公平性：比較基準是否合理？
    3. 結論支撐度：結論是否被數據支撐？
    4. 白話程度：國中生能看懂嗎？
    5. 術語解釋：專業術語有解釋嗎？

    ## 輸入
    one_page.md 內容：
    {貼上完整 one_page.md}

    glossary.md 內容：
    {貼上完整 glossary.md}

    ## 輸出格式
    對每個檢查項目給出：
    - ✅ 通過：簡述原因
    - ❌ 未通過：具體指出問題 + 具體修改建議

    特別注意「白話程度」：如果有任何段落國中生可能看不懂，
    必須提供具體的「原句 → 改寫句」建議。
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

## 5.9 Checkpoint 寫入

Phase 5 完成後，將所有輸出儲存到 checkpoint：

1. 建立目錄（跨平台，必須成功）：

   ```bash
   python -c "from pathlib import Path; Path('output/phase5').mkdir(parents=True, exist_ok=True)"
   ```

2. 使用 Write 工具寫入以下檔案（即使內容為空也要寫出檔案）：


**./output/phase5/one_page.md**
```
{修正後的主報告內容}
```

**./output/phase5/diagrams.md**
```
{修正後的圖表規格}
```

**./output/phase5/table.md**
```
{修正後的數據表，如無則寫入「# 無數據表」}
```

**./output/phase5/glossary.md**
```
{修正後的術語詞彙表}
```

**./output/phase5/script.md**
```
{修正後的演講稿}
```

**./output/phase5/citation_map.md**
```
{來源對照表}
```

**./output/phase5/technical_appendix.md**
```
{完整技術附錄，如 DETAIL_LEVEL = TECHNICAL 則寫入「# 無技術附錄（所有細節在主報告中）」}
```

---

## 5.9.1 Checkpoint 驗證（強制；失敗即中止）

完成 Write 後，必須用 Bash 工具驗證檔案存在且非空：

```bash
python -c "from pathlib import Path; files=['output/phase5/one_page.md','output/phase5/diagrams.md','output/phase5/table.md','output/phase5/glossary.md','output/phase5/script.md','output/phase5/citation_map.md','output/phase5/technical_appendix.md']; missing=[f for f in files if not Path(f).exists() or Path(f).stat().st_size==0]; print('missing_or_empty',missing); raise SystemExit(1 if missing else 0)"
```

若驗證失敗，代表 checkpoint 未落盤或寫入失敗，必須停止流程並修正。


### 多輪迭代時的版本保留

當迭代輪次 > 1 時，同時複製到 iterations 目錄：

```bash
python -c "from pathlib import Path; import shutil; n='{N}'; dst=Path(f'output/iterations/iter{n}/phase5'); dst.mkdir(parents=True, exist_ok=True);
for name in ['one_page.md','diagrams.md','table.md','glossary.md','script.md','citation_map.md','technical_appendix.md']:
    shutil.copy2(Path('output/phase5')/name, dst/name)"
```

