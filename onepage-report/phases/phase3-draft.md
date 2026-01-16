# Phase 3：產生初稿

## 3.0 入口檢查

**IF `RESUME_FROM` > 3：**
1. 從 `./output/phase3/` 讀取 checkpoint：
   - `one_page.md` → 主報告內容
   - `diagrams.md` → 圖表規格
   - `table.md` → 數據表（如有）
   - `glossary.md` → 術語詞彙表
   - `script.md` → 演講稿
2. 跳過本 Phase，直接進入 Phase 4

**ELSE：**
- 正常執行下方流程

---

根據素材內容與使用者設定，產生三到四份文件。

## 產出文件清單

| 文件 | 說明 | 格式規範 |
|------|------|----------|
| `one_page.md` | 主報告內容 | `Read {skill_dir}/templates/one-page-format.md` |
| `diagrams.md` | 圖表規格與生成指示 | `Read {skill_dir}/templates/diagrams-spec.md` |
| `table.md` | 數據比較表格（如有）| 見下方說明 |
| `glossary.md` | 術語詞彙表 | `Read {skill_dir}/templates/glossary-format.md` |
| `script.md` | 演講稿 | `Read {skill_dir}/templates/script-format.md` |

---

## 3.0.5 技術細節分類（DETAIL_LEVEL = BALANCED 或 EXECUTIVE 時執行）

在產生 one_page.md 之前，先將 materials.md 的內容分類為「主報告必須內容」和「技術附錄內容」。

### 分類標準

#### A. 主報告必須內容
- ✓ 結論和核心數字（改善百分比、效能提升）
- ✓ 問題陳述（為什麼需要這個方案）
- ✓ 推論邏輯（為什麼可行）
- ✓ POC 設計（如何驗證）
- ✓ 行動建議
- ✓ 成功判定準則

#### B. 技術附錄內容（可從主報告移出）
- ✓ 詳細的執行緒名稱和函數列表
- ✓ 完整的技術流程表格
- ✓ 引擎差異分析細節
- ✓ 系統架構圖的內部模組名稱
- ✓ 底層實作機制說明
- ✓ 程式碼片段或 API 呼叫範例

### 分類範例

| materials.md 內容 | 主報告 | 技術附錄 | 理由 |
|------------------|--------|---------|------|
| "Touch2Photon 延遲改善 81%" | ✓ | ✓ | 核心結論，兩處都要 |
| "執行緒: InputReader → InputDispatcher → ViewRootImpl" | ✗ | ✓ | 實作細節，移到附錄 |
| "問題：SurfaceFlinger 排隊延遲 2-3 幀" | ✓ | ✓ | 核心問題，兩處都要 |
| "Unity 使用 UnityEngine.Input.GetTouch()" | ✗ | ✓ | 引擎差異細節，移到附錄 |
| "預期改善 1% Low FPS 達 15%" | ✓ | - | 關鍵預期效益，主報告保留 |
| "函數呼叫: notifyMotion() → deliverInputEvent()" | ✗ | ✓ | 函數細節，移到附錄 |

### 輸出清單

分類完成後，建立兩份內容清單：

**主報告內容清單**：
- 用於 3.1 節產生 one_page.md
- 保留 Citation ID，但內容簡化為白話文
- 範例：[C6] Android 觸控事件處理機制導致輸入延遲，從觸控到顯示經過 4 個執行緒

**技術附錄內容清單**：
- 用於 3.1.5 節產生 technical_appendix.md
- 保留完整的技術細節和表格
- 範例：[C6-detail] 執行緒列表：InputReader, InputDispatcher, ViewRootImpl, RenderThread；函數呼叫鏈：InputReader::loopOnce() → InputDispatcher::notifyMotion() → ...

---

## 3.1 產生 one_page.md

**執行前請讀取：** `{skill_dir}/templates/one-page-format.md`

根據素材提取並整理內容，使用統一的完整格式。

### 3.1.1 根據 DETAIL_LEVEL 調整產出策略

**IF DETAIL_LEVEL = EXECUTIVE：**
- 使用「主報告內容清單」（由 3.0.5 節分類產生）
- 所有技術術語改用白話文或加 [[標記]]
- 每個區塊限制為 2-3 個 bullet points
- 目標：國小生能懂，極度簡潔
- 在 one_page.md 末尾加入技術附錄引用提示：
  ```markdown
  ---

  > **技術細節**：完整的執行緒列表、函數呼叫鏈、引擎差異分析請參閱技術附錄頁
  ```

