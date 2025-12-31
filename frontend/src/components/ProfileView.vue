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
        <button type="button" class="ghost">查看我的预约</button>
        <button type="button" class="primary" @click="handleSave">保存修改</button>
      </div>
    </section>

    <section class="grid" data-animate style="--delay: 0.12s">
      <div class="card">
        <div class="card-header">
          <div>
            <p class="card-kicker">基础信息</p>
            <h2>身份资料</h2>
          </div>
          <span class="chip chip-neutral">{{ profile.role }}</span>
        </div>
        <form class="form">
          <label>
            姓名
            <input type="text" v-model="profile.name" />
          </label>
          <label>
            学号 / 工号
            <input type="text" v-model="profile.staffNo" />
          </label>
          <label>
            学院 / 单位
            <input type="text" v-model="profile.college" />
          </label>
          <label>
            指导教师
            <input type="text" v-model="profile.advisor" />
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
            手机号
            <input type="text" v-model="profile.phone" />
          </label>
          <label>
            邮箱
            <input type="text" v-model="profile.email" />
          </label>
          <label>
            紧急联系人
            <input type="text" v-model="profile.emergency" />
          </label>
          <label>
            备注
            <input type="text" v-model="profile.notes" />
          </label>
        </form>
        <p v-if="saved" class="form-hint">资料已保存。</p>
      </div>
    </section>

    <section class="grid" data-animate style="--delay: 0.2s">
      <div class="card wide">
        <div class="card-header">
          <div>
            <p class="card-kicker">借用资格</p>
            <h2>状态概览</h2>
          </div>
          <span class="chip chip-good">可借用</span>
        </div>
        <div class="stat-grid">
          <div class="stat-card">
            <p class="stat-label">导师审核</p>
            <p class="stat-value">已通过</p>
            <p class="stat-meta">更新于 2 天前</p>
          </div>
          <div class="stat-card">
            <p class="stat-label">违规记录</p>
            <p class="stat-value">0 次</p>
            <p class="stat-meta">最近 12 个月</p>
          </div>
          <div class="stat-card">
            <p class="stat-label">可用额度</p>
            <p class="stat-value">12 小时</p>
            <p class="stat-meta">当前预约周期</p>
          </div>
        </div>
      </div>
    </section>
  </main>
</template>

<script setup>
import { reactive, ref } from "vue";

const profile = reactive({
  name: "王晓宁",
  role: "校内学生",
  staffNo: "S20251234",
  college: "材料学院",
  advisor: "T-0912",
  phone: "138-0000-1234",
  email: "wangxn@jiangnan.edu.cn",
  emergency: "李老师 139-8888-5678",
  notes: "可安排夜间借用",
});

const saved = ref(false);

const handleSave = () => {
  saved.value = true;
  setTimeout(() => {
    saved.value = false;
  }, 2000);
};
</script>
