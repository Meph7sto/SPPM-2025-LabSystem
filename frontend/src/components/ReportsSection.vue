<template>
  <div class="card wide">
    <div class="card-header">
      <div>
        <p class="card-kicker">报表</p>
        <h2>使用率与财务</h2>
      </div>
      <span class="chip chip-neutral">可导出</span>
    </div>
    <div v-if="activeStats" class="report-grid">
      <div class="report-card">
        <h3>总预约数</h3>
        <p>{{ activeStats.total_reservations }} 次</p>
        <div class="progress-ring" :style="`--value: ${calculateRatio(activeStats.completed, activeStats.total_reservations)}`"></div>
      </div>
      <div class="report-card">
        <h3>已完成预约</h3>
        <p>{{ activeStats.completed }} 次</p>
        <div class="progress-ring" :style="`--value: ${calculateRatio(activeStats.completed, activeStats.total_reservations)}`"></div>
      </div>
      <div class="report-card">
        <h3>校外月度收入</h3>
        <p>¥ {{ activeStats.total_payment.toLocaleString() }}</p>
        <div class="progress-ring" style="--value: 0.61"></div>
      </div>
      <div class="report-card">
        <h3>当前借出中</h3>
        <p>{{ activeStats.borrowed }} 台</p>
        <div class="progress-ring" :style="`--value: ${calculateRatio(activeStats.borrowed, activeStats.total_reservations)}`"></div>
      </div>
    </div>
    <div v-else class="loading-stats">
      {{ errorMessage || "加载统计数据中..." }}
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import { reportAPI } from "../api";

const props = defineProps({
  stats: Object,
  refreshInterval: {
    type: Number,
    default: 30000
  }
});

const localStats = ref(null);
const errorMessage = ref("");
const loading = ref(false);

const shouldAutoFetch = computed(() => props.stats === undefined);
const activeStats = computed(() => (shouldAutoFetch.value ? localStats.value : props.stats));

let refreshTimer = null;

const fetchStats = async () => {
  if (loading.value) return;
  try {
    loading.value = true;
    errorMessage.value = "";
    const response = await reportAPI.summary();
    const data = response?.data ?? response;
    localStats.value = data;
  } catch (error) {
    console.error("Failed to fetch report summary:", error);
    errorMessage.value = "统计数据加载失败";
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  if (!shouldAutoFetch.value) return;
  fetchStats();
  if (props.refreshInterval > 0) {
    refreshTimer = setInterval(fetchStats, props.refreshInterval);
  }
});

onBeforeUnmount(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer);
  }
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
