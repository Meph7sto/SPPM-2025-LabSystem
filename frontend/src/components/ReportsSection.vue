<template>
  <div class="card wide">
    <div class="card-header">
      <div>
        <p class="card-kicker">报表</p>
        <h2>使用率与财务</h2>
      </div>
      <span class="chip chip-neutral">可导出</span>
    </div>
    <div v-if="stats" class="report-grid">
      <div class="report-card">
        <h3>总预约数</h3>
        <p>{{ stats.total_reservations }} 次</p>
        <div class="progress-ring" :style="`--value: ${calculateRatio(stats.completed, stats.total_reservations)}`"></div>
      </div>
      <div class="report-card">
        <h3>已完成预约</h3>
        <p>{{ stats.completed }} 次</p>
        <div class="progress-ring" :style="`--value: ${calculateRatio(stats.completed, stats.total_reservations)}`"></div>
      </div>
      <div class="report-card">
        <h3>校外月度收入</h3>
        <p>¥ {{ stats.total_payment.toLocaleString() }}</p>
        <div class="progress-ring" style="--value: 0.61"></div>
      </div>
      <div class="report-card">
        <h3>当前借出中</h3>
        <p>{{ stats.borrowed }} 台</p>
        <div class="progress-ring" :style="`--value: ${calculateRatio(stats.borrowed, stats.total_reservations)}`"></div>
      </div>
    </div>
    <div v-else class="loading-stats">
      加载统计数据中...
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  stats: Object
});

const calculateRatio = (part, total) => {
  if (!total) return 0;
  return Math.min(part / total, 1);
};
</script>

<style scoped>
.loading-stats {
  padding: 40px;
  text-align: center;
  color: var(--text-muted);
}
</style>
