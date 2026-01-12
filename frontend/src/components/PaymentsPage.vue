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
        <button type="button" class="ghost" @click="syncAll" :disabled="loading">
          同步财务
        </button>
        <button type="button" class="primary" @click="finalizeAll" :disabled="loading || finalConfirmations.length === 0">
          批量确认
        </button>
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
                :disabled="item.status !== '待确认' || loading"
                @click="confirmPayment(item)"
              >
                确认收款
              </button>
              <button type="button" class="ghost" :disabled="loading" @click="syncOne(item)">
                同步
              </button>
            </div>
          </div>
          <p v-if="error" class="form-hint">{{ error }}</p>
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
          <p v-if="error" class="form-hint">{{ error }}</p>
        </div>
      </div>
    </section>
  </main>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { financeAPI, reservationAPI } from "../api";

const loading = ref(false);
const error = ref("");

const paymentReservations = ref([]);
const finalReservations = ref([]);

const payments = computed(() =>
  paymentReservations.value
    .filter((r) => r.user?.borrower_type === "external")
    .map((r) => {
      const statusLabel =
        r.payment_status === "pending"
          ? "待确认"
          : r.payment_status === "paid"
          ? "已确认"
          : r.payment_status === "refunded"
          ? "已退款"
          : "待确认";
      return {
        id: r.payment_order_no || `R-${r.id}`,
        reservationId: r.id,
        orderNo: r.payment_order_no,
        detail: `校外 · ${r.user?.organization || r.user?.name || "申请人"} · ${
          r.device?.model || "设备"
        }`,
        amount: Number(r.payment_amount || 0),
        status: statusLabel,
        raw: r,
      };
    })
);

const finalConfirmations = computed(() =>
  finalReservations.value
    .filter((r) => r.user?.borrower_type === "external")
    .map((r) => ({
      id: r.id,
      title: `校外 · ${r.user?.organization || r.user?.name || "申请人"}`,
      detail: `${r.device?.model || "设备"} · ${formatDateRange(r.start_time, r.end_time)}`,
      status: "待确认",
      raw: r,
    }))
);

const statusClass = (status) => {
  if (status === "待确认") return "chip-warn";
  if (status === "已确认") return "chip-good";
  if (status === "退款处理中") return "chip-alert";
  if (status === "已退款") return "chip-alert";
  return "chip-neutral";
};

const formatDateRange = (start, end) => {
  if (!start || !end) return "未指定时间";
  const startDate = new Date(start);
  const endDate = new Date(end);
  const date = startDate.toLocaleDateString("zh-CN", { month: "numeric", day: "numeric" });
  const startTime = startDate.toLocaleTimeString("zh-CN", { hour: "2-digit", minute: "2-digit" });
  const endTime = endDate.toLocaleTimeString("zh-CN", { hour: "2-digit", minute: "2-digit" });
  return `${date} ${startTime} - ${endTime}`;
};

const fetchQueues = async () => {
  loading.value = true;
  error.value = "";
  try {
    const [paymentRes, finalRes] = await Promise.all([
      reservationAPI.list(null, 0, 200, { current_step: "payment" }),
      reservationAPI.list(null, 0, 200, { current_step: "final" }),
    ]);
    paymentReservations.value = paymentRes.data?.items || [];
    // 仅把已缴费（或无需缴费但走到final的）留给最终确认队列，这里外部只需 paid
    finalReservations.value = (finalRes.data?.items || []).filter(
      (r) => r.user?.borrower_type !== "external" || r.payment_status === "paid"
    );
  } catch (err) {
    console.error("Failed to fetch payment queues:", err);
    error.value = err.message || "缴费队列加载失败";
  } finally {
    loading.value = false;
  }
};

const syncOne = async (item) => {
  if (!item?.reservationId) return;
  loading.value = true;
  error.value = "";
  try {
    await reservationAPI.syncPayment(item.reservationId);
    await fetchQueues();
  } catch (err) {
    console.error("Failed to sync payment:", err);
    error.value = err.message || "同步财务失败";
  } finally {
    loading.value = false;
  }
};

const syncAll = async () => {
  if (payments.value.length === 0) return;
  loading.value = true;
  error.value = "";
  try {
    await Promise.all(
      payments.value.map((p) => reservationAPI.syncPayment(p.reservationId))
    );
    await fetchQueues();
  } catch (err) {
    console.error("Failed to sync all payments:", err);
    error.value = err.message || "同步财务失败";
  } finally {
    loading.value = false;
  }
};

// 用于演示：点击“确认收款”会走 Mock 财务更新 + 同步（真实对接时应由财务系统回传）
const confirmPayment = async (item) => {
  if (!item?.orderNo || !item?.reservationId) {
    error.value = "该预约未生成缴费单号";
    return;
  }
  loading.value = true;
  error.value = "";
  try {
    await financeAPI.mockUpdatePayment(item.orderNo, { status: "paid" });
    await reservationAPI.syncPayment(item.reservationId);
    await fetchQueues();
  } catch (err) {
    console.error("Failed to confirm payment:", err);
    error.value = err.message || "确认收款失败";
  } finally {
    loading.value = false;
  }
};

const finalize = async (reservationId) => {
  loading.value = true;
  error.value = "";
  try {
    await reservationAPI.finalize(reservationId);
    await fetchQueues();
  } catch (err) {
    console.error("Failed to finalize:", err);
    error.value = err.message || "最终确认失败";
  } finally {
    loading.value = false;
  }
};

const finalizeAll = async () => {
  if (finalConfirmations.value.length === 0) return;
  loading.value = true;
  error.value = "";
  try {
    await Promise.all(finalConfirmations.value.map((r) => reservationAPI.finalize(r.id)));
    await fetchQueues();
  } catch (err) {
    console.error("Failed to finalize all:", err);
    error.value = err.message || "批量最终确认失败";
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchQueues();
});
</script>
