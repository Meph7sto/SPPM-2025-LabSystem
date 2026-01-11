<template>
  <div class="card admin-only">
    <div class="card-header">
      <div>
        <p class="card-kicker">缴费核验</p>
        <h2>校外缴费核对</h2>
      </div>
      <span class="chip chip-accent">财务同步</span>
    </div>
    <div class="payment-list">
      <div class="payment-item">
        <div>
          <h3>订单 F-2210</h3>
          <p>等待财务确认</p>
        </div>
        <span class="chip chip-neutral">待确认</span>
      </div>
      <div class="payment-item">
        <div>
          <h3>订单 F-2207</h3>
          <p>校外费用已支付</p>
        </div>
        <span class="chip chip-good">已确认</span>
      </div>
      <div class="payment-item">
        <div>
          <h3>订单 F-2201</h3>
          <p>退款计算</p>
        </div>
        <span class="chip chip-warn">95% 规则</span>
      </div>
    </div>
  </div>
</template>
