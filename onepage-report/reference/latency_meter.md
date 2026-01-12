# MTK Latency Meter
這題的靈感來源  
https://gpuopen.com/learn/integrating-amd-radeon-anti-lag-2-sdk-in-your-game/  
https://github.com/GPUOpen-Tools/frame_latency_meter  

## 1. PC 上「端到端延遲量測」已被驗證可工程化的前提條件（參考資料）

以 AMD 的 Frame Latency Meter（FLM）/ Anti-Lag 2 生態為例，其能被廣泛用於 A/B 與回歸，並非偶然，而是建立在以下可歸納條件之上：
- 量測 KPI 清晰且可重複
  - 「Input → Display（或 Input → Photon）」的端到端延遲（input lag）可被定義成**事件時間差**
- 工具可量產化
  - 支援長時間自動取樣、CSV 匯出、ROI（畫面小區域）設定、熱鍵/腳本控制
- 量測方法能避開遊戲內容依賴（或至少可降低）
  - 透過 ROI 變化偵測（畫面有明確變化即可）量測「輸入 → 顯示」
- 工具限制被明確揭露
  - 擷取路徑/效能瓶頸/特定模式限制，都可以在測試設計中被控制或標註

---

## 2. Dimensity / Android 在「延遲量測」的現況與缺口（已知事實）

我們現行常用的量測與治理主軸偏向：
- FPS / 1% low / frame time（渲染結果）
- 功耗 / 溫控（平台治理結果）
- thread runnable delay / wakeup latency（排程原因）

但在 DX7 的「玩家體感」面向，仍缺一個可量產回歸的核心 KPI：
- **Input → Display（端到端延遲）**  
  - 目前多依賴少量人工體感或高成本外部設備（例如高速攝影），難以做大規模回歸與跨版本比較

## 2.5 現行量測方式的成本問題（我們為什麼需要工具化）

目前在手機端要量 Input→Display 延遲，常見作法是：
- 用 **iPhone 240FPS**（或同級高速攝影）對著螢幕錄影
- 事後以人工方式「逐幀數幀」：從輸入動作發生到畫面變化出現的幀差換算成毫秒

這種方式的主要問題：
- **量測成本高**
  - 需要額外設備、架設/對焦/光線控制
  - 每次測試都需要人工回放與數幀，無法大量取樣
- **回歸困難**
  - 人工流程難以標準化，跨人/跨場景一致性不足
  - 很難把 input lag 變成每日/每週的自動回歸 KPI
- **A/B 迭代慢**
  - 每個策略調整都要重新拍、重新數，導致迭代週期拉長

因此 DX7 的核心是：把「高成本人工量測」轉成「可自動化、可大量取樣、可回歸」的 MTK Latency Meter 能力。

---

---

## 3. 與 AMD FLM 的「結構相似性」對照（非等價、但可比）

| 量測模組 | AMD FLM（PC） | MTK Latency Meter（Android） |
|---|---|---|
| Input Trigger | 產生/捕捉輸入事件 | 產生/捕捉 touch/gesture（自動化可重播） |
| Frame Capture | 連續擷取畫面（含限制/瓶頸） | 連續擷取畫面（以 ROI 為主，避免工具成本蓋過真實延遲） |
| ROI Detector | ROI 變化偵測（差分/門檻） | ROI 變化偵測（差分/SAD/門檻，支援高對比 pattern） |
| Output | 統計 + CSV（可回歸） | 統計 + CSV（可回歸），並可選擇對齊 Perfetto/AGI trace |

需要特別說明的是：
- Android 的 capture / 權限 / overlay 路徑與 PC 不同，兩者不等價  
- 但在 **「用 ROI 變化偵測把端到端延遲工具化」** 這個方法論上，具可比性  
- 工程焦點是：把限制說清楚，讓測試設計能穩定重複，而不是追求任何場景都能量

---

## 4. 為何「可能」成為 DX7 的直接效益（合理推論）

若我們能把 Input→Display 延遲量測變成平台能力：
- 低延遲治理（例如 input sample 前 pace、減少 pipeline 排隊）的效益可被量化
- 各種系統治理策略（FPSGO/Loom/排程策略/控頻策略）可以用同一套 KPI 做 A/B
- 在「Avg FPS 相近 / target FPS 相同」前提下，可直接回答主管關心的問題：
  - 「1% low 看起來差不多，但為什麼體感不一樣？」  
  - 「同樣功耗下，哪個方案 input lag 更低、更穩？」

> 結論：MTK Latency Meter 的價值不在於替代 FPS 指標，而是補齊「玩家體感」的可回歸 KPI。

---

## 5. POC 設計
### 條件
- A：現行方案（不量 input lag）
- B：現行方案 + **MTK Latency Meter（外掛式 / 不改遊戲）**
- C：現行方案 + **MTK Latency Meter（引擎整合式 / 有 test pattern 或 marker）**

### 遊戲場景
1. 遊戲高刷（穩態）
2. 遊戲 + 抖音 複合場景（干擾/搶佔）

### 成功判定
- 工具可用性
  - 可長時間自動取樣
  - 有效 sample 率高（偵測成功率/誤判率可控）
  - CSV 可回歸（版本間可比）
- KPI 產出
  - 在 Avg FPS 相近（或 target FPS 相同）前提下，能穩定輸出：
    - Input→Display：P50 / P95 / P99（ms）
  - 並可在 A/B/C 下看到可重複差異（方向一致、幅度可信）

---

## 6. 參考資料（原始連結）
- AMD Radeon Anti-Lag 2：Integrating Radeon Anti-Lag 2 SDK in your game  
  https://gpuopen.com/learn/integrating-amd-radeon-anti-lag-2-sdk-in-your-game/
- GPUOpen Tools：Frame Latency Meter（repo）  
  https://github.com/GPUOpen-Tools/frame_latency_meter
