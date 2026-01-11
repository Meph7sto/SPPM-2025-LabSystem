<template>
  <main class="canvas">
    <section class="page-header" data-animate style="--delay: 0.05s">
      <div>
        <p class="eyebrow">台账管理</p>
        <h1>设备与人员台账</h1>
        <p class="lead">
          管理员维护设备、教师、学生与校外人员台账，支持审计与导出。
        </p>
      </div>
      <div class="page-actions">
        <button type="button" class="ghost">导入数据</button>
        <button type="button" class="primary">新增台账</button>
      </div>
    </section>

    <section class="grid" data-animate style="--delay: 0.12s">
      <LedgerSection />
      <div class="card">
        <div class="card-header">
          <div>
            <p class="card-kicker">审计</p>
            <h2>最近更新</h2>
          </div>
          <span class="chip chip-neutral">留痕</span>
        </div>
        <div class="report-list">
          <div class="report-item">
            <div>
              <h3>设备 A-417</h3>
              <p>状态更新为检修 · 2025-04-10 09:12</p>
            </div>
            <span class="chip chip-warn">检修</span>
          </div>
          <div class="report-item">
            <div>
              <h3>学生台账</h3>
              <p>新增 28 条记录 · 2025-04-09 18:30</p>
            </div>
            <span class="chip chip-good">已同步</span>
          </div>
          <div class="report-item">
            <div>
              <h3>教师台账</h3>
              <p>导师关系更新 · 2025-04-08 15:22</p>
            </div>
            <span class="chip chip-neutral">完成</span>
          </div>
        </div>
      </div>
    </section>
  </main>
</template>

<script setup>
import LedgerSection from "./LedgerSection.vue";
</script>