**IF DETAIL_LEVEL = BALANCED：**（預設）
- 使用「主報告內容清單」（由 3.0.5 節分類產生）
- 技術細節移到附錄，主報告保留結論和推論
- 可使用部分技術術語，但需加 [[標記]]
- 在 one_page.md 末尾加入技術附錄引用提示：
  ```markdown
  ---

  > **技術細節**：完整的執行緒列表、函數呼叫鏈、引擎差異分析請參閱技術附錄頁 2-3
  ```
- 目標：國中生能懂，技術同仁可查附錄

**IF DETAIL_LEVEL = TECHNICAL：**
- 使用 materials.md 的完整內容
- 保留所有技術細節在主報告
- 可以使用專業術語（但仍需加 [[標記]] 供詞彙表解釋）
- **不產生 technical_appendix.md**（所有細節都在主報告）
- 目標：技術同仁能看懂實作細節

### 3.1.2 Citation 保留規則

**重要**：即使內容簡化，Citation ID 仍需保留。

範例：
```markdown
## 現況與問題
- Android 的觸控事件處理採用非同步機制，導致輸入延遲不可預測 [C6]

（C6 原始素材包含執行緒名稱和函數列表，但主報告簡化為白話描述）
```

### 3.1.3 核心原則（所有 DETAIL_LEVEL 共通）

- 內容密度要足夠讓主管做決策
- 每個 bullet 都要有實質內容
- 數字要具體（不要「大幅改善」，要「改善 81%」）
- 要有「已驗證」→「現況問題」→「為何可行」→「POC 設計」→「成功判定」的邏輯鏈
- DETAIL_LEVEL = EXECUTIVE/BALANCED 時必須讓國中生能看懂，TECHNICAL 時可使用專業術語

---

## 3.1.5 產生 technical_appendix.md（DETAIL_LEVEL = BALANCED 或 EXECUTIVE 時執行）

根據「技術附錄內容清單」（由 3.0.5 節分類產生）產生技術附錄頁面內容。

**IF DETAIL_LEVEL = TECHNICAL：**
- **跳過此節**，不產生 technical_appendix.md
- 所有技術細節都保留在 one_page.md 中

**ELSE（BALANCED 或 EXECUTIVE）：**
- 執行以下步驟

### 檔案格式規範

```markdown
# 技術附錄

## {主題名稱} [C{N}]

### 執行緒列表
1. **執行緒名稱**：功能描述
2. ...

### 函數呼叫鏈
```
函數A()
  → 函數B()
    → 函數C()
```

### 技術表格
| 欄位1 | 欄位2 | 欄位3 |
|------|------|------|
| ... | ... | ... |

（來源：materials.md [C{N}] + Citation Map 補充）
```

### 內容組織建議

| 原始素材類型 | technical_appendix.md 結構 | 範例 |
|------------|--------------------------|------|
| Android Touch2Photon 流程 | 執行緒列表 + 函數呼叫鏈 + 時序分析表 | [C6] InputReader, InputDispatcher, ... |
| 引擎差異分析 | 對比表格 + 共通性說明 | [C11][C12] Unity vs Unreal |
| 系統架構說明 | 分層架構 + 模組說明 | 應用層、框架層、HAL層、硬體層 |
| 技術機制詳解 | 機制說明 + 函數呼叫 + 參數說明 | VSync、BufferQueue、Fence |

### 內容範例

```markdown
# 技術附錄

## Android Touch2Photon 完整流程 [C6]

### 執行緒列表
1. **InputReader**：讀取觸控事件 (`/dev/input/event*`)
   - 執行位置：`system_server` 程序
   - 優先級：Real-time priority

2. **InputDispatcher**：分發事件到目標 App
   - 執行位置：`system_server` 程序
   - 通信方式：Binder IPC

3. **ViewRootImpl**：App 主執行緒處理事件
   - 執行位置：App 程序
   - 延遲來源：Main Thread 排隊 + GC

4. **RenderThread**：GPU 渲染執行緒
   - 執行位置：App 程序
   - 延遲來源：GPU Queue + Frame Pacing

### 函數呼叫鏈
```
InputReader::loopOnce()
  → EventHub::getEvents()              // 讀取 kernel event
  → InputDispatcher::notifyMotion()     // 通知 Dispatcher
    → dispatchMotionLocked()            // 查找目標 Window
      → Binder::transact()              // 跨程序通信（1-2ms）
        → ViewRootImpl::deliverInputEvent()
          → View::dispatchTouchEvent()  // 事件分發樹
            → scheduleTraversals()      // 排程重繪
              → ThreadedRenderer::syncAndDrawFrame()
                → GPU Command Buffer     // 送 GPU 渲染
