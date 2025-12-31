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
        <button type="button" class="ghost">补生成报表</button>
        <button type="button" class="primary">导出 PDF</button>
      </div>
    </section>

    <section class="grid" data-animate style="--delay: 0.12s">
      <ReportsSection />
      <div class="card">
        <div class="card-header">
          <div>
            <p class="card-kicker">历史报表</p>
            <h2>最近生成</h2>
          </div>
          <span class="chip chip-neutral">自动任务</span>
        </div>
        <div class="report-list">
          <div class="report-item">
            <div>
              <h3>2025-W14 周报</h3>
              <p>设备使用率、预约量、校外收入</p>
            </div>
            <button type="button" class="ghost">下载</button>
          </div>
          <div class="report-item">
            <div>
              <h3>2025-03 月报</h3>
              <p>借出统计、检修汇总、审批效率</p>
            </div>
            <button type="button" class="ghost">下载</button>
          </div>
          <div class="report-item">
            <div>
              <h3>2024 年报</h3>
              <p>设备利用率、年度收入、重点设备</p>
            </div>
            <button type="button" class="ghost">下载</button>
          </div>
        </div>
      </div>
    </section>
  </main>
</template>

<script setup>
import ReportsSection from "./ReportsSection.vue";
</script>
