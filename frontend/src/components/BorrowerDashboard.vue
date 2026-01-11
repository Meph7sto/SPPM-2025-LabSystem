<template>
  <main class="canvas">
    <HeroSection />
    <section class="grid" data-animate style="--delay: 0.12s">
      <AvailabilityMatrix />
      <QuickReservation />
    </section>
    <section class="grid" data-animate style="--delay: 0.18s">
      <TimelineSection />
    </section>
    <section class="grid" data-animate style="--delay: 0.24s">
      <NotificationsSection />
    </section>
    <section class="grid" data-animate style="--delay: 0.3s">
      <ReportsSection />
    </section>
  </main>
</template>

<script setup>
import HeroSection from "./HeroSection.vue";
import AvailabilityMatrix from "./AvailabilityMatrix.vue";
import QuickReservation from "./QuickReservation.vue";
import TimelineSection from "./TimelineSection.vue";
import NotificationsSection from "./NotificationsSection.vue";
import ReportsSection from "./ReportsSection.vue";
</script>
