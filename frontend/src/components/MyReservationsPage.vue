<template>
  <main class="canvas">
    <section class="page-header" data-animate style="--delay: 0.05s">
      <div>
        <p class="eyebrow">我的预约</p>
        <h1>预约状态追踪</h1>
        <p class="lead">
          查看已提交预约，可在未审批或退回补充材料状态下修改并重新提交。
        </p>
      </div>
      <div class="page-actions">
        <button type="button" class="ghost">导出清单</button>
        <button type="button" class="primary">新建预约</button>
      </div>
    </section>

    <section class="grid" data-animate style="--delay: 0.12s">
      <div class="card wide">
        <div class="card-header">
          <div>
            <p class="card-kicker">列表</p>
            <h2>近期预约</h2>
          </div>
          <span class="chip chip-neutral">未来 7 天</span>
        </div>
        <div class="reservation-list">
          <div v-for="item in reservations" :key="item.id" class="reservation-item">
            <div>
              <h3>{{ item.device }}</h3>
              <p>{{ item.slot }} · {{ item.location }}</p>
            </div>
            <div class="chip-row">
              <span class="chip" :class="statusClass(item.status)">
                {{ item.status }}
              </span>
              <span class="chip chip-neutral">{{ item.id }}</span>
            </div>
            <div class="reservation-actions">
              <button
                v-if="showPaymentAction(item.status)"
                type="button"
                class="primary"
                @click="openPayment(item)"
              >
                {{ paymentActionLabel(item.status) }}
              </button>
              <button
                type="button"
                class="ghost"
                :disabled="!canEdit(item.status)"
                @click="startEdit(item)"
              >
                修改
              </button>
              <button
                type="button"
                class="danger"
                :disabled="!canCancel(item.status)"
                @click="cancelReservation(item.id)"
              >
                撤销
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="grid" data-animate style="--delay: 0.2s">
      <div class="card">
        <div class="card-header">
          <div>
            <p class="card-kicker">修改</p>
            <h2>预约调整</h2>
          </div>
          <span class="chip chip-warn">仅限未审批</span>
        </div>
        <div v-if="editing" class="form">
          <label>
            设备
            <input type="text" v-model="editForm.device" />
          </label>
          <label>
            时间段
            <input type="text" v-model="editForm.slot" />
          </label>
          <label>
            用途
            <input type="text" v-model="editForm.purpose" />
          </label>
          <button type="button" class="primary" @click="saveEdit">
            重新提交
          </button>
          <p v-if="editSaved" class="form-hint">已提交修改申请。</p>
        </div>
        <div v-else class="empty-state">
          选择一条“未审批 / 退回补充材料”的预约进行修改。
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <div>
            <p class="card-kicker">撤销规则</p>
            <h2>提示</h2>
          </div>
          <span class="chip chip-alert">至少提前 1 天</span>
        </div>
        <div class="rule-list">
          <div class="rule-item">
            <span class="rule-title">未审批撤销</span>
            <span class="rule-desc">可直接撤销，不进入退款流程</span>
          </div>
          <div class="rule-item">
            <span class="rule-title">已批准撤销</span>
            <span class="rule-desc">需提前 1 天，校外触发退款记录</span>
          </div>
          <div class="rule-item">
            <span class="rule-title">退款规则</span>
            <span class="rule-desc">校外付费仅退 95%</span>
          </div>
        </div>
      </div>
    </section>

    <section
      v-if="isExternal"
      class="grid"
      data-animate
      style="--delay: 0.28s"
    >
      <div class="card">
        <div class="card-header">
          <div>
            <p class="card-kicker">支付订单</p>
            <h2>校外缴费清单</h2>
          </div>
          <span class="chip chip-neutral">{{ paymentOrders.length }} 条</span>
        </div>
        <div class="payment-queue">
          <div v-for="order in paymentOrders" :key="order.id" class="payment-row">
            <div>
              <h3>{{ order.id }}</h3>
              <p>{{ order.detail }}</p>
            </div>
            <div class="chip-row">
              <span class="chip" :class="paymentStatusClass(order.status)">
                {{ order.status }}
              </span>
              <span class="chip chip-neutral">￥{{ order.amount }}</span>
            </div>
            <div class="payment-actions">
              <button
                type="button"
                class="primary"
                :disabled="order.status !== '待支付'"
                @click="payOrder(order.id)"
              >
                去支付
              </button>
              <button type="button" class="ghost" @click="selectOrder(order.id)">
                查看指引
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <div>
            <p class="card-kicker">缴费指引</p>
            <h2>支付步骤</h2>
          </div>
          <span class="chip chip-warn">审批通过后生成</span>
        </div>
        <div class="rule-list">
          <div class="rule-item">
            <span class="rule-title">生成订单</span>
            <span class="rule-desc">管理员审批通过后自动生成缴费单号</span>
          </div>
          <div class="rule-item">
            <span class="rule-title">线下转账</span>
            <span class="rule-desc">凭缴费单号到财务处完成支付</span>
          </div>
          <div class="rule-item">
            <span class="rule-title">结果同步</span>
            <span class="rule-desc">财务回传后进入待最终确认</span>
          </div>
        </div>
        <div v-if="activeOrder" class="payment-detail">
          <div class="summary-list">
            <div class="summary-row">
              <span>缴费单号</span>
              <strong>{{ activeOrder.id }}</strong>
            </div>
            <div class="summary-row">
              <span>关联预约</span>
              <strong>{{ activeOrder.reservationId }}</strong>
            </div>
            <div class="summary-row">
              <span>应付金额</span>
              <strong>￥{{ activeOrder.amount }}</strong>
            </div>
            <div class="summary-row">
              <span>收款账户</span>
              <strong>{{ activeOrder.account }}</strong>
            </div>
            <div class="summary-row">
              <span>截止日期</span>
              <strong>{{ activeOrder.deadline }}</strong>
            </div>
          </div>
        </div>
        <p v-else class="empty-state">选择订单查看缴费信息。</p>
        <p v-if="paymentNotice" class="form-hint">{{ paymentNotice }}</p>
      </div>
    </section>
  </main>
