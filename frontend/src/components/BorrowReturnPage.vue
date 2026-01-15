<template>
  <main class="canvas">
    <section class="page-header" data-animate style="--delay: 0.05s">
      <div>
        <p class="eyebrow">借还管理</p>
        <h1>设备借出与归还</h1>
        <p class="lead">
          办理设备借出交接与归还验收，支持状态变更与物理检查记录。
        </p>
      </div>
      <div class="page-actions">
        <button type="button" class="ghost" @click="fetchReservations">刷新列表</button>
      </div>
    </section>

    <section class="grid" data-animate style="--delay: 0.12s">
      <div class="card wide">
        <div class="card-header">
          <div>
            <p class="card-kicker">借出待办</p>
            <h2>待借出设备</h2>
          </div>
          <span class="chip chip-accent">{{ effectiveReservations.length }} 条</span>
        </div>
        <div class="reservation-list" v-if="effectiveReservations.length > 0">
          <div v-for="item in effectiveReservations" :key="item.id" class="reservation-item">
            <div>
              <h3>{{ item.device?.model || "未知设备" }}</h3>
              <p>
                预约号：R-{{ item.id }} · 借用人：{{ item.user?.name || "未知" }}
              </p>
              <p class="meta">
                预约时间：{{ formatDateRange(item.start_time, item.end_time) }}
              </p>
            </div>
            <div class="reservation-actions">
              <button
                type="button"
                class="primary"
                @click="openBorrowModal(item)"
              >
                登记借出
              </button>
            </div>
          </div>
        </div>
        <p v-else class="empty-state">暂无待借出记录</p>
      </div>
    </section>

    <section class="grid" data-animate style="--delay: 0.2s">
      <div class="card wide">
        <div class="card-header">
          <div>
            <p class="card-kicker">归还待办</p>
            <h2>待归还设备</h2>
          </div>
          <span class="chip chip-warn">{{ borrowedReservations.length }} 条</span>
        </div>
        <div class="reservation-list" v-if="borrowedReservations.length > 0">
          <div v-for="item in borrowedReservations" :key="item.id" class="reservation-item">
            <div>
              <h3>{{ item.device?.model || "未知设备" }}</h3>
              <p>
                预约号：R-{{ item.id }} · 借用人：{{ item.user?.name || "未知" }}
              </p>
              <p class="meta">
                借出时间：{{ formatDate(item.borrow_time) }}
              </p>
            </div>
            <div class="reservation-actions">
              <button
                type="button"
                class="primary"
                @click="openReturnModal(item)"
              >
                登记归还
              </button>
            </div>
          </div>
        </div>
        <p v-else class="empty-state">暂无待归还记录</p>
      </div>
    </section>

    <!-- 借出弹窗 -->
    <div v-if="showBorrowModal" class="modal-backdrop">
      <div class="modal">
        <div class="modal-header">
          <h2>登记借出</h2>
          <button type="button" class="close-btn" @click="closeBorrowModal">×</button>
        </div>
        <div class="modal-body">
          <p>
            正在办理 <strong>{{ activeItem?.device?.model }}</strong> 的借出。<br>
            借用人：{{ activeItem?.user?.name }}
          </p>
          <label>
            交接备注
            <textarea
              v-model="borrowForm.handover_note"
              placeholder="设备外观、配件清单核对情况..."
              rows="3"
            ></textarea>
          </label>
        </div>
        <div class="modal-footer">
          <button type="button" class="ghost" @click="closeBorrowModal">取消</button>
          <button type="button" class="primary" @click="submitBorrow">确认借出</button>
        </div>
      </div>
    </div>

    <!-- 归还弹窗 -->
    <div v-if="showReturnModal" class="modal-backdrop">
      <div class="modal">
        <div class="modal-header">
          <h2>登记归还</h2>
          <button type="button" class="close-btn" @click="closeReturnModal">×</button>
        </div>
        <div class="modal-body">
          <p>
            正在办理 <strong>{{ activeItem?.device?.model }}</strong> 的归还。<br>
            借用人：{{ activeItem?.user?.name }}
          </p>
          <label>
            设备状态
            <select v-model="returnForm.device_condition">
              <option value="normal">正常 (Normal)</option>
              <option value="damaged">损坏 (Damaged)</option>
              <option value="needs_maintenance">需检修 (Needs Maintenance)</option>
            </select>
          </label>
          <label>
            归还备注
            <textarea
              v-model="returnForm.return_note"
              placeholder="设备检查情况说明..."
              rows="3"
            ></textarea>
          </label>
        </div>
        <div class="modal-footer">
          <button type="button" class="ghost" @click="closeReturnModal">取消</button>
          <button type="button" class="primary" @click="submitReturn">确认归还</button>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { reservationAPI } from "../api";

