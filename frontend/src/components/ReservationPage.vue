<template>
  <main class="canvas">
    <section class="page-header" data-animate style="--delay: 0.05s">
      <div>
        <p class="eyebrow">预约申请</p>
        <h1>提交借用申请</h1>
        <p class="lead">
          选择设备与时段，系统将自动进行冲突检测，并按角色进入对应审批链。
        </p>
      </div>
      <div class="page-actions">
        <button type="button" class="ghost">查看预约规则</button>
        <button type="button" class="primary">保存草稿</button>
      </div>
    </section>

    <section class="grid" data-animate style="--delay: 0.12s">
      <div class="card">
        <div class="card-header">
          <div>
            <p class="card-kicker">表单</p>
            <h2>预约信息</h2>
          </div>
          <span class="chip chip-neutral">草稿</span>
        </div>
        <form class="form" @submit.prevent="handleSubmit">
          <label>
            设备选择
            <select v-model="form.device">
              <option>A-417 光谱仪</option>
              <option>B-203 热分析平台</option>
              <option>C-118 光学平台</option>
              <option>A-512 显微成像系统</option>
            </select>
          </label>
          <label>
            借用日期
            <input type="date" v-model="form.date" />
          </label>
          <label>
            借用时间段
            <select v-model="form.slot">
              <option value="08:00-10:00">08:00 - 10:00</option>
              <option value="10:00-12:00">10:00 - 12:00</option>
              <option value="14:00-16:00">14:00 - 16:00</option>
              <option value="16:00-18:00">16:00 - 18:00</option>
              <option value="20:00-22:00">20:00 - 22:00</option>
            </select>
          </label>
          <label>
            用途说明
            <input type="text" v-model="form.purpose" placeholder="项目编号 / 实验目的" />
          </label>
          <label>
            联系方式
            <input type="text" v-model="form.contact" placeholder="手机 / 邮箱" />
          </label>
          <button type="submit" class="primary">提交申请</button>
          <p v-if="submitted" class="form-hint">
            申请已提交，等待进入审批流程。
          </p>
        </form>
      </div>

      <div class="card">
        <div class="card-header">
          <div>
            <p class="card-kicker">摘要</p>
            <h2>预约预览</h2>
          </div>
          <span class="chip chip-good">冲突检测</span>
        </div>
        <div class="summary-list">
          <div class="summary-row">
            <span>设备</span>
            <strong>{{ form.device }}</strong>
          </div>
          <div class="summary-row">
            <span>日期</span>
            <strong>{{ form.date || "待选择" }}</strong>
          </div>
          <div class="summary-row">
            <span>时段</span>
            <strong>{{ form.slot }}</strong>
          </div>
          <div class="summary-row">
            <span>用途</span>
            <strong>{{ form.purpose || "待填写" }}</strong>
          </div>
        </div>
        <div class="rule-list">
          <div class="rule-item">
            <span class="rule-title">最小粒度</span>
            <span class="rule-desc">借用时段最小 2 小时</span>
          </div>
          <div class="rule-item">
            <span class="rule-title">提前预约</span>
            <span class="rule-desc">必须提前 1-7 天提交</span>
          </div>
          <div class="rule-item">
            <span class="rule-title">校外缴费</span>
            <span class="rule-desc">校外人员需缴费确认后生效</span>
          </div>
        </div>
      </div>
    </section>

    <section class="grid" data-animate style="--delay: 0.2s">
      <div class="card wide">
        <div class="card-header">
          <div>
            <p class="card-kicker">审批链</p>
            <h2>流程节点</h2>
          </div>
          <span class="chip chip-accent">自动匹配</span>
        </div>
        <div class="timeline">
          <div class="timeline-item">
            <div>
              <h3>提交申请</h3>
              <p>填写设备、时段与用途说明</p>
            </div>
            <span class="chip chip-good">完成</span>
          </div>
          <div class="timeline-item">
            <div>
              <h3>冲突校验</h3>
              <p>同设备同时间段不可冲突</p>
            </div>
            <span class="chip chip-neutral">待处理</span>
          </div>
          <div class="timeline-item">
            <div>
              <h3>审批链</h3>
              <p>导师 / 管理员 / 负责人按角色处理</p>
            </div>
            <span class="chip chip-neutral">待处理</span>
          </div>
        </div>
      </div>
    </section>
  </main>
</template>

<script setup>
import { reactive, ref } from "vue";

const form = reactive({
  device: "A-417 光谱仪",
  date: "",
  slot: "08:00-10:00",
  purpose: "",
  contact: "",
});

const submitted = ref(false);

const handleSubmit = () => {
  submitted.value = true;
  setTimeout(() => {
    submitted.value = false;
  }, 2000);
};
</script>
