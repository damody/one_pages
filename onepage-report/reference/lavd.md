# 提案：以 LAVD（scx_lavd / sched_ext）補足 FPSGO，在「同算力」下提升遊戲 1% low
這題的靈感來源
https://www.techbang.com/posts/127134-meta-steam-deck-anti-lag-server-tech

## 1 歷史回顧
- MTK 已有 FPSGO，可有效做幀率/功耗導向的資源治理。
- 但在「關鍵線程過多、互相喚醒/等待關係複雜」的遊戲情境，僅靠 FPSGO 很難做到 task graph 級的精細排程控制，因此 1% low / P99 frame time 仍可能不穩。
- Steam Deck（同屬行動裝置形態）已導入並驗證的 LAVD 排程思路，主打以 tail latency 為 KPI：在不增加硬體算力下，透過排程讓關鍵路徑上的 thread 更穩定、降低關鍵喚醒延遲，從而改善 1% low。
- 建議啟動 POC：以 LAVD 作為 FPSGO 的互補層（不是取代），目標是以量測數據證明：同等畫質/同等 target FPS 下，1% low 提升且功耗波動下降或不惡化。

## 2 問題與痛點
- 遊戲一幀由多個 thread 串成 pipeline（Game/Render/RHI/Driver/OS），掉幀通常來自少數關鍵幀被延後（tail latency），不是平均算力不足。
- FPSGO 偏向幀率/負載/功耗的調控迴路；當 critical chain 增多（多 worker、多 async、更多同步點）時：
  - 只靠 boost/調頻容易變成粗粒度
  - 功耗上去，但關鍵幀仍偶發 miss deadline
  - 在背景負載、溫控、頻率抖動時更明顯

## 3 解法主張：FPSGO + LAVD 的分工（互補）
- FPSGO：回答「資源要給多少」（macro：頻率/target FPS/功耗策略）
- LAVD：回答「資源先給誰、關鍵時刻誰不能等」（micro：排程順序/關鍵喚醒延遲）
- 在有效益的遊戲場景可以透過MAGT下hint，來開關這個Feature

預期增量：
- 在同樣算力（相近平均 util/freq）下，讓 frame critical path 的 thread 更少被插隊
- 降低 wakeup→running latency
- 直接反映在 P99 frame time 收斂、1% low 提升
- 長時間遊戲下，減少「為了救尾端而暴力拉頻」的需求 → 功耗波動有機會下降或不惡化

## 4 POC 設計
### 條件
- A：現行方案(FPSGO/Loom)
- B：現行方案(Loom) + LAVD（scx_lavd）
- C：現行方案(FPSGO) + LAVD（scx_lavd）

### 遊戲場景
1. 遊戲高刷（穩態）
2. 遊戲 + 抖音 複合場景

### 成功判定
- 在 Avg FPS 相近（或 target FPS 相同）的前提下：
  - 1% low 明顯提升
  - 關鍵 thread 的 wakeup latency / runnable delay 顯著下降
  - 功耗波動不惡化（理想是下降；至少不因救delay而急拉）

## 5 附：參考資料（原始連結）
- OSSNA 2024 scx_lavd 投影片（核心演算法與定位）https://static.sched.com/hosted_files/ossna2024/9b/scx-lavd-oss-na24.pdf
- scx 原始碼（sched_ext schedulers）https://github.com/sched-ext/scx
- Linux sched_ext 文件（機制與介面）https://docs.kernel.org/scheduler/sched-ext.html
- Phoronix（遊戲向評測報導）https://www.phoronix.com/news/LAVD-Scheduler-Linux-Gaming
- sched-ext 官方（scx_lavd 說明）https://sched-ext.com/docs/scheds/rust/scx_lavd
