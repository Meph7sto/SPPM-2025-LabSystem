<template>
  <aside class="rail">
    <div class="brand">
      <div class="brand-mark">LESMS</div>
      <div class="brand-sub">实验设备服务</div>
    </div>
    <nav class="rail-nav">
      <button
        v-for="item in navItems"
        :key="item.key"
        type="button"
        class="rail-link"
        :class="{ active: item.key === activePage, muted: item.disabled }"
        :disabled="item.disabled"
        @click="$emit('navigate', item.key)"
      >
        {{ item.label }}
      </button>
    </nav>
    <div class="rail-meta">
      <div class="meta-block">
        <div class="meta-title">系统脉搏</div>
        <div class="meta-value">稳定 · 2 条提醒</div>
        <div class="meta-caption">{{ timestamp || "更新中" }}</div>
      </div>
      <div class="meta-block">
        <div class="meta-title">当前身份</div>
        <div class="meta-value">{{ roleLabel || "未登录" }}</div>
        <div class="meta-caption">
          {{ roleType === "admin" ? "工作人员" : "借用人员" }}
        </div>
      </div>
      <div class="rail-footer">
        <div class="footer-label">下次审计</div>
        <div class="footer-value">12 天</div>
      </div>
      <button type="button" class="ghost rail-exit" @click="$emit('exit')">
        返回登录
      </button>
    </div>
  </aside>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  roleType: {
    type: String,
    required: true,
  },
  roleLabel: {
    type: String,
    default: "",
  },
  timestamp: {
    type: String,
    default: "",
  },
  activePage: {
    type: String,
    default: "dashboard",
  },
});

defineEmits(["exit", "navigate"]);

const borrowerNav = [
  { key: "dashboard", label: "总览" },
  { key: "availability", label: "可用性" },
  { key: "reservation", label: "预约申请" },
  { key: "my-reservations", label: "我的预约" },
  { key: "profile", label: "个人资料" },
  { key: "notifications", label: "通知" },
  { key: "reports", label: "报表" },
];

const adminNav = [
  { key: "dashboard", label: "总览" },
  { key: "approvals", label: "审批" },
  { key: "availability", label: "可用性" },
  { key: "ledger", label: "台账" },
  { key: "payments", label: "缴费核验" },
  { key: "reports", label: "报表" },
];

const navItems = computed(() =>
  props.roleType === "admin" ? adminNav : borrowerNav
);
</script>
