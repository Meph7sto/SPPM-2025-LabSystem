<template>
  <main class="canvas">
    <section class="page-header" data-animate style="--delay: 0.05s">
      <div>
        <p class="eyebrow">报表中心</p>
        <h1>周报 · 月报 · 年报</h1>
        <p class="lead">
          支持历史报表查询与导出，可通过定时任务自动生成。
        </p>
      </div>
      <div class="page-actions">
        <div class="dropdown">
          <button type="button" class="ghost" @click="showTriggerMenu = !showTriggerMenu">
            补生成报表
            <i class="icon-chevron-down"></i>
          </button>
          <div v-if="showTriggerMenu" class="dropdown-menu">
            <a href="#" @click.prevent="triggerReport('weekly')">本周报表</a>
            <a href="#" @click.prevent="triggerReport('monthly')">本月报表</a>
            <a href="#" @click.prevent="triggerReport('yearly')">本年报表</a>
          </div>
        </div>
        <button type="button" class="primary" @click="exportImmediate('weekly')">即时导出周报</button>
      </div>
    </section>

    <section class="grid" data-animate style="--delay: 0.12s">
      <ReportsSection :stats="summaryStats" />
      <div class="card">
        <div class="card-header">
          <div>
            <p class="card-kicker">历史报表</p>
            <h2>最近生成</h2>
          </div>
          <span class="chip chip-neutral">自动任务</span>
        </div>
        <div v-if="loading" class="loading-state">
          加载中...
        </div>
        <div v-else-if="generatedReports.length === 0" class="empty-state">
          暂无已生成的报表
        </div>
        <div v-else class="report-list">
          <div v-for="report in generatedReports" :key="report.id" class="report-item">
            <div>
              <h3>{{ formatReportTitle(report) }}</h3>
              <p>生成时间: {{ formatDate(report.created_at) }}</p>
            </div>
            <button type="button" class="ghost" @click="downloadReport(report)">下载</button>
          </div>
        </div>
      </div>
      <ReportDesignCard />
    </section>
  </main>
</template>

<script setup>
import { ref, onMounted } from "vue";
import ReportsSection from "./ReportsSection.vue";
import ReportDesignCard from "./ReportDesignCard.vue";
import { reportAPI } from "../api";

const loading = ref(true);
const summaryStats = ref(null);
const generatedReports = ref([]);
const showTriggerMenu = ref(false);

const fetchData = async () => {
  try {
    loading.value = true;
    const [summary, reports] = await Promise.all([
      reportAPI.summary(),
      reportAPI.listGenerated()
    ]);
    const summaryData = summary?.data ?? summary;
    const reportsData = reports?.data ?? reports;
    summaryStats.value = summaryData;
    generatedReports.value = Array.isArray(reportsData) ? reportsData : [];
  } catch (error) {
    console.error("Failed to fetch reports:", error);
    alert(error.message);
  } finally {
    loading.value = false;
  }
};

const formatReportTitle = (report) => {
  const typeMap = {
    weekly: "周报",
    monthly: "月报",
    yearly: "年报"
  };
  return `${report.filename.split('_')[1] || ''} ${typeMap[report.report_type] || '报表'}`;
};

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleString();
};

const downloadReport = async (report) => {
  try {
    const blob = await reportAPI.downloadGenerated(report.id);
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", report.filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  } catch (error) {
    alert("下载失败: " + error.message);
  }
};

const triggerReport = async (type) => {
  try {
    showTriggerMenu.value = false;
    await reportAPI.trigger(type);
    alert("报表生成任务已提交");
    await fetchData();
  } catch (error) {
    alert("生成失败: " + error.message);
  }
};

const exportImmediate = async (type) => {
  try {
    const blob = await reportAPI.exportExcel(type);
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `immediate_${type}_report.xlsx`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  } catch (error) {
    alert("导出失败: " + error.message);
  }
};

onMounted(fetchData);
</script>

<style scoped>
.dropdown {
  position: relative;
  display: inline-block;
}

.dropdown-menu {
  position: absolute;
  right: 0;
  top: 100%;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
  z-index: 100;
  min-width: 160px;
  padding: 8px 0;
  margin-top: 8px;
  border: 1px solid var(--border);
}

.dropdown-menu a {
  display: block;
  padding: 10px 16px;
  color: var(--text-main);
  text-decoration: none;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.dropdown-menu a:hover {
  background: var(--bg-surface);
  color: var(--accent);
}

.loading-state, .empty-state {
  padding: 40px;
  text-align: center;
  color: var(--text-muted);
}
</style>
