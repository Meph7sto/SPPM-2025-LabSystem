<template>
  <main class="canvas">
    <section class="page-header" data-animate style="--delay: 0.05s">
      <div>
        <p class="eyebrow">审批中心</p>
        <h1>待办审批清单</h1>
        <p class="lead">
          校内申请优先处理，冲突预约需人工决策。支持通过、驳回与退回补充材料。
        </p>
      </div>
      <div class="page-actions">
        <button type="button" class="ghost">刷新队列</button>
        <button type="button" class="primary">批量处理</button>
      </div>
    </section>

    <section class="grid" data-animate style="--delay: 0.12s">
      <div class="card">
        <div class="card-header">
          <div>
            <p class="card-kicker">今日任务</p>
            <h2>审批概览</h2>
          </div>
          <span class="chip chip-accent">校内优先</span>
        </div>
        <div class="stat-grid">
          <div class="stat-card">
            <p class="stat-label">待管理员审批</p>
            <p class="stat-value">8 条</p>
            <p class="stat-meta">含校内 5 条</p>
          </div>
          <div class="stat-card">
            <p class="stat-label">待导师审批</p>
            <p class="stat-value">3 条</p>
            <p class="stat-meta">学生申请</p>
          </div>
          <div class="stat-card">
            <p class="stat-label">待负责人审批</p>
            <p class="stat-value">2 条</p>
            <p class="stat-meta">校外申请</p>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <div>
            <p class="card-kicker">规则提示</p>
            <h2>冲突处理</h2>
          </div>
          <span class="chip chip-warn">必须人工判定</span>
        </div>
        <div class="rule-list">
          <div class="rule-item">
            <span class="rule-title">校内优先</span>
            <span class="rule-desc">同设备冲突时优先处理校内申请</span>
          </div>
          <div class="rule-item">
            <span class="rule-title">退回补充</span>
            <span class="rule-desc">材料不足可退回并备注原因</span>
          </div>
          <div class="rule-item">
            <span class="rule-title">审批留痕</span>
            <span class="rule-desc">审批意见写入轨迹，便于审计</span>
          </div>
        </div>
      </div>
    </section>

    <section class="grid" data-animate style="--delay: 0.2s">
      <div class="card wide">
        <div class="card-header">
          <div>
            <p class="card-kicker">待办</p>
            <h2>审批队列</h2>
          </div>
          <span class="chip chip-neutral">{{ approvals.length }} 条</span>
        </div>
        <div class="approval-queue">
          <div v-for="item in approvals" :key="item.id" class="approval-card">
            <div>
              <h3>{{ item.title }}</h3>
              <p>{{ item.detail }}</p>
              <div class="chip-row">
                <span class="chip" :class="priorityClass(item.priority)">
                  {{ item.priority }}
                </span>
                <span class="chip chip-neutral">{{ item.step }}</span>
                <span v-if="item.conflict" class="chip chip-alert">冲突</span>
              </div>
              <p class="chain-caption">审批链条</p>
              <div class="approval-chain">
                <div
                  v-for="(node, index) in item.chain"
                  :key="`${item.id}-${index}`"
                  class="chain-step"
                  :class="chainClass(node.state)"
                >
                  <span class="chain-label">{{ node.label }}</span>
                  <span class="chain-role">{{ node.role }}</span>
                </div>
              </div>
            </div>
            <div class="approval-actions">
              <button type="button" class="primary" @click="setStatus(item.id, '通过')">
                通过
              </button>
              <button type="button" class="ghost" @click="setStatus(item.id, '退回补充')">
                退回补充
              </button>
              <button type="button" class="danger" @click="setStatus(item.id, '驳回')">
                驳回
              </button>
              <span class="approval-status">{{ item.status }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  </main>
</template>

<script setup>
import { ref } from "vue";

const approvals = ref([
  {
    id: "A-2001",
    title: "学生 · 纳米实验室",
    detail: "A-417 光谱仪 · 4 月 12 日 08:00 - 10:00",
    step: "导师审批",
    priority: "校内优先",
    conflict: true,
    status: "待处理",
    chain: [
      { label: "导师审批", role: "指导教师", state: "current" },
      { label: "管理员审批", role: "设备管理员", state: "pending" },
      { label: "可借出", role: "实验室", state: "pending" },
    ],
  },
  {
    id: "A-2002",
    title: "教师 · 生物实验室",
    detail: "B-203 热分析平台 · 4 月 13 日 10:00 - 12:00",
    step: "管理员审批",
    priority: "校内优先",
    conflict: false,
    status: "待处理",
    chain: [
      { label: "管理员审批", role: "设备管理员", state: "current" },
      { label: "可借出", role: "实验室", state: "pending" },
    ],
  },
  {
    id: "A-2003",
    title: "校外 · 产业合作",
    detail: "C-118 光学平台 · 4 月 15 日 14:00 - 16:00",
    step: "负责人审批",
    priority: "校外缴费",
    conflict: false,
    status: "待处理",
    chain: [
      { label: "管理员初审", role: "设备管理员", state: "done" },
      { label: "负责人审批", role: "实验室负责人", state: "current" },
      { label: "缴费确认", role: "财务系统", state: "pending" },
      { label: "最终确认", role: "设备管理员", state: "pending" },
      { label: "可借出", role: "实验室", state: "pending" },
    ],
  },
]);

const priorityClass = (priority) => {
  if (priority === "校内优先") return "chip-good";
  if (priority === "校外缴费") return "chip-warn";
  return "chip-neutral";
};

const chainClass = (state) => {
  if (state === "done") return "chain-done";
  if (state === "current") return "chain-current";
  return "chain-pending";
};

const setStatus = (id, status) => {
  const target = approvals.value.find((item) => item.id === id);
  if (!target) return;
  target.status = status;
};
</script>
