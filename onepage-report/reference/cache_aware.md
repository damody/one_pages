各位長官好
以下是For DX7 的題目

# Cache Aware
這題的靈感來源
https://www.phoronix.com/news/Cache-Aware-Scheduling-Go

## 1. PC 上 sched_cache 已被驗證有效的前提條件（參考資料）

在 PC／Server 平台（以 AMD EPYC Genoa 為代表），Cache-Aware Scheduling 之所以能產生顯著效果，並非偶然，而是建立在以下可歸納條件之上：
- 平台具備 **多個 cache domain**
  - NUMA node
  - CCX（私有 L2、分割 L3）
- thread 屬於 **長壽命、持續執行型**
- thread 之間 **存在高度資料共享**
- 跨 cache domain 遷移，會造成 **實質且可量測的 cache 破壞成本**
在這些條件同時成立時，Linux sched_cache 僅透過「降低不必要的跨 cache domain migration」，即可帶來：
- Host time 明顯下降（Genoa 約 -45%）
- Throughput 顯著提升（約 +82%）
---

## 2. Dimensity SoC 的 cache / memory 架構（已知事實）

以天璣 9500 為例，其 CPU 與快取結構具備以下可確認特性：
- CPU 架構：
  - 1 × Ultra
  - 3 × Big
  - 4 × Little
- Cache 層級設計：
  - 每個 cluster 內共用一顆 L2 cache
  - 不同 cluster 之間 **不共享 L2 cache**
- SoC 層級快取：
  - L3 cache（16MB）
  - SLC（10MB），供跨 cluster 使用
- 主記憶體：
  - LPDDR5X，其延遲與頻寬特性明顯不同於 server 等級 DDR

---

## 3. 與 PC 平台的「結構相似性」對照（非等價、但具可比性）

| 平台        | 可觀察的 cache domain 邊界 
|-------------|---------------------------------------
| AMD Genoa   | CCX/NUMA（L2不共享，每8核共享1個L3）
| Dimensity  | Cluster（L2 不共享，L3/SLC 共用）

需要特別說明的是：

- Dimensity 並非與 Genoa 在 cache 架構上「等價」
- 但在 **「存在多個 cache domain，且跨 domain 遷移具有實質成本」** 這一點上，兩者具備可比性
- 且在手機 SoC 上，cache domain 的邊界更早出現在 **L2 層級**，其容量更小、對 IPC 更敏感

---

## 4. 為何「可能」出現與 PC 類似的效果（合理推論）

若以下條件在手機遊戲場景中成立：

- 遊戲關鍵 threads（如 GameThread / RenderThread）為：
  - 長壽命
  - 持續執行
- threads 之間存在穩定的資料共享（scene state、render state）
- 跨 cluster 遷移會導致：
  - L2 cache 內容不可沿用
  - working set 需要重新 warm-up
- 記憶體延遲（LPDDR5X）使 cache miss 成本被進一步放大

那麼在工程上可以合理推論：

> **降低不必要的跨 cluster migration，  
> 在手機平台上「有機會」帶來與 PC 類似方向的效益，  
> 包含效能穩定度與功耗行為的改善。**

- 在有效益的遊戲場景可以透過MAGT下hint，來開關這個Feature

## 5 POC 設計
### 條件
- A：現行方案(FPSGO/Loom)
- B：現行方案(Loom) + LAVD（cache aware）

### 遊戲場景
1. 遊戲高刷（穩態）
2. 遊戲 + 抖音 複合場景

### 成功判定
- 在 Avg FPS 相近（或 target FPS 相同）的前提下：
  - 1% low 明顯提升
  - 關鍵 thread 的 wakeup latency / runnable delay 顯著下降
  - 功耗波動不惡化（理想是下降；至少不因救delay而急拉）


## 5. 參考資料

- Openwall LKML（PATCH v2：完整 POC + `_get_migrate_hint()` + ftrace/procfs 觀測工具）：https://lists.openwall.net/linux-kernel/2025/12/03/1427
- LKML.org（RFC v3 Cover：從 Wake-up placement 轉向 Load Balancing 的設計動機/決策脈絡）：https://lkml.org/lkml/2025/6/18/1575
- Patchew（RFC PATCH v4 Cover：mbox 下載入口，含功能開關 SCHED_CACHE_LB / SCHED_CACHE_WAKE）：https://patchew.org/linux/cover.1754712565.git.tim.c.chen%40linux.intel.com/
- Patchew（PATCH：SCHED_CACHE_LB 相關變更頁，便於逐 patch 檢視）：https://patchew.org/linux/cover.1754712565.git.tim.c.chen%40linux.intel.com/eba3303cdab63e2d96dcc630d153004e4afb88f3.1754712565.git.tim.c.chen%40linux.intel.com/
- Patchew（PATCH：SCHED_CACHE_WAKE 相關變更頁，便於逐 patch 檢視）：https://patchew.org/linux/cover.1754712565.git.tim.c.chen%40linux.intel.com/144358df73cbb8c7d24f757fc40cb068be603bed.1754712565.git.tim.c.chen%40linux.intel.com/

- Phoronix（Cache-Aware Scheduling Go：整理 Genoa/Sapphire Rapids 測試與改善幅度）：https://www.phoronix.com/news/Cache-Aware-Scheduling-Go
- Phoronix（Cache-Aware Scheduling @ LPC 2025：patch 背景與簡報資訊）：https://www.phoronix.com/news/Cache-Aware-Scheduling-2025
- LWN（Cache-aware load-balancing：技術解讀與設計重點整理）：https://lwn.net/Articles/1033190/
- LWN（Cache-aware scheduling patch 追蹤/整理：對 patch 系列的延伸說明）：https://lwn.net/Articles/1041668/
- OpenBenchmarking（對應測試結果頁：可查 benchmark 結果與環境配置）：https://openbenchmarking.org/result/2510233-NE-CACHEAWAR82%26sor%26grr

- Notebookcheck（Dimensity 9500 規格：CPU 叢集、L3/SLC、記憶體等整理）：https://www.notebookcheck.net/MediaTek-Dimensity-9500-Processor-Benchmarks-and-Specs.957550.0.html

- Android Developers（AGI：Analyze thread scheduling，說明 affinity/migration 對效能的影響與建議）：https://developer.android.com/agi/sys-trace/threads-scheduling
- AOSP（Performance Hint API：系統層 performance hint 機制總覽）：https://source.android.com/docs/core/perf/performance-hint-api
- Android Developers（ADPF Performance Hint API（繁中）：遊戲端如何使用 performance hint）：https://developer.android.com/games/optimize/adpf/performance-hint-api?hl=zh-tw
- AOSP（Performance management：Android 效能/功耗治理架構背景）：https://source.android.com/docs/core/power/performance

- Arm（big.LITTLE：異質核心架構背景（英文））：https://www.arm.com/technologies/big-little
- Arm（big.LITTLE：異質核心架構背景（繁中））：https://www.arm.com/zh-TW/technologies/big-little

