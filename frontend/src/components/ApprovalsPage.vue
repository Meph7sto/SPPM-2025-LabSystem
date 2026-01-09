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
        <button type="button" class="ghost" @click="fetchApprovals" :disabled="loading">
          刷新队列
        </button>
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
            <p class="stat-value">{{ stats.admin }} 条</p>
            <p class="stat-meta">含校内 {{ stats.adminInternal }} 条</p>
          </div>
          <div class="stat-card">
            <p class="stat-label">待导师审批</p>
            <p class="stat-value">{{ stats.advisor }} 条</p>
            <p class="stat-meta">学生申请</p>
          </div>
          <div class="stat-card">
            <p class="stat-label">待负责人审批</p>
            <p class="stat-value">{{ stats.head }} 条</p>
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
              <button
                type="button"
                class="primary"
                :disabled="isUpdating(item.id)"
                @click="handleAction(item, 'approve')"
              >
                通过
              </button>
              <button
                type="button"
                class="ghost"
                :disabled="isUpdating(item.id)"
                @click="handleAction(item, 'return')"
              >
                退回补充
              </button>
              <button
                type="button"
                class="danger"
                :disabled="isUpdating(item.id)"
                @click="handleAction(item, 'reject')"
              >
                驳回
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
import { reservationAPI, getCachedUserInfo } from "../api";

const reservations = ref([]);
const loading = ref(false);
const error = ref("");
const updating = ref({});

const user = getCachedUserInfo();
const role = user?.role;

const stepLabelMap = {
  advisor: "导师审批",
  admin: "管理员审批",
  head: "负责人审批",
  payment: "缴费确认",
  final: "最终确认",
  available: "可借出",
};

const stepRoleMap = {
  advisor: "指导教师",
  admin: "设备管理员",
  head: "实验室负责人",
  payment: "财务系统",
  final: "设备管理员",
  available: "实验室",
};

const chainTemplates = {
  student: ["advisor", "admin", "final", "available"],
  teacher: ["admin", "final", "available"],
  external: ["admin", "head", "payment", "final", "available"],
};

const stats = computed(() => {
  const base = { admin: 0, advisor: 0, head: 0, adminInternal: 0 };
  reservations.value.forEach((item) => {
    const step = item.current_step;
    if (step === "admin") {
      base.admin += 1;
      if (item.user?.borrower_type !== "external") {
        base.adminInternal += 1;
      }
    }
    if (step === "advisor") {
      base.advisor += 1;
    }
    if (step === "head") {
      base.head += 1;
    }
  });
  return base;
});

const approvals = computed(() => {
  const currentStep =
    role === "head" ? "head" : "admin";
  return reservations.value
    .filter((item) => item.current_step === currentStep)
    .map((item) => toApprovalCard(item));
});

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

const isUpdating = (id) => !!updating.value[id];

const formatDateRange = (start, end) => {
  if (!start || !end) return "未指定时间";
  const startDate = new Date(start);
  const endDate = new Date(end);
  const date = startDate.toLocaleDateString("zh-CN", {
    month: "numeric",
    day: "numeric",
  });
  const startTime = startDate.toLocaleTimeString("zh-CN", {
    hour: "2-digit",
    minute: "2-digit",
  });
  const endTime = endDate.toLocaleTimeString("zh-CN", {
    hour: "2-digit",
    minute: "2-digit",
  });
  return `${date} ${startTime} - ${endTime}`;
};

const buildChain = (item) => {
  const type = item.user?.borrower_type || "teacher";
  const template = chainTemplates[type] || chainTemplates.teacher;
  const currentStep = item.current_step;
  return template.map((step) => {
    let state = "pending";
    if (item.status === "approved" || item.status === "effective") {
      state = "done";
    } else if (step === currentStep) {
      state = "current";
    } else if (currentStep && template.indexOf(step) < template.indexOf(currentStep)) {
      state = "done";
    }
    return {
      label: stepLabelMap[step] || step,
      role: stepRoleMap[step] || "系统",
      state,
    };
  });
};

const toApprovalCard = (item) => {
  const borrowerType = item.user?.borrower_type;
  const typeLabel =
    borrowerType === "student"
      ? "学生"
      : borrowerType === "external"
      ? "校外"
      : "教师";
  const priority = borrowerType === "external" ? "校外缴费" : "校内优先";
  const stepLabel = stepLabelMap[item.current_step] || "待处理";
  return {
    id: item.id,
    title: `${typeLabel} · ${item.user?.name || "申请人"}`,
    detail: `${item.device?.model || "未知设备"} · ${formatDateRange(
      item.start_time,
      item.end_time
    )}`,
    step: stepLabel,
    priority,
    conflict: false,
    status: "待处理",
    chain: buildChain(item),
    raw: item,
  };
};

const handleAction = async (item, action) => {
  const nextAction = item.raw?.next_action;
  const payload =
    action === "approve"
      ? nextAction
      : action === "return"
      ? { status: "returned", current_step: null }
      : { status: "rejected", current_step: null };

  if (action === "approve" && !payload) {
    error.value = "后端未返回下一步动作，无法提交审批";
    return;
  }

  updating.value = { ...updating.value, [item.id]: true };
  error.value = "";
  try {
    await reservationAPI.update(item.id, payload);
    await fetchApprovals();
  } catch (err) {
    console.error("Failed to update approval:", err);
    error.value = err.message || "审批更新失败";
  } finally {
    const next = { ...updating.value };
    delete next[item.id];
    updating.value = next;
  }
};

const fetchApprovals = async () => {
  loading.value = true;
  error.value = "";
  try {
    const res = await reservationAPI.list(null, 0, 200);
    const items = res.data?.items || [];
    const pendingStatuses = new Set([
      "pending",
      "advisor_approved",
      "admin_approved",
      "head_approved",
    ]);
    reservations.value = items.filter((item) =>
      pendingStatuses.has(item.status)
    );
  } catch (err) {
    console.error("Failed to fetch approvals:", err);
    error.value = err.message || "审批列表加载失败";
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchApprovals();
});
</script>
