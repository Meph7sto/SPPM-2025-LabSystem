<template>
  <div class="login-shell">
    <div class="login-card" data-animate style="--delay: 0.05s">
      <div class="login-header">
        <div>
          <p class="eyebrow">注册</p>
          <h1>借用人员账号创建</h1>
          <p class="lead">
            仅借用人员需要注册账号。角色不同，需填写的信息也不同。
            提交后可回到登录入口继续流程。
          </p>
        </div>
        <div class="login-brand">
          <span class="login-mark">LESMS</span>
          <span class="login-sub">Create Account</span>
        </div>
      </div>
      <div class="login-grid">
        <section class="login-panel">
          <h2>注册说明</h2>
          <p class="login-caption">遵循借用规则与校内优先策略</p>
          <div class="rule-list">
            <div class="rule-item">
              <span class="rule-title">预约提前期</span>
              <span class="rule-desc">必须提前 1-7 天提交预约</span>
            </div>
            <div class="rule-item">
              <span class="rule-title">时间粒度</span>
              <span class="rule-desc">最小 2 小时，按时段管理</span>
            </div>
            <div class="rule-item">
              <span class="rule-title">校外缴费</span>
              <span class="rule-desc">校外借用需先缴费后确认</span>
            </div>
          </div>
          <button type="button" class="ghost" @click="$emit('back')">
            返回登录
          </button>
        </section>
        <form class="login-form" @submit.prevent="handleRegister">
          <div class="login-field">
            <label for="register-role">借用人员类型</label>
            <select id="register-role" v-model="form.role">
              <option value="teacher">校内教师</option>
              <option value="student">校内学生</option>
              <option value="external">校外人员</option>
            </select>
          </div>
          <div class="login-field">
            <label for="register-name">姓名</label>
            <input id="register-name" v-model="form.name" type="text" placeholder="请输入姓名" />
          </div>
          <div class="login-field">
            <label for="register-contact">联系方式</label>
            <input
              id="register-contact"
              v-model="form.contact"
              type="text"
              placeholder="手机号 / 邮箱"
            />
          </div>
          <div class="login-field" v-if="form.role !== 'external'">
            <label for="register-college">学院 / 单位</label>
            <input
              id="register-college"
              v-model="form.college"
              type="text"
              placeholder="例如：材料学院"
            />
          </div>
          <div class="login-field" v-if="form.role === 'teacher'">
            <label for="register-teacher-id">教师编号</label>
            <input
              id="register-teacher-id"
              v-model="form.teacherNo"
              type="text"
              placeholder="工号"
            />
          </div>
          <div class="login-field" v-if="form.role === 'student'">
            <label for="register-student-id">学生学号</label>
            <input
              id="register-student-id"
              v-model="form.studentNo"
              type="text"
              placeholder="学号"
            />
          </div>
          <div class="login-field" v-if="form.role === 'student'">
            <label for="register-advisor">指导教师编号</label>
            <input
              id="register-advisor"
              v-model="form.advisorNo"
              type="text"
              placeholder="导师工号"
            />
          </div>
          <div class="login-field" v-if="form.role === 'external'">
            <label for="register-org">单位名称</label>
            <input
              id="register-org"
              v-model="form.orgName"
              type="text"
              placeholder="公司 / 机构"
            />
          </div>
          <div class="login-field">
            <label for="register-password">设置密码</label>
            <input
              id="register-password"
              v-model="form.password"
              type="password"
              placeholder="至少 8 位"
            />
          </div>
          <div class="login-actions">
            <button type="submit" class="primary">提交注册</button>
            <button type="button" class="ghost" @click="$emit('back')">
              取消
            </button>
          </div>
          <div class="login-hint">
            注册完成后需通过管理员核验身份信息，方可发起预约。
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive } from "vue";

const props = defineProps({
  defaultRole: {
    type: String,
    default: "",
  },
});

const emit = defineEmits(["registered", "back"]);

const form = reactive({
  role: props.defaultRole || "student",
  name: "",
  contact: "",
  college: "",
  teacherNo: "",
  studentNo: "",
  advisorNo: "",
  orgName: "",
  password: "",
});

const handleRegister = () => {
  emit("registered", form.role);
};
</script>
