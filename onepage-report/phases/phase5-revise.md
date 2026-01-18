# Phase 5：根據回饋重寫

> **執行者：subagent**
> **輸入：** `./output/phase3/`（原稿）+ `./output/phase4/`（審稿結果）
> **輸出：** `./output/phase5/`

---

## 5.0 入口檢查

**IF `RESUME_FROM` > 5：**
1. 從 `./output/phase5/` 讀取 checkpoint，跳過本 Phase
2. 直接進入 Phase 6

**ELSE：** 正常執行下方流程

---

## 修正策略

| 使用者回答 | 處理方式 |
|------------|----------|
| 同意修正 | 按建議修改 |
| 提供補充 | 整合新資訊後修改 |
| 維持原樣 | 保留，但考慮是否需加註條件 |

---

## 禁止事項

- ✗ 不可硬撐沒有證據的結論
- ✗ 不可隱藏矛盾
- ✗ 不可在沒數字時寫具體百分比
- ✗ 不可忽略使用者提供的補充資訊

---

## 內容恢復流程

當 Phase 4 審稿發現 `missing_technical_detail` 或 `unused_citation` Issue 時，需要從 materials.md 恢復遺失的技術細節。

**⚠️ 詳細流程請讀取：** `{skill_dir}/phases/appendix/phase5-content-recovery.md`

### 恢復位置

v4.1 固定為 TECHNICAL 模式，所有內容都恢復到 `one_page.md`。

**關鍵原則**：
- ✓ 所有恢復的內容都必須標註 Citation ID
- ✓ 保留原始 materials.md 的引用來源
- ✗ 禁止憑空生成不在 materials.md 中的技術細節

---

## 重要：每一輪都必須輸出完整的 Markdown 文件

每次重寫時，必須輸出**完整的**文件內容，不要只輸出差異或修改的部分：

```
✗ 錯誤做法：「將第 3 點改為...」「在技術關鍵點後加入...」
✓ 正確做法：輸出完整的 one_page.md、diagrams.md、script.md、glossary.md
```

### 每輪必須完整輸出的文件

| 文件 | 說明 |
|------|------|
| `one_page.md` | 完整報告內容（包含所有技術細節） |
| `diagrams.md` | 完整圖表規格 |
| `script.md` | 完整演講稿 |
| `glossary.md` | 完整術語表 |
| `citation_map.md` | 完整來源對照表 |

即使某個文件沒有修改，也要完整輸出。

---

## Phase 5.5：多輪審稿迭代

當 `MAX_ITERATIONS > 1` 時，重複 Phase 4 → Phase 5 流程。

### 關鍵原則：每輪審稿必須使用 Sub Agent

**為什麼每輪都要用 Sub Agent？**
- AI 傾向認為自己寫的內容是正確的
- 容易忽略自己剛才犯的錯誤
- 缺乏獨立的批判視角

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
    執行 Phase 5（重寫）
    迭代計數 += 1
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

## Checkpoint 寫入

1. 建立目錄：
   ```bash
   python -c "from pathlib import Path; Path('output/phase5').mkdir(parents=True, exist_ok=True)"
   ```

2. 使用 Write 工具寫入：
   - `./output/phase5/one_page.md`（包含所有技術細節）
   - `./output/phase5/diagrams.md`
   - `./output/phase5/table.md`（如無則寫「# 無數據表」）
   - `./output/phase5/glossary.md`
   - `./output/phase5/script.md`
   - `./output/phase5/citation_map.md`

3. 驗證（必須）：
   ```bash
   python -c "from pathlib import Path; files=['output/phase5/one_page.md','output/phase5/diagrams.md','output/phase5/table.md','output/phase5/glossary.md','output/phase5/script.md','output/phase5/citation_map.md']; missing=[f for f in files if not Path(f).exists() or Path(f).stat().st_size==0]; print('missing_or_empty',missing); raise SystemExit(1 if missing else 0)"
   ```

### 多輪迭代時的版本保留

當迭代輪次 > 1 時，同時複製到 `output/iterations/iter{N}/phase5/`。
