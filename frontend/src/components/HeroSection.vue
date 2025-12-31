<template>
  <section class="hero" data-animate style="--delay: 0.05s">
    <div class="hero-text">
      <p class="eyebrow">预约智能中心</p>
      <h1>共享设备的精确排程。</h1>
      <p class="lead">
        在一条时间轴里追踪可用性、审批与缴费进度。工作人员保持校内流程顺滑，
        借用人员随时掌握状态。
      </p>
      <div class="hero-actions">
        <button type="button" class="primary">发起预约</button>
        <button type="button" class="ghost">查看我的队列</button>
      </div>
      <div class="ribbon">
        <span class="ribbon-step active">提交</span>
        <span class="ribbon-step">冲突校验</span>
        <span class="ribbon-step">审批链</span>
        <span class="ribbon-step">缴费</span>
        <span class="ribbon-step">最终确认</span>
        <span class="ribbon-step">借出</span>
      </div>
    </div>
    <div class="hero-panel">
      <div class="panel-card">
        <div class="panel-title">实时可用</div>
        <div class="panel-value">128 / 20000</div>
        <div class="panel-caption">未来 48 小时可用设备</div>
        <div class="signal-grid">
          <span class="signal good"></span>
          <span class="signal good"></span>
          <span class="signal warn"></span>
          <span class="signal warn"></span>
          <span class="signal alert"></span>
          <span class="signal good"></span>
          <span class="signal good"></span>
          <span class="signal warn"></span>
          <span class="signal good"></span>
        </div>
      </div>
      <div class="panel-card">
        <div class="panel-title">审批队列</div>
        <div class="panel-value">待办 17 条</div>
        <div class="panel-caption">学生 - 导师环节：6</div>
        <div class="chip-row">
          <span class="chip chip-neutral">校内优先</span>
          <span class="chip chip-accent">校外缴费核对</span>
        </div>
      </div>
    </div>
  </section>
</template>
