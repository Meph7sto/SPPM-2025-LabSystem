<template>
  <div class="card">
    <div class="card-header">
      <div>
        <p class="card-kicker">通知</p>
        <h2>系统提醒</h2>
      </div>
      <span class="chip" :class="unreadCount ? 'chip-alert' : 'chip-neutral'">
        {{ unreadCount ? `${unreadCount} 条新消息` : "暂无未读" }}
      </span>
    </div>
    <div class="notice-list">
      <div v-if="loading" class="notice-item">
        <div class="notice-dot"></div>
        <div>
          <h3>加载中...</h3>
          <p>请稍候</p>
        </div>
      </div>
      <div v-else-if="!items.length" class="notice-item">
        <div class="notice-dot muted"></div>
        <div>
          <h3>暂无通知</h3>
          <p>完成操作后会收到站内提醒</p>
        </div>
      </div>
      <div
        v-else
        v-for="item in items"
        :key="item.id"
        class="notice-item"
      >
        <div class="notice-dot" :class="{ muted: item.is_read }"></div>
        <div>
          <h3>{{ item.title }}</h3>
          <p>{{ item.content }}</p>
          <small style="color:#6b7280;">{{ formatType(item.type) }}</small>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  items: {
    type: Array,
    default: () => [],
  },
  loading: {
    type: Boolean,
    default: false,
  },
  unreadCount: {
    type: Number,
    default: 0,
  },
});

const formatType = (type) => {
  const map = {
    submit_success: "提交成功",
    approval_result: "审批结果",
    payment_confirmed: "缴费确认",
  };
  return map[type] || type;
};
</script>
