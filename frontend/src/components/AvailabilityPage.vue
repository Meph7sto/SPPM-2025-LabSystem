<template>
  <main class="canvas">
    <section class="page-header" data-animate style="--delay: 0.05s">
      <div>
        <p class="eyebrow">可用性查询</p>
        <h1>设备可用时段一览</h1>
        <p class="lead">
          支持按日期、时段与关键字检索。检修窗内设备自动标记为不可预约。
        </p>
      </div>
      <div class="page-actions">
        <button type="button" class="ghost">导出列表</button>
        <button type="button" class="primary">发起预约</button>
      </div>
    </section>

    <section class="grid" data-animate style="--delay: 0.12s">
      <div class="card">
        <div class="card-header">
          <div>
            <p class="card-kicker">筛选</p>
            <h2>条件组合</h2>
          </div>
          <span class="chip chip-neutral">即时更新</span>
        </div>
        <form class="form" @submit.prevent="handleSearch">
          <label>
            查询日期
            <input type="date" v-model="filters.date" />
          </label>
          <label>
            时间段
            <select v-model="filters.slot">
              <option value="08:00-10:00">08:00 - 10:00</option>
              <option value="10:00-12:00">10:00 - 12:00</option>
              <option value="14:00-16:00">14:00 - 16:00</option>
              <option value="16:00-18:00">16:00 - 18:00</option>
              <option value="20:00-22:00">20:00 - 22:00</option>
            </select>
          </label>
          <label>
            关键字
            <input type="text" v-model="filters.keyword" placeholder="设备编号 / 型号" />
          </label>
          <label>
            区域
            <select v-model="filters.zone">
              <option value="A区">A 区</option>
              <option value="B区">B 区</option>
              <option value="C区">C 区</option>
            </select>
          </label>
          <button type="submit" class="primary" :disabled="loading">
            {{ loading ? "查询中..." : "查询" }}
          </button>
          <p v-if="error" class="form-hint">{{ error }}</p>
        </form>
      </div>

      <div class="card">
        <div class="card-header">
          <div>
            <p class="card-kicker">结果</p>
            <h2>可用设备</h2>
          </div>
          <span class="chip chip-good">{{ filteredList.length }} 台</span>
        </div>
        <div class="availability-list">
          <div v-for="item in filteredList" :key="item.id" class="availability-item">
            <div>
              <h3>{{ item.name }}</h3>
              <p>{{ item.meta }}</p>
            </div>
            <div class="chip-row">
              <span class="chip" :class="item.statusClass">{{ item.status }}</span>
              <span class="chip chip-neutral">{{ item.zone }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="grid" data-animate style="--delay: 0.2s">
      <AvailabilityMatrix />
      <div class="card">
        <div class="card-header">
          <div>
            <p class="card-kicker">规则</p>
            <h2>预约与检修提示</h2>
          </div>
          <span class="chip chip-warn">最小 2 小时</span>
        </div>
        <div class="rule-list">
          <div class="rule-item">
            <span class="rule-title">检修窗</span>
            <span class="rule-desc">检修时段不可预约，系统自动锁定</span>
          </div>
          <div class="rule-item">
            <span class="rule-title">预约提前期</span>
            <span class="rule-desc">必须提前 1-7 天提交申请</span>
          </div>
          <div class="rule-item">
            <span class="rule-title">冲突处理</span>
            <span class="rule-desc">同设备同时间段不可重复预约</span>
          </div>
        </div>
      </div>
    </section>
  </main>
</template>

<script setup>
import { computed, reactive, ref, onMounted } from "vue";
import AvailabilityMatrix from "./AvailabilityMatrix.vue";
import { deviceAPI } from "../api";

const getToday = () => {
  const now = new Date();
  const local = new Date(now.getTime() - now.getTimezoneOffset() * 60000);
  return local.toISOString().slice(0, 10);
};

const filters = reactive({
  date: getToday(),
  slot: "08:00-10:00",
  keyword: "",
  zone: "A区",
});

const availabilityItems = ref([]);
const loading = ref(false);
const error = ref("");

const filteredList = computed(() => {
  return availabilityItems.value;
});

const handleSearch = async () => {
  if (!filters.date) {
    error.value = "请选择查询日期";
    return;
  }

  loading.value = true;
  error.value = "";
  try {
    const params = {
      date: filters.date,
      slot: filters.slot,
    };
    if (filters.keyword.trim()) {
      params.keyword = filters.keyword.trim();
    }
    if (filters.zone) {
      params.zone = filters.zone;
    }
    const res = await deviceAPI.availability(params);
    const items = res.data?.items || [];
    availabilityItems.value = items.map((item) => ({
      id: item.id,
      name: item.name,
      meta: item.meta,
      status: item.status,
      statusClass: item.status_class,
      zone: item.zone,
    }));
  } catch (err) {
    console.error("Failed to fetch availability:", err);
    error.value = err.message || "查询失败，请稍后重试";
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  handleSearch();
});
</script>
