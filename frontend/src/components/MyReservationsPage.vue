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
  </main>
</template>

<script setup>
import { reactive, ref } from "vue";

const reservations = ref([
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
]);

const editing = ref(null);
const editForm = reactive({
  id: "",
  device: "",
  slot: "",
  purpose: "",
});
const editSaved = ref(false);

const statusClass = (status) => {
  if (status === "已批准") return "chip-good";
  if (status === "待审批") return "chip-neutral";
  if (status === "退回补充材料") return "chip-warn";
  if (status === "已撤销") return "chip-alert";
  return "chip-neutral";
};

const canEdit = (status) =>
  status === "待审批" || status === "退回补充材料";

const canCancel = (status) => status === "待审批" || status === "已批准";

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
};
</script>
