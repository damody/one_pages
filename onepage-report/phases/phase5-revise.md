# Phase 5：根據回饋重寫

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

1. 建立目錄：`mkdir -p ./output/phase5`

2. 使用 Write 工具寫入以下檔案：

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

### 多輪迭代時的版本保留

當迭代輪次 > 1 時，同時複製到 iterations 目錄：

```bash
mkdir -p ./output/iterations/iter{N}/phase5
cp ./output/phase5/* ./output/iterations/iter{N}/phase5/
```