```

### 時序分析表
| 階段 | 執行緒 | 耗時 | 累計 | 說明 |
|------|--------|------|------|------|
| 讀取輸入 | InputReader | 1-2ms | 1-2ms | 觸控 IC → kernel |
| 分發事件 | InputDispatcher | 2-3ms | 3-5ms | Binder IPC |
| App 處理 | UI Thread | 3-5ms | 6-10ms | 事件分發樹 + GC |
| GPU 渲染 | RenderThread | 8-12ms | 14-22ms | GPU Queue |
| SF 合成 | SurfaceFlinger | 2-4ms | 16-26ms | VSync 等待 + 合成 |

（來源：materials.md [C6] + Citation Map 補充）

---

## 引擎差異分析 [C11][C12]

### Unity 引擎
- **Input API**: `UnityEngine.Input.GetTouch()`
- **處理時機**: `Update()` 或 `FixedUpdate()`
- **底層對接**: 透過 JNI 呼叫 `android.view.MotionEvent`
- **特性**: Managed C# 層，有 GC 延遲

### Unreal 引擎
- **Input API**: `FSlateApplication::OnTouchStarted()`
- **處理時機**: Game Thread 的 Tick()
- **底層對接**: 透過 `FAndroidInputInterface::JNI_OnTouch()`
- **特性**: Native C++ 層，無 GC 延遲

### 對比表

| 項目 | Unity | Unreal | 影響 |
|------|-------|--------|------|
| API 層級 | Managed C# | Native C++ | Unreal 延遲略低 1-2ms |
| 底層機制 | 共同使用 InputEvent | 共同使用 InputEvent | 本方案對兩者都有效 |
| GC 影響 | 有（偶發性）| 無 | Unity 需注意 GC 調優 |

### 共通性
兩個引擎底層都走 Android 的 InputEvent 機制，因此本次 SDK 改善對兩者都有效，預期改善幅度相近。

（來源：materials.md [C11][C12]）
```

### 內容來源規則

**禁止事項**：
- ✗ 憑空生成不在 materials.md 中的技術細節
- ✗ 將不同 Citation 的內容混合而無法追溯
- ✗ 修改 materials.md 中的原始數字或結論

**必須遵守**：
- ✓ 所有內容來自 materials.md 的原始素材
- ✓ 保留完整的 Citation ID
- ✓ 如果 materials.md 沒有該資訊，標註「素材未提供」
- ✓ 如果 citation_map.md 有補充說明（web search 結果），加入附註

### 附錄頁數控制

- 建議 1-2 個主題（每個主題一個 `##` 標題）
- 如果技術細節過多，優先保留：
  1. 完整流程圖（含執行緒/函數名稱）
  2. 技術總結表（含數字對比）
  3. 引擎/平台差異分析
  4. 系統架構圖

---

## 3.2 圖表內容識別

在產生圖表前，先掃描素材識別**所有**可視覺化的內容。

### 識別規則

| 內容類型 | 識別關鍵詞 | 圖表類型 |
|----------|-----------|---------|
| 改善對比 | 改善、優化、問題→解決、Before/After、降低、提升、消除 | `before_after` |
| 平台對比 | PC、手機、Android、iOS、平台、差異、對照表、vs | `platform_compare` |
| 流程步驟 | 步驟、流程、鏈路、pipeline、→、然後、接著、管線 | `flow` |
| 時間序列 | 延遲、latency、時序、從...到...、全鏈路、Input-to-Display | `timeline` |

### 強制圖表要求（必須產生）

| 位置 | 必須圖表 | 類型 | 說明 |
|------|----------|------|------|
| **主投影片** | 前後比較圖 | `before_after` | 必須有！展示改善前 vs 改善後的差異 |
| **附錄** | 系統架構圖 | `architecture` | 必須有！展示整體系統/技術架構 |
| **附錄** | 流程比較圖 | `platform_compare` | 如有參考 PC/其他平台/方法，必須有！ |

