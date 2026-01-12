# MTK Anti-Lag：基於 SDK 級別的「輸入-顯示」延遲優化方案

這題的靈感來源：
- [AMD Radeon™ Anti-Lag 2 SDK 整合指南](https://gpuopen.com/learn/integrating-amd-radeon-anti-lag-2-sdk-in-your-game/)
- [AMD Frame Latency Meter (FLM) 量測工具](https://github.com/GPUOpen-Tools/frame_latency_meter)

---

## 1. PC 上 Anti-Lag 2 已被驗證有效的前提條件

在 PC 平台（以 AMD Radeon 系列為代表），Anti-Lag 2 之所以能產生顯著效果，是因為它將治理邏輯從「驅動層」深入到了「遊戲引擎內」：

* **解決 CPU-Bound 造成的排隊**：當 CPU 處理指令速度快於 GPU 渲染時，會在渲染管線中產生 Frame Queue。
* **精準同步點 (In-engine Synchronization)**：在遊戲引擎的渲染管線（如 `Present()` 之前）插入同步點，確保 CPU 不會無限制地超前。
* **輸入採樣對齊**：確保 Input Sampling（滑鼠/鍵盤採樣）發生在該幀渲染開始前的最後一刻。

**在這些條件成立時，AMD Anti-Lag 2 帶來了：**
* **系統延遲顯著下降**：在競技類遊戲（如《CS2》）中延遲降低約 **37%**。
* **響應流暢度提升**：避免了傳統限幀器導致的微卡頓。

---

## 2. Dimensity SoC 與 Android 系統的延遲現狀

以天璣 9500 平台運行 Android 遊戲為例，目前的延遲瓶頸包含：

* **Android BufferQueue 機制**：生產者（App）與消費者（SurfaceFlinger）之間的 Buffer 輪轉，天生存在 **1-2 幀** 的緩衝延遲。
* **FPSGO 的治理範圍限制**：現有的 FPSGO 強項在於「保幀率」與「節能」，但難以感知引擎內部的 **Input-to-Render** 間隔，無法主動要求引擎延後採樣輸入。
* **SoC 調度開銷**：在高負載下，Input Event 的處理與渲染線程的喚醒抖動，會直接反映在 **Total System Latency** 上。

---

## 3. 與 PC 平台的「路徑相似性」對照

| 延遲階段 | PC (AMD Anti-Lag 2) | Dimensity (MTK Proposed) |
| :--- | :--- | :--- |
| **同步層級** | In-engine SDK (Vulkan/DX12) | **MAGT / Performance Hint API 擴展** |
| **關鍵同步點** | CPU `Present()` 與 GPU 執行完畢 | **RenderThread 提交與 SurfaceFlinger 消費** |
| **量測工具** | FLM (Software/Hardware) | **FLM + Android Systrace (AGI)** |

> **技術關鍵點：**
> 手機平台的挑戰在於觸控採樣（Touch Sampling）與顯示刷新率（Vsync）的同步比 PC 滑鼠更複雜。導入 SDK 級別的握手（Handshake）是實現微秒級延遲控制的唯一路徑。

---

## 4. 為何導入 Anti-Lag 技術具有實質效益（合理推論）

若能在天璣平台上實作類似 Anti-Lag 2 的 SDK 協作機制：

* **消除無效排隊**：當 GPU 忙碌時，主動通知引擎推遲下一幀的輸入採樣，確保玩家點擊的是「螢幕上最新的一幀」。
* **優化渲染路徑 (Render Path)**：
    * 縮短從「觸控事件觸發」到「核心渲染指令發出」的間隔。
    * 收斂 **P99 Frame Time**，因為長尾延遲通常與 Frame Queue 的不穩定堆疊有關。

**工程推論結論：**
> **透過 SDK 實現引擎與 SoC 的深度節奏同步，能顯著降低「點擊到螢幕反應」的總延遲，這對於《鳴潮》、《和平菁英》等高頻互動遊戲是核心競爭力。**



---

## 5. POC 設計與成功判定

### 實驗條件
* **A 組 (Baseline)**：現行方案（僅開啟 FPSGO，無延遲同步）。
* **B 組 (Experimental)**：導入 **MTK Anti-Lag SDK**（實現引擎與平台同步）。

### 量測工具：FLM (Frame Latency Meter)
* 利用 FLM/ftrace/LTR 進行 **End-to-End Latency** 量測。
* 監控 **Click-to-Photon**（從點擊觸控到螢幕像素變化的總時間）。

### 成功判定準則
1.  **系統延遲下降**：全鏈路延遲在同等 FPS 下降低 **5%** 以上。
2.  **1% Low 提升**：Frame Time 抖動幅度明顯收斂。
3.  **功耗行為**：不因縮短延遲而造成溫升超標，維持功耗波動與 A 組持平。

---

## 6. 參考資料

* **AMD GPUOpen (Anti-Lag 2 SDK)**：[連結](https://gpuopen.com/learn/integrating-amd-radeon-anti-lag-2-sdk-in-your-game/)
* **GitHub (Frame Latency Meter)**：[連結](https://github.com/GPUOpen-Tools/frame_latency_meter)
* **Android Developers (Input Latency Optimization)**：[連結](https://developer.android.com/games/optimize/input-latency)
* **AOSP (Graphics Pipeline & SurfaceFlinger)**：[連結](https://source.android.com/docs/core/graphics/surfaceflinger-latency)