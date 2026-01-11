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
          {{ roleCaption }}
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
  borrowerRole: {
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

const headNav = [
  { key: "dashboard", label: "总览" },
  { key: "approvals", label: "审批" },
  { key: "staff", label: "员工管理" },
  { key: "procurement", label: "设备采购/报废" },
  { key: "system-config", label: "系统配置" },
  { key: "reports", label: "报表" },
];

const navItems = computed(() => {
  if (props.roleType === "admin") return adminNav;
  if (props.roleType === "head") return headNav;
  if (props.borrowerRole === "teacher") {
    return [
      ...borrowerNav.slice(0, 4),
      { key: "students", label: "学生管理" },
      ...borrowerNav.slice(4),
    ];
  }
  return borrowerNav;
});

const roleCaption = computed(() => {
  if (props.roleType === "borrower") {
    if (props.borrowerRole === "teacher") return "借用人员 · 教师";
    if (props.borrowerRole === "student") return "借用人员 · 学生";
    if (props.borrowerRole === "external") return "借用人员 · 校外";
    return "借用人员";
  }
  if (props.roleType === "head") return "负责人视图";
  return "管理员视图";
});
</script>
