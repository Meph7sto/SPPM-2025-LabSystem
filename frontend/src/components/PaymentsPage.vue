<template>
  <main class="canvas">
    <section class="page-header" data-animate style="--delay: 0.05s">
      <div>
        <p class="eyebrow">缴费核验</p>
        <h1>校外缴费确认</h1>
        <p class="lead">
          财务系统回传支付结果后，管理员执行最终确认才能进入可借出状态。
        </p>
      </div>
      <div class="page-actions">
        <button type="button" class="ghost">同步财务</button>
        <button type="button" class="primary">批量确认</button>
      </div>
    </section>

    <section class="grid" data-animate style="--delay: 0.12s">
      <div class="card">
        <div class="card-header">
          <div>
            <p class="card-kicker">缴费订单</p>
            <h2>待确认清单</h2>
          </div>
          <span class="chip chip-neutral">{{ payments.length }} 条</span>
        </div>
        <div class="payment-queue">
          <div v-for="item in payments" :key="item.id" class="payment-row">
            <div>
              <h3>{{ item.id }}</h3>
              <p>{{ item.detail }}</p>
            </div>
            <div class="chip-row">
              <span class="chip" :class="statusClass(item.status)">
                {{ item.status }}
              </span>
              <span class="chip chip-neutral">￥{{ item.amount }}</span>
            </div>
            <div class="payment-actions">
              <button
                type="button"
                class="primary"
                :disabled="item.status !== '待确认'"
                @click="confirmPayment(item.id)"
              >
                确认收款
              </button>
              <button type="button" class="ghost">查看详情</button>
            </div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <div>
            <p class="card-kicker">退款处理</p>
            <h2>退款规则</h2>
          </div>
          <span class="chip chip-alert">95% 规则</span>
        </div>
        <div class="rule-list">
          <div class="rule-item">
            <span class="rule-title">退款比例</span>
            <span class="rule-desc">校外付费仅退还原费用 95%</span>
          </div>
          <div class="rule-item">
            <span class="rule-title">撤销提前期</span>
            <span class="rule-desc">已批准预约撤销需提前 1 天</span>
          </div>
          <div class="rule-item">
            <span class="rule-title">财务同步</span>
            <span class="rule-desc">退款记录需对接财务系统</span>
          </div>
        </div>
      </div>
    </section>

    <section class="grid" data-animate style="--delay: 0.2s">
      <div class="card wide">
        <div class="card-header">
          <div>
            <p class="card-kicker">最终确认</p>
            <h2>可借出队列</h2>
          </div>
          <span class="chip chip-good">{{ finalConfirmations.length }} 条</span>
        </div>
        <div class="approval-queue">
          <div
            v-for="item in finalConfirmations"
            :key="item.id"
            class="approval-card"
          >
            <div>
              <h3>{{ item.title }}</h3>
              <p>{{ item.detail }}</p>
              <div class="chip-row">
                <span class="chip chip-good">缴费成功</span>
                <span class="chip chip-neutral">{{ item.id }}</span>
              </div>
            </div>
            <div class="approval-actions">
              <button type="button" class="primary" @click="finalize(item.id)">
                最终确认
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

const payments = ref([
  {
    id: "F-2210",
    detail: "校外 · 产业合作 · C-118 光学平台",
    amount: 5400,
    status: "待确认",
  },
  {
    id: "F-2207",
    detail: "校外 · 新材料企业 · B-203 热分析平台",
    amount: 3200,
    status: "已确认",
  },
  {
    id: "F-2201",
    detail: "校外 · 产业合作 · A-417 光谱仪",
    amount: 2800,
    status: "退款处理中",
  },
]);

const finalConfirmations = ref([
  {
    id: "R-2011",
    title: "校外 · 产业合作",
    detail: "C-118 光学平台 · 4 月 18 日 14:00 - 16:00",
    status: "待确认",
  },
  {
    id: "R-2012",
    title: "校外 · 新材料企业",
    detail: "B-203 热分析平台 · 4 月 19 日 10:00 - 12:00",
    status: "待确认",
  },
]);

const statusClass = (status) => {
  if (status === "待确认") return "chip-warn";
  if (status === "已确认") return "chip-good";
  if (status === "退款处理中") return "chip-alert";
  return "chip-neutral";
};

const confirmPayment = (id) => {
  const target = payments.value.find((item) => item.id === id);
  if (!target) return;
  target.status = "已确认";
};

const finalize = (id) => {
  const target = finalConfirmations.value.find((item) => item.id === id);
  if (!target) return;
  target.status = "已生效";
};
</script>
