<template>
  <div class="login-shell">
    <div class="login-card" data-animate style="--delay: 0.05s">
      <div class="login-header">
        <div>
          <p class="eyebrow">江南大学实验室设备管理系统</p>
          <h1>统一入口 · 全角色协同</h1>
          <p class="lead">
            借用人员、管理员与负责人共用同一入口。选择角色后进入对应流程，
            审批链与缴费规则自动匹配。
          </p>
        </div>
        <div class="login-brand">
          <span class="login-mark">LESMS</span>
          <span class="login-sub">Lab Equipment Service</span>
        </div>
      </div>
      <div class="login-grid">
        <section class="login-panel">
          <h2>选择角色</h2>
          <p class="login-caption">已预设所有角色与流程入口</p>
          <div class="role-grid">
            <button
              v-for="role in roles"
              :key="role.value"
              type="button"
              class="role-card"
              :class="{ active: selectedRole === role.value }"
              :aria-pressed="selectedRole === role.value ? 'true' : 'false'"
              @click="selectedRole = role.value"
            >
              <div>
                <h3>{{ role.title }}</h3>
                <p>{{ role.desc }}</p>
              </div>
              <span class="chip chip-neutral">{{ role.tag }}</span>
            </button>
          </div>
        </section>
        <form class="login-form" @submit.prevent="handleEnter">
          <div class="login-field">
            <label for="account">账号</label>
            <input id="account" type="text" placeholder="工号 / 学号 / 手机号" />
          </div>
          <div class="login-field">
            <label for="password">密码</label>
            <input id="password" type="password" placeholder="请输入密码" />
          </div>
          <div class="login-field">
            <label for="role">当前角色</label>
            <select id="role" v-model="selectedRole">
              <option v-for="role in roles" :key="role.value" :value="role.value">
                {{ role.title }}
              </option>
            </select>
          </div>
          <div class="login-actions">
            <button type="submit" class="primary">进入系统</button>
            <button type="button" class="ghost">找回密码</button>
            <button type="button" class="ghost" @click="handleRegister">
              注册账号
            </button>
          </div>
          <div class="login-hint">
            提示：借用人员需提前 1-7 天预约，校外借用需缴费确认后生效。
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from "vue";

const props = defineProps({
  defaultRole: {
    type: String,
    default: "",
  },
});

const roles = [
  {
    value: "teacher",
    title: "校内教师",
    desc: "申请由设备管理员审批",
    tag: "借用人员",
  },
  {
    value: "student",
    title: "校内学生",
    desc: "导师审批 → 管理员审批",
    tag: "借用人员",
  },
  {
    value: "external",
    title: "校外人员",
    desc: "管理员初审 → 负责人审批 → 缴费",
    tag: "借用人员",
  },
  {
    value: "admin",
    title: "设备管理员",
    desc: "台账维护与审批流转",
    tag: "工作人员",
  },
  {
    value: "head",
    title: "实验室负责人",
    desc: "校外终审与报表监管",
    tag: "工作人员",
  },
];

const selectedRole = ref(props.defaultRole || roles[0].value);

const emit = defineEmits(["enter", "register"]);

const handleEnter = () => {
  emit("enter", selectedRole.value);
};

const handleRegister = () => {
  emit("register", selectedRole.value);
};

watch(
  () => props.defaultRole,
  (value) => {
    if (value) {
      selectedRole.value = value;
    }
  }
);
</script>
