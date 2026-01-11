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