</template>

<script setup>
import { computed, reactive, ref, watch } from "vue";

const props = defineProps({
  borrowerRole: {
    type: String,
    default: "student",
  },
});

const reservations = ref([]);
const paymentOrders = ref([]);
const selectedOrderId = ref("");
const paymentNotice = ref("");

const editing = ref(null);
const editForm = reactive({
  id: "",
  device: "",
  slot: "",
  purpose: "",
});
const editSaved = ref(false);

const isExternal = computed(() => props.borrowerRole === "external");

const seedReservations = (role) => {
  if (role === "external") {
    return [
      {
        id: "R-2041",
        device: "C-118 光学平台",
        slot: "4 月 18 日 14:00 - 16:00",
        location: "C 区",
        status: "待缴费",
        purpose: "产业合作测试",
        orderId: "F-3210",
      },
      {
        id: "R-2044",
        device: "A-417 光谱仪",
        slot: "4 月 21 日 08:00 - 10:00",
        location: "A 区",
        status: "待确认",
        purpose: "企业材料分析",
        orderId: "F-3212",
      },
      {
        id: "R-2048",
        device: "B-203 热分析平台",
        slot: "4 月 24 日 10:00 - 12:00",
        location: "B 区",
        status: "退回补充材料",
        purpose: "外部委托",
      },
    ];
  }
  return [
    {
      id: "R-1491",
      device: "A-417 光谱仪",
      slot: "4 月 12 日 08:00 - 10:00",
      location: "A 区",
      status: "已批准",
      purpose: "项目 A-12",
    },
    {
      id: "R-1493",
      device: "B-203 热分析平台",
      slot: "4 月 13 日 10:00 - 12:00",
      location: "B 区",
      status: "退回补充材料",
      purpose: "材料测试",
    },
    {
      id: "R-1498",
      device: "C-118 光学平台",
      slot: "4 月 15 日 14:00 - 16:00",
      location: "C 区",
      status: "待审批",
      purpose: "实验验证",
    },
  ];
};

