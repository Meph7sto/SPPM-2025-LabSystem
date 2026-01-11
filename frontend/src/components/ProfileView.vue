<template>
  <main class="canvas">
    <section class="page-header" data-animate style="--delay: 0.05s">
      <div>
        <p class="eyebrow">个人资料</p>
        <h1>账号信息维护</h1>
        <p class="lead">
          可更新联系方式与学院信息，系统会在提交预约时校验身份与导师关系。
        </p>
      </div>
      <div class="page-actions">
        <button type="button" class="ghost" @click="goToMyReservations">查看我的预约</button>
        <button type="button" class="primary" @click="handleSave" :disabled="saving">
          {{ saving ? '保存中...' : '保存修改' }}
        </button>
      </div>
    </section>

    <section class="grid" data-animate style="--delay: 0.12s">
      <div class="card">
        <div class="card-header">
          <div>
            <p class="card-kicker">基础信息</p>
            <h2>身份资料</h2>
          </div>
          <span class="chip chip-neutral">{{ getRoleLabel() }}</span>
        </div>
        <form class="form">
          <label>
            姓名
            <input type="text" v-model="profile.name" />
          </label>
          <label>
            学号 / 工号
            <input type="text" :value="getStaffNo()" disabled />
          </label>
          <label v-if="profile.borrower_type !== 'external'">
            学院 / 单位
            <input type="text" v-model="profile.college" />
          </label>
          <label v-if="profile.borrower_type === 'student'">
            指导教师工号
            <input type="text" :value="profile.advisor_no || '未设置'" disabled />
          </label>
          <label v-if="profile.borrower_type === 'external'">
            单位名称
            <input type="text" v-model="profile.org_name" />
          </label>
        </form>
      </div>

      <div class="card">
        <div class="card-header">
          <div>
            <p class="card-kicker">联系方式</p>
            <h2>联系信息</h2>
          </div>
          <span class="chip chip-good">已绑定</span>
        </div>
        <form class="form">
          <label>
            联系方式
            <input type="text" v-model="profile.contact" />
          </label>
          <label>
            账号
            <input type="text" :value="profile.account" disabled />
          </label>
        </form>
        <p v-if="message" :class="['form-hint', messageType]">{{ message }}</p>
      </div>
    </section>

    <section class="grid" data-animate style="--delay: 0.2s">
      <div class="card wide">
        <div class="card-header">
          <div>
            <p class="card-kicker">借用资格</p>
            <h2>状态概览</h2>
          </div>
          <span :class="['chip', profile.is_active ? 'chip-good' : 'chip-warn']">
            {{ profile.is_active ? '可借用' : '未激活' }}
          </span>
        </div>
        <div class="stat-grid">
          <div class="stat-card" v-if="profile.borrower_type === 'student'">
            <p class="stat-label">导师审核</p>
            <p class="stat-value">{{ profile.advisor_no ? '已关联' : '待关联' }}</p>
            <p class="stat-meta">{{ profile.advisor_no ? `导师工号: ${profile.advisor_no}` : '需要导师工号' }}</p>
          </div>
          <div class="stat-card">
            <p class="stat-label">账号类型</p>
            <p class="stat-value">{{ getRoleLabel() }}</p>
            <p class="stat-meta">{{ profile.borrower_type || profile.role }}</p>
          </div>
          <div class="stat-card">
            <p class="stat-label">注册时间</p>
            <p class="stat-value">{{ formatDate(profile.created_at) }}</p>
            <p class="stat-meta">账号创建日期</p>
          </div>
        </div>
      </div>
    </section>
  </main>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import { userAPI } from "../api.js";

const emit = defineEmits(['navigate']);

const profile = reactive({
  id: 0,
  account: "",
  role: "",
  borrower_type: null,
  name: "",
  contact: "",
  college: null,
  teacher_no: null,
  student_no: null,
  advisor_no: null,
  org_name: null,
  is_active: true,
  created_at: null,
});

const saving = ref(false);
const message = ref("");
const messageType = ref("success");

// 获取角色标签
const getRoleLabel = () => {
  const roleMap = {
    teacher: "校内教师",
    student: "校内学生",
    external: "校外人员",
    admin: "设备管理员",
    head: "实验室负责人",
  };
  return roleMap[profile.borrower_type] || roleMap[profile.role] || "未知";
};

// 获取工号/学号
const getStaffNo = () => {
  return profile.teacher_no || profile.student_no || profile.account;
};

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return "未知";
  const date = new Date(dateStr);
  return new Intl.DateTimeFormat("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(date);
};

// 加载个人资料
const loadProfile = async () => {
  try {
    const response = await userAPI.getProfile();
    if (response.data) {
      Object.assign(profile, response.data);
    }
  } catch (error) {
    console.error("Failed to load profile:", error);
    showMessage("加载个人资料失败", "error");
  }
};

// 保存个人资料
const handleSave = async () => {
  saving.value = true;
  message.value = "";

  try {
    const updateData = {
      name: profile.name,
      contact: profile.contact,
      college: profile.college,
      org_name: profile.org_name,
    };

    const response = await userAPI.updateProfile(updateData);
    if (response.data) {
      Object.assign(profile, response.data);
      showMessage("资料保存成功", "success");
    }
  } catch (error) {
    console.error("Failed to save profile:", error);
    showMessage(error.message || "保存失败，请稍后重试", "error");
  } finally {
    saving.value = false;
  }
};

// 显示消息
const showMessage = (msg, type = "success") => {
  message.value = msg;
  messageType.value = type;
  setTimeout(() => {
    message.value = "";
  }, 3000);
};

// 跳转到我的预约
const goToMyReservations = () => {
  // 触发父组件的导航事件
  window.dispatchEvent(new CustomEvent('navigate-to-reservations'));
};

onMounted(() => {
  loadProfile();
});
</script>

<style scoped>
.form-hint {
  margin-top: 1rem;
  padding: 0.75rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
}

.form-hint.success {
  background: rgba(16, 185, 129, 0.1);
  color: rgb(16, 185, 129);
}

.form-hint.error {
  background: rgba(239, 68, 68, 0.1);
  color: rgb(239, 68, 68);
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>

