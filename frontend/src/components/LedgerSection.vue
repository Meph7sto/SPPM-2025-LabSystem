<template>
  <div class="card admin-only">
    <div class="card-header">
      <div>
        <p class="card-kicker">台账</p>
        <h2>资产与人员台账</h2>
      </div>
      <span class="chip chip-neutral">可审计</span>
    </div>
    <div class="ledger">
      <div class="ledger-row">
        <div>
          <h3>设备台账</h3>
          <p v-if="deviceStats">
            {{ deviceStats.total }} 台，{{ deviceStats.maintenance }} 台检修中
          </p>
          <p v-else class="form-hint">{{ error || "正在加载设备台账..." }}</p>
        </div>
        <button type="button" class="ghost">打开</button>
      </div>
      <div class="ledger-row">
        <div>
          <h3>教师台账</h3>
          <p v-if="staffStats">
            {{ staffStats.teachers }} 名教师，{{ staffStats.total }} 名人员
          </p>
          <p v-else class="form-hint">{{ error || "正在加载教师台账..." }}</p>
        </div>
        <button type="button" class="ghost">打开</button>
      </div>
      <div class="ledger-row">
        <div>
          <h3>学生台账</h3>
          <p v-if="staffStats">
            {{ staffStats.students }} 条记录已同步
          </p>
          <p v-else class="form-hint">{{ error || "正在加载学生台账..." }}</p>
        </div>
        <button type="button" class="ghost">打开</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { deviceAPI, staffAPI } from "../api";

const deviceStats = ref(null);
const staffStats = ref(null);
const error = ref("");

const fetchLedgerStats = async () => {
  error.value = "";
  try {
    const [deviceRes, staffRes] = await Promise.all([
      deviceAPI.ledgerStats(),
      staffAPI.stats(),
    ]);
    deviceStats.value = {
      total: deviceRes.data?.total ?? 0,
      maintenance: deviceRes.data?.by_status?.maintenance ?? 0,
    };
    staffStats.value = {
      teachers: staffRes.data?.teachers ?? 0,
      students: staffRes.data?.students ?? 0,
      externals: staffRes.data?.externals ?? 0,
      total: staffRes.data?.total ?? 0,
    };
  } catch (err) {
    console.error("Failed to fetch ledger stats:", err);
    error.value = err.message || "台账数据加载失败";
  }
};

onMounted(() => {
  fetchLedgerStats();
});
</script>