const seedPayments = (role) => {
  if (role !== "external") return [];
  return [
    {
      id: "F-3210",
      reservationId: "R-2041",
      detail: "校外 · 产业合作 · C-118 光学平台",
      amount: 5400,
      status: "待支付",
      account: "江南大学财务处 · 6222 **** 8890",
      deadline: "4 月 16 日 18:00",
    },
    {
      id: "F-3212",
      reservationId: "R-2044",
      detail: "校外 · 企业项目 · A-417 光谱仪",
      amount: 3200,
      status: "待确认",
      account: "江南大学财务处 · 6222 **** 8890",
      deadline: "4 月 19 日 18:00",
    },
  ];
};

watch(
  () => props.borrowerRole,
  (role) => {
    reservations.value = seedReservations(role);
    paymentOrders.value = seedPayments(role);
    selectedOrderId.value = "";
    paymentNotice.value = "";
    editing.value = null;
    editSaved.value = false;
  },
  { immediate: true }
);

const activeOrder = computed(
  () => paymentOrders.value.find((order) => order.id === selectedOrderId.value) || null
);

const statusClass = (status) => {
  if (status === "已批准") return "chip-good";
  if (status === "待审批") return "chip-neutral";
  if (status === "待缴费") return "chip-warn";
  if (status === "待确认") return "chip-neutral";
  if (status === "退回补充材料") return "chip-warn";
  if (status === "已撤销") return "chip-alert";
  return "chip-neutral";
};

const paymentStatusClass = (status) => {
  if (status === "待支付") return "chip-warn";
  if (status === "待确认") return "chip-neutral";
  if (status === "已支付") return "chip-good";
  if (status === "已取消") return "chip-alert";
  return "chip-neutral";
};

const canEdit = (status) =>
  status === "待审批" || status === "退回补充材料";

const canCancel = (status) =>
  status === "待审批" || status === "已批准" || status === "待缴费";

const showPaymentAction = (status) =>
  isExternal.value && (status === "待缴费" || status === "待确认");

const paymentActionLabel = (status) =>
  status === "待缴费" ? "支付" : "查看订单";

const startEdit = (item) => {
  if (!canEdit(item.status)) return;
  editing.value = item.id;
  editForm.id = item.id;
  editForm.device = item.device;
  editForm.slot = item.slot;
  editForm.purpose = item.purpose;
};

const saveEdit = () => {
  const index = reservations.value.findIndex((item) => item.id === editForm.id);
  if (index === -1) return;
  reservations.value[index] = {
    ...reservations.value[index],
    device: editForm.device,
    slot: editForm.slot,
    purpose: editForm.purpose,
    status: "待审批",
  };
  editSaved.value = true;
  setTimeout(() => {
    editSaved.value = false;
  }, 2000);
};

const cancelReservation = (id) => {
  const index = reservations.value.findIndex((item) => item.id === id);
  if (index === -1) return;
  reservations.value[index].status = "已撤销";
  const orderId = reservations.value[index].orderId;
  if (orderId) {
    const order = paymentOrders.value.find((item) => item.id === orderId);
    if (order) order.status = "已取消";
  }
};

const selectOrder = (orderId) => {
  selectedOrderId.value = orderId;
};

const payOrder = (orderId) => {
  const order = paymentOrders.value.find((item) => item.id === orderId);
  if (!order) return;
  selectedOrderId.value = orderId;
  if (order.status === "待支付") {
    order.status = "待确认";
    const reservation = reservations.value.find(
      (item) => item.orderId === orderId
    );
    if (reservation) reservation.status = "待确认";
    paymentNotice.value = "支付已提交，等待财务回传确认。";
    setTimeout(() => {
      paymentNotice.value = "";
    }, 2400);
  }
};

const openPayment = (item) => {
  if (!item.orderId) return;
  if (item.status === "待缴费") {
    payOrder(item.orderId);
    return;
  }
  selectOrder(item.orderId);
};
</script>
