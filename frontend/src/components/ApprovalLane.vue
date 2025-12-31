<template>
  <div class="card admin-only">
    <div class="card-header">
      <div>
        <p class="card-kicker">审批通道</p>
        <h2>优先级审阅</h2>
      </div>
      <span class="chip chip-accent">校内优先</span>
    </div>
    <div class="approval-list">
      <div class="approval-item">
        <div>
          <h3>学生 - 纳米实验室</h3>
          <p>需要导师审批</p>
        </div>
        <div class="chip-row">
          <span class="chip chip-warn">剩余 2 小时</span>
          <span class="chip chip-neutral">冲突风险</span>
        </div>
      </div>
      <div class="approval-item">
        <div>
          <h3>校外 - 产业合作</h3>
          <p>待缴费确认</p>
        </div>
        <div class="chip-row">
          <span class="chip chip-alert">支付核验</span>
        </div>
      </div>
      <div class="approval-item">
        <div>
          <h3>教师 - 生物实验室</h3>
          <p>管理员审批中</p>
        </div>
        <div class="chip-row">
          <span class="chip chip-good">无冲突</span>
        </div>
      </div>
    </div>
  </div>
</template>
