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
        <form class="form">
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
          <button type="button" class="primary">查询</button>
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
import { computed, reactive } from "vue";
import AvailabilityMatrix from "./AvailabilityMatrix.vue";

const filters = reactive({
  date: "",
  slot: "08:00-10:00",
  keyword: "",
  zone: "A区",
});

const equipmentList = [
  {
    id: "A-417",
    name: "A-417 光谱仪",
    meta: "精密光学 | 设备编号 A-417",
    status: "可用",
    statusClass: "chip-good",
    zone: "A区",
  },
  {
    id: "B-203",
    name: "B-203 热分析平台",
    meta: "材料分析 | 设备编号 B-203",
    status: "已占用",
    statusClass: "chip-warn",
    zone: "B区",
  },
  {
    id: "C-118",
    name: "C-118 光学平台",
    meta: "精密光学 | 设备编号 C-118",
    status: "检修",
    statusClass: "chip-alert",
    zone: "C区",
  },
  {
    id: "A-512",
    name: "A-512 显微成像系统",
    meta: "生命科学 | 设备编号 A-512",
    status: "可用",
    statusClass: "chip-good",
    zone: "A区",
  },
];

const filteredList = computed(() => {
  const keyword = filters.keyword.trim().toLowerCase();
  return equipmentList.filter((item) => {
    const matchesKeyword =
      !keyword ||
      item.name.toLowerCase().includes(keyword) ||
      item.meta.toLowerCase().includes(keyword);
    const matchesZone = item.zone === filters.zone;
    return matchesKeyword && matchesZone;
  });
});
</script>
