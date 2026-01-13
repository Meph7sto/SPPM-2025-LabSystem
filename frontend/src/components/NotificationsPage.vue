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
        <button type="button" class="ghost" :disabled="loading || !unreadCount" @click="handleMarkAllRead">
          全部已读
        </button>
        <button type="button" class="primary" @click="fetchNotifications" :disabled="loading">
          刷新
        </button>
      </div>
    </section>

    <section class="grid" data-animate style="--delay: 0.12s">
      <NotificationsSection
        :items="notifications"
        :loading="loading"
        :unread-count="unreadCount"
      />
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
import { computed, onMounted, ref } from "vue";
import NotificationsSection from "./NotificationsSection.vue";
import { notificationAPI } from "../api";

const notifications = ref([]);
const loading = ref(false);

const emitUpdated = () => {
  window.dispatchEvent(new Event("notifications-updated"));
};

const fetchNotifications = async () => {
  loading.value = true;
  try {
    const res = await notificationAPI.list({ limit: 20 });
    notifications.value = res.data?.items || [];
    emitUpdated();
  } catch (error) {
    console.error("Failed to fetch notifications", error);
  } finally {
    loading.value = false;
  }
};

const unreadCount = computed(() => notifications.value.filter(item => !item.is_read).length);

const handleMarkAllRead = async () => {
  if (!notifications.value.length) return;
  try {
    await notificationAPI.markAllRead();
    await fetchNotifications();
    emitUpdated();
  } catch (error) {
    console.error("Failed to mark all as read", error);
  }
};

onMounted(() => {
  fetchNotifications();
});
</script>
