<template>
  <div class="card wide">
    <div class="card-header">
      <div>
        <p class="card-kicker">报表</p>
        <h2>使用率与财务</h2>
      </div>
      <span class="chip chip-neutral">可导出</span>
    </div>
    <div class="report-grid">
      <div class="report-card">
        <h3>周使用率</h3>
        <p>平均占用 72%</p>
        <div class="progress-ring" style="--value: 0.72"></div>
      </div>
      <div class="report-card">
        <h3>校外月度收入</h3>
        <p>已确认 ¥84,200</p>
        <div class="progress-ring" style="--value: 0.61"></div>
      </div>
      <div class="report-card">
        <h3>检修负载</h3>
        <p>14 台设备排期</p>
        <div class="progress-ring" style="--value: 0.38"></div>
      </div>
      <div class="report-card">
        <h3>借用满意度</h3>
        <p>4.7 / 5.0</p>
        <div class="progress-ring" style="--value: 0.9"></div>
      </div>
    </div>
  </div>
</template>
