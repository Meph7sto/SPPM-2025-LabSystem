<template>
  <main class="canvas">
    <section class="page-header" data-animate style="--delay: 0.05s">
      <div>
        <p class="eyebrow">通知中心</p>
        <h1>系统提醒与消息</h1>
        <p class="lead">
          覆盖预约提交、审批结果、缴费确认、撤销退款与报表生成等关键节点。
        </p>
      </div>
      <div class="page-actions">
        <button type="button" class="ghost">全部已读</button>
        <button type="button" class="primary">通知设置</button>
      </div>
    </section>

    <section class="grid" data-animate style="--delay: 0.12s">
      <NotificationsSection />
      <div class="card">
        <div class="card-header">
          <div>
            <p class="card-kicker">触发点</p>
            <h2>提醒覆盖</h2>
          </div>
          <span class="chip chip-neutral">已启用</span>
        </div>
        <div class="rule-list">
          <div class="rule-item">
            <span class="rule-title">提交申请</span>
            <span class="rule-desc">申请成功后发送站内通知</span>
          </div>
          <div class="rule-item">
            <span class="rule-title">审批结果</span>
            <span class="rule-desc">通过 / 驳回 / 补充材料同步提醒</span>
          </div>
          <div class="rule-item">
            <span class="rule-title">缴费确认</span>
            <span class="rule-desc">财务同步结果即时提醒</span>
          </div>
        </div>
      </div>
    </section>
  </main>
</template>

<script setup>
import NotificationsSection from "./NotificationsSection.vue";
</script>
