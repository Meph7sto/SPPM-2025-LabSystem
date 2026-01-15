<template>
  <main class="canvas">
    <HeroSection />
    <section class="grid" data-animate style="--delay: 0.12s">
      <AvailabilityMatrix />
      <ApprovalLane />
    </section>
    <section class="grid" data-animate style="--delay: 0.18s">
      <LedgerSection />
      <NotificationsSection />
    </section>
    <section class="grid" data-animate style="--delay: 0.3s">
      <ReportsSection />
      <PaymentValidation />
    </section>
    <section class="grid" data-animate style="--delay: 0.36s">
      <div class="card wide">
        <div class="card-header">
          <div>
            <p class="card-kicker">NFR-6</p>
            <h2>局域网访问限制</h2>
          </div>
          <span class="chip chip-neutral">模拟</span>
        </div>
        <form class="form">
          <label>
            来源 IP / 反代标识
            <input type="text" placeholder="例如：10.1.20.33 或 X-Forwarded-For" />
          </label>
          <p class="form-hint">仅做白名单校验入口的界面模拟，实际限制由网关或配置中心统一下发。</p>
        </form>
      </div>
    </section>
  </main>
</template>

<script setup>
import HeroSection from "./HeroSection.vue";
import AvailabilityMatrix from "./AvailabilityMatrix.vue";
import ApprovalLane from "./ApprovalLane.vue";
import LedgerSection from "./LedgerSection.vue";
import NotificationsSection from "./NotificationsSection.vue";
import ReportsSection from "./ReportsSection.vue";
import PaymentValidation from "./PaymentValidation.vue";
</script>