---

## 3.3 產生 diagrams.md

**執行前請讀取：** `{skill_dir}/templates/diagrams-spec.md`

根據 3.2 識別的內容，產生**多張圖表**。

---

## 3.4 產生 table.md（如有數據比較時）

當素材中包含數據比較時產生表格。

### 判斷是否需要表格

- 素材中有 Before/After 數據
- 素材中有多個方案的指標比較
- 素材中有時間序列的變化數據
- 使用者設定 E1/E2（需要實驗數據）

### table.md 格式

```markdown
## 指標比較表

| Metric | Baseline | Experimental | Delta | 說明 |
|--------|----------|--------------|-------|------|
| FPS_avg | 60 fps | 66 fps | +10% | 平均幀率提升 |
| FPS_1%low | 45 fps | 52 fps | +16% | 最低幀更穩定 |
| Power | 900 mW | 820 mW | -9% | 功耗降低 |
| Jank | 15 次 | 3 次 | -80% | 掉幀大幅減少 |

**測試條件**：
- 裝置：Dimensity 9300
- 場景：原神璃月港
- 時長：120 秒
```

### 表格設計原則

- 欄位數量：4-6 欄（太多會擠）
- 行數：3-8 行（太多考慮分組）
- Delta 欄：自動計算，顯示百分比或差值
- 重要數據可用粗體標示

---

## 3.5 產生 glossary.md

**執行前請讀取：** `{skill_dir}/templates/glossary-format.md`

掃描 one_page.md 中的專業術語，用**國中生能懂**的方式產生術語解釋。

**優先使用 Citation Map 補充說明：**
- Phase 2.8 已對每個 Citation 進行 web search 並整理了術語解釋
- 產生 glossary.md 時，優先從 Citation Map 的「補充說明 > 術語解釋」取用

---

## 3.6 產生 script.md

**執行前請讀取：** `{skill_dir}/templates/script-format.md`

演講稿，每段標註要看投影片的哪個區塊。

**核心原則：金字塔式邏輯承接**
- 一句承接一句
- 邏輯不斷鏈
- 結論是總結

---

## 3.7 術語標記

在 one_page.md 中，用 `[[術語]]` 標記需要解釋的術語：

```markdown
## 技術關鍵點
- 降低跨 [[cluster]] 的 [[migration]]，可減少 [[L2 cache]] miss
- 預估可改善 [[1% Low FPS]] 達 15%
```

這些標記會在 Phase 6 渲染時轉換為超連結。

---

## 3.8 Checkpoint 寫入

Phase 3 完成後，將所有輸出儲存到 checkpoint：

1. 建立目錄（跨平台，必須成功）：

   ```bash
   python -c "from pathlib import Path; Path('output/phase3').mkdir(parents=True, exist_ok=True)"
   ```

2. 使用 Write 工具寫入以下檔案（即使內容為空也要寫出檔案）：


**./output/phase3/one_page.md**
```
{3.1 節產生的主報告內容}
```

**./output/phase3/diagrams.md**
```
{3.3 節產生的圖表規格}
```

**./output/phase3/table.md**
```
{3.4 節產生的數據表，如無則寫入「# 無數據表」}
```

**./output/phase3/technical_appendix.md**
```
{3.1.5 節產生的技術附錄，如 DETAIL_LEVEL = TECHNICAL 則寫入「# 無技術附錄（所有細節在主報告中）」}
```

**./output/phase3/glossary.md**
```
{3.5 節產生的術語詞彙表}
```

**./output/phase3/script.md**
```
{3.6 節產生的演講稿}
```

---

## 3.8.1 Checkpoint 驗證（強制；失敗即中止）

完成 Write 後，必須用 Bash 工具驗證檔案存在且非空：

```bash
python -c "from pathlib import Path; files=['output/phase3/one_page.md','output/phase3/diagrams.md','output/phase3/table.md','output/phase3/technical_appendix.md','output/phase3/glossary.md','output/phase3/script.md']; missing=[f for f in files if not Path(f).exists() or Path(f).stat().st_size==0]; print('missing_or_empty',missing); raise SystemExit(1 if missing else 0)"
```

若驗證失敗，代表 checkpoint 未落盤或寫入失敗，必須停止流程並修正。