const allReservations = ref([]);
const showBorrowModal = ref(false);
const showReturnModal = ref(false);
const activeItem = ref(null);

const borrowForm = ref({
  handover_note: "设备状态良好，配件齐全",
});

const returnForm = ref({
  device_condition: "normal",
  return_note: "设备使用正常",
});

const effectiveReservations = computed(() => 
  allReservations.value.filter(r => r.status === "effective")
);

const borrowedReservations = computed(() => 
  allReservations.value.filter(r => r.status === "borrowed")
);

const formatDate = (str) => {
  if (!str) return "-";
  return new Date(str).toLocaleString("zh-CN");
};

const formatDateRange = (start, end) => {
  return `${formatDate(start)} - ${formatDate(end)}`;
};

const fetchReservations = async () => {
  try {
    // 获取足够多的记录以覆盖近期的借还
    const res = await reservationAPI.list(null, 0, 100); 
    if (res.data && res.data.items) {
      allReservations.value = res.data.items;
    }
  } catch (err) {
    console.error("Failed to fetch reservations:", err);
    alert("列表加载失败");
  }
};

const openBorrowModal = (item) => {
  activeItem.value = item;
  borrowForm.value.handover_note = "设备状态良好，配件齐全";
  showBorrowModal.value = true;
};

const closeBorrowModal = () => {
  showBorrowModal.value = false;
  activeItem.value = null;
};

const submitBorrow = async () => {
  if (!activeItem.value) return;
  try {
    await reservationAPI.borrow(activeItem.value.id, {
      handover_note: borrowForm.value.handover_note
    });
    alert("借出登记成功！");
    closeBorrowModal();
    fetchReservations();
  } catch (err) {
    console.error("Borrow failed:", err);
    alert("借出登记失败: " + err.message);
  }
};

const openReturnModal = (item) => {
  activeItem.value = item;
  returnForm.value.device_condition = "normal";
  returnForm.value.return_note = "设备使用正常";
  showReturnModal.value = true;
};

const closeReturnModal = () => {
  showReturnModal.value = false;
  activeItem.value = null;
};

const submitReturn = async () => {
  if (!activeItem.value) return;
  try {
    await reservationAPI.return(activeItem.value.id, {
      device_condition: returnForm.value.device_condition,
      return_note: returnForm.value.return_note
    });
    alert("归还登记成功！");
    closeReturnModal();
    fetchReservations();
  } catch (err) {
    console.error("Return failed:", err);
    alert("归还登记失败: " + err.message);
  }
};

onMounted(() => {
  fetchReservations();
});
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.25rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
}

.modal-body {
  margin-bottom: 2rem;
}

.modal-body label {
  display: block;
  margin-top: 1rem;
  font-weight: 500;
}

.modal-body select,
.modal-body textarea {
  width: 100%;
  margin-top: 0.5rem;
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.reservation-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.reservation-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border: 1px solid #eee;
  border-radius: 6px;
  background: #f9f9f9;
}

.reservation-item h3 {
  margin: 0 0 0.25rem 0;
  font-size: 1rem;
}

.reservation-item p {
  margin: 0;
  color: #666;
  font-size: 0.875rem;
}

.reservation-item .meta {
  font-size: 0.75rem;
  color: #999;
  margin-top: 0.25rem;
}

.empty-state {
  text-align: center;
  color: #999;
  padding: 2rem;
}
</style>
