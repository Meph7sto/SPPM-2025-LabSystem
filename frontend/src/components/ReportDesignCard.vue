<template>
  <div class="card report-design">
    <div class="card-header">
      <div>
        <p class="card-kicker">数据报表</p>
        <h2>系统数据设计图</h2>
      </div>
      <span class="chip chip-neutral">原型</span>
    </div>
    <div class="report-controls">
      <div class="control-row">
        <span class="control-label">时间范围</span>
        <div class="control-pills">
          <button
            v-for="range in timeRanges"
            :key="range.key"
            type="button"
            class="control-pill"
            :class="{ active: timeRange === range.key }"
            @click="timeRange = range.key"
          >
            {{ range.label }}
          </button>
        </div>
        <div class="control-summary">
          <span class="summary-text">范围：{{ activeRangeLabel }}</span>
          <span class="summary-text">维度：{{ activeFiltersLabel }}</span>
        </div>
      </div>
      <div class="control-row">
        <label class="control-field">
          设备类别
          <select v-model="filters.deviceCategory">
            <option v-for="option in deviceCategories" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </select>
        </label>
        <label class="control-field">
          使用人类型
          <select v-model="filters.userType">
            <option v-for="option in userTypes" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </select>
        </label>
        <label class="control-field">
          审批状态
          <select v-model="filters.status">
            <option v-for="option in statusOptions" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </select>
        </label>
      </div>
      <div v-if="timeRange === 'custom'" class="control-row control-custom">
        <label class="control-field">
          开始
          <input type="date" v-model="customRange.start" />
        </label>
        <label class="control-field">
          结束
          <input type="date" v-model="customRange.end" />
        </label>
      </div>
    </div>
    <div class="design-body">
      <div class="design-kpis">
        <div class="design-kpi">
          <span class="design-label">活跃设备</span>
          <span class="design-value">{{ displayData.kpis.activeDevices }}</span>
          <span class="design-delta" :class="displayData.deltaClasses.activeDevices">
            {{ displayData.delta.activeDevices }}
          </span>
        </div>
        <div class="design-kpi">
          <span class="design-label">风险预警</span>
          <span class="design-value">{{ displayData.kpis.risk }}</span>
          <span class="design-delta" :class="displayData.deltaClasses.risk">
            {{ displayData.delta.risk }}
          </span>
        </div>
        <div class="design-kpi">
          <span class="design-label">校外收入</span>
          <span class="design-value">￥{{ displayData.kpis.revenue.toLocaleString() }}</span>
          <span class="design-delta" :class="displayData.deltaClasses.revenue">
            {{ displayData.delta.revenue }}
          </span>
        </div>
      </div>

      <div class="design-chart">
        <div class="design-chart-header">
          <span>设备使用率趋势</span>
          <span class="design-tag">{{ rangeBadge }}</span>
        </div>
        <svg viewBox="0 0 360 160" class="design-svg" aria-hidden="true">
          <g class="design-grid">
            <line x1="20" y1="30" x2="340" y2="30" />
            <line x1="20" y1="70" x2="340" y2="70" />
            <line x1="20" y1="110" x2="340" y2="110" />
          </g>
          <g class="design-bars">
            <rect
              v-for="(bar, index) in chart.bars"
              :key="`bar-${index}`"
              :x="bar.x"
              :y="bar.y"
              :width="bar.width"
              :height="bar.height"
            />
          </g>
          <path class="design-area" :d="chart.areaPath" />
          <path class="design-line" :d="chart.linePath" />
          <g class="design-points">
            <circle
              v-for="(point, index) in chart.points"
              :key="`point-${index}`"
              :cx="point.x"
              :cy="point.y"
              r="3.5"
            />
          </g>
          <g class="design-alerts">
            <circle
              v-for="(alert, index) in chart.alerts"
              :key="`alert-${index}`"
              :cx="alert.x"
              :cy="alert.y"
              r="3"
            />
          </g>
        </svg>
        <div class="design-legend">
          <span class="legend-item"><i class="legend-dot accent"></i>预约量</span>
          <span class="legend-item"><i class="legend-dot teal"></i>使用率</span>
          <span class="legend-item"><i class="legend-dot signal"></i>预警</span>
        </div>
      </div>

      <div class="design-notes">
        <div>
          <span class="note-label">峰值时段</span>
          <span class="note-value">{{ displayData.notes.peak }}</span>
        </div>
        <div>
          <span class="note-label">设备闲置</span>
          <span class="note-value">
            {{ displayData.notes.idleCount }} 台（{{ displayData.notes.idleTag }}）
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from "vue";

const timeRanges = [
  { key: "7d", label: "近7天" },
  { key: "30d", label: "近30天" },
  { key: "month", label: "本月" },
  { key: "quarter", label: "本季度" },
  { key: "custom", label: "自定义" }
];

const timeRange = ref("30d");

const customRange = reactive({
  start: "2026-01-01",
  end: "2026-01-15"
});

const deviceCategories = [
  { value: "all", label: "全部设备" },
  { value: "precision", label: "精密测量" },
  { value: "materials", label: "材料分析" },
  { value: "electronics", label: "电子测量" },
  { value: "bio", label: "生命科学" }
];

const userTypes = [
  { value: "all", label: "全部" },
  { value: "teacher", label: "教师" },
  { value: "student", label: "学生" },
  { value: "external", label: "校外" }
];

const statusOptions = [
  { value: "all", label: "全部" },
  { value: "active", label: "已生效" },
  { value: "cancelled", label: "已撤销" },
  { value: "returned", label: "已归还" },
  { value: "inuse", label: "借用中" }
];

const filters = reactive({
  deviceCategory: "all",
  userType: "all",
  status: "all"
});

const baseData = {
  "7d": {
    kpis: { activeDevices: 92, risk: 6, revenue: 18400 },
    usage: [62, 74, 58, 80, 67, 88, 72, 90],
    reservations: [40, 54, 46, 68, 59, 71, 52, 76],
    alerts: [3, 4, 2, 5, 3, 4, 2, 3],
    notes: { peak: "周三 14:00 - 18:00", idleCount: 3, idleTag: "重点盘点" }
  },
  "30d": {
    kpis: { activeDevices: 128, risk: 4, revenue: 76400 },
    usage: [58, 66, 72, 60, 68, 75, 70, 82],
    reservations: [45, 58, 62, 54, 63, 70, 64, 78],
    alerts: [2, 3, 1, 3, 2, 4, 2, 3],
    notes: { peak: "周四 13:00 - 17:00", idleCount: 4, idleTag: "低利用" }
  },
  "month": {
    kpis: { activeDevices: 136, risk: 5, revenue: 84200 },
    usage: [60, 70, 68, 74, 72, 80, 76, 88],
    reservations: [48, 60, 58, 64, 66, 73, 69, 81],
    alerts: [2, 2, 3, 2, 3, 4, 3, 3],
    notes: { peak: "周二 10:00 - 16:00", idleCount: 2, idleTag: "待调度" }
  },
  "quarter": {
    kpis: { activeDevices: 152, risk: 8, revenue: 248000 },
    usage: [55, 62, 66, 70, 74, 78, 83, 86],
    reservations: [42, 50, 58, 62, 68, 72, 75, 80],
    alerts: [4, 5, 3, 4, 4, 5, 4, 5],
    notes: { peak: "季度中段 09:00 - 17:00", idleCount: 6, idleTag: "高风险" }
  },
  "custom": {
    kpis: { activeDevices: 118, risk: 5, revenue: 56400 },
    usage: [57, 65, 61, 69, 63, 77, 69, 83],
    reservations: [44, 56, 52, 60, 55, 69, 57, 74],
    alerts: [3, 3, 2, 3, 3, 4, 3, 3],
    notes: { peak: "自定义时段 13:00 - 18:00", idleCount: 5, idleTag: "关注" }
  }
};

const deviceFactorMap = {
  all: 1,
  precision: 0.95,
  materials: 1.08,
  electronics: 0.9,
  bio: 1.02
};

const userFactorMap = {
  all: 1,
  teacher: 0.9,
  student: 1.1,
  external: 0.75
};

const statusFactorMap = {
  all: 1,
  active: 1.05,
  cancelled: 0.4,
  returned: 0.8,
  inuse: 0.95
};

const clamp = (value, min, max) => Math.min(Math.max(value, min), max);

const factor = computed(() => (
  deviceFactorMap[filters.deviceCategory]
  * userFactorMap[filters.userType]
  * statusFactorMap[filters.status]
));

const rangeBadge = computed(() => {
  if (timeRange.value === "custom") return "自定义";
  return timeRanges.find((range) => range.key === timeRange.value)?.label || "近30天";
});

const activeRangeLabel = computed(() => {
  if (timeRange.value === "custom") {
    const start = customRange.start || "----";
    const end = customRange.end || "----";
    return `${start} ~ ${end}`;
  }
  return timeRanges.find((range) => range.key === timeRange.value)?.label || "近30天";
});

const activeFiltersLabel = computed(() => {
  const labels = [];
  if (filters.deviceCategory !== "all") {
    labels.push(deviceCategories.find((option) => option.value === filters.deviceCategory)?.label);
  }
  if (filters.userType !== "all") {
    labels.push(userTypes.find((option) => option.value === filters.userType)?.label);
  }
  if (filters.status !== "all") {
    labels.push(statusOptions.find((option) => option.value === filters.status)?.label);
  }
  const filtered = labels.filter(Boolean);
  return filtered.length ? filtered.join(" · ") : "全部";
});

const displayData = computed(() => {
  const base = baseData[timeRange.value] || baseData["30d"];
  const factorValue = factor.value;
  const riskFactor = clamp(2 - factorValue, 0.7, 1.5);
  const usage = base.usage.map((value) => clamp(Math.round(value * factorValue), 8, 100));
  const reservations = base.reservations.map((value) => clamp(Math.round(value * factorValue), 8, 100));
  const alerts = base.alerts.map((value) => clamp(Math.round(value * riskFactor), 0, 10));

  const delta = {
    activeDevices: factorValue >= 1 ? `+${Math.round((factorValue - 1) * 100)}%` : `${Math.round((factorValue - 1) * 100)}%`,
    risk: riskFactor >= 1 ? `+${Math.round((riskFactor - 1) * 10)}` : `${Math.round((riskFactor - 1) * 10)}`,
    revenue: factorValue >= 1 ? `+${Math.round((factorValue - 1) * 120)}%` : `${Math.round((factorValue - 1) * 120)}%`
  };

  return {
    kpis: {
      activeDevices: Math.max(1, Math.round(base.kpis.activeDevices * factorValue)),
      risk: Math.max(1, Math.round(base.kpis.risk * riskFactor)),
      revenue: Math.max(0, Math.round(base.kpis.revenue * factorValue))
    },
    delta,
    deltaClasses: {
      activeDevices: delta.activeDevices.startsWith("-") ? "down" : "up",
      risk: delta.risk.startsWith("-") ? "down" : "up",
      revenue: delta.revenue.startsWith("-") ? "down" : "up"
    },
    usage,
    reservations,
    alerts,
    notes: {
      peak: base.notes.peak,
      idleCount: Math.max(1, Math.round(base.notes.idleCount * riskFactor)),
      idleTag: base.notes.idleTag
    }
  };
});

const chart = computed(() => {
  const startX = 30;
  const step = 40;
  const barWidth = 16;
  const top = 30;
  const bottom = 140;
  const maxValue = 100;

  const bars = displayData.value.usage.map((value, index) => {
    const height = (value / maxValue) * (bottom - top);
    return {
      x: startX + index * step,
      y: bottom - height,
      width: barWidth,
      height
    };
  });

  const points = displayData.value.reservations.map((value, index) => ({
    x: startX + index * step + barWidth / 2,
    y: bottom - (value / maxValue) * (bottom - top)
  }));

  const alerts = displayData.value.alerts.map((value, index) => ({
    x: startX + index * step + barWidth / 2,
    y: bottom + 8 - value * 2
  }));

  const linePath = points.map((point, index) => `${index === 0 ? "M" : "L"}${point.x} ${point.y}`).join(" ");
  const areaPath = `${linePath} L${points[points.length - 1].x} ${bottom} L${points[0].x} ${bottom} Z`;

  return {
    bars,
    points,
    alerts,
    linePath,
    areaPath
  };
});
</script>

<style scoped>
.report-design {
  position: relative;
  overflow: hidden;
}

.report-controls {
  margin-bottom: 18px;
  padding: 12px 14px;
  border: 1px solid rgba(28, 40, 52, 0.12);
  background: rgba(28, 40, 52, 0.04);
  display: grid;
  gap: 12px;
  font-family: "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
}

.control-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}

.control-label {
  font-size: 12px;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: rgba(28, 40, 52, 0.6);
}

.control-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.control-pill {
  border: 1px solid rgba(28, 40, 52, 0.3);
  background: transparent;
  padding: 6px 12px;
  font-size: 12px;
  cursor: pointer;
  letter-spacing: 0.4px;
  transition: background 0.2s ease, border-color 0.2s ease;
}

.control-pill.active {
  background: rgba(196, 105, 47, 0.2);
  border-color: rgba(196, 105, 47, 0.8);
}

.control-summary {
  margin-left: auto;
  display: grid;
  gap: 4px;
  font-size: 12px;
  color: rgba(28, 40, 52, 0.7);
  text-align: right;
}

.summary-text {
  white-space: nowrap;
}

.control-field {
  display: grid;
  gap: 6px;
  font-size: 12px;
  color: rgba(28, 40, 52, 0.7);
}

.control-field select,
.control-field input {
  padding: 8px 10px;
  border: 1px solid rgba(28, 40, 52, 0.25);
  background: rgba(255, 255, 255, 0.85);
  font-size: 12px;
  font-family: "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
}

.control-custom {
  padding-top: 6px;
  border-top: 1px dashed rgba(28, 40, 52, 0.18);
}

.design-body {
  display: grid;
  gap: 18px;
}

.design-kpis {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  font-family: "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
}

.design-kpi {
  padding: 12px 12px 10px;
  border: 1px solid rgba(28, 40, 52, 0.12);
  background: rgba(28, 40, 52, 0.05);
  display: grid;
  gap: 6px;
}

.design-label {
  font-size: 12px;
  letter-spacing: 1px;
  color: rgba(28, 40, 52, 0.6);
  text-transform: uppercase;
}

.design-value {
  font-size: 22px;
  font-weight: 600;
  color: var(--ink-950);
}

.design-delta {
  font-size: 12px;
}

.design-delta.up {
  color: var(--teal);
}

.design-delta.down {
  color: var(--signal);
}

.design-chart {
  padding: 14px 14px 12px;
  border: 1px solid rgba(28, 40, 52, 0.14);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.9), rgba(240, 232, 218, 0.6));
  display: grid;
  gap: 12px;
}

.design-chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-family: "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
  font-size: 13px;
  color: rgba(28, 40, 52, 0.8);
}

.design-tag {
  font-size: 11px;
  letter-spacing: 1.2px;
  text-transform: uppercase;
  color: rgba(28, 40, 52, 0.6);
}

.design-svg {
  width: 100%;
  height: auto;
}

.design-grid line {
  stroke: rgba(28, 40, 52, 0.15);
  stroke-dasharray: 4 6;
}

.design-bars rect {
  fill: rgba(47, 143, 137, 0.35);
}

.design-area {
  fill: rgba(196, 105, 47, 0.18);
}

.design-line {
  fill: none;
  stroke: var(--accent);
  stroke-width: 2.4;
}

.design-points circle {
  fill: #f8f3ea;
  stroke: var(--accent);
  stroke-width: 2;
}

.design-alerts circle {
  fill: var(--signal);
}

.design-legend {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  font-size: 12px;
  color: rgba(28, 40, 52, 0.7);
}

.legend-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
  background: rgba(28, 40, 52, 0.3);
}

.legend-dot.accent {
  background: var(--accent);
}

.legend-dot.teal {
  background: var(--teal);
}

.legend-dot.signal {
  background: var(--signal);
}

.design-notes {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  font-family: "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
}

.design-notes div {
  padding: 10px 12px;
  border: 1px solid rgba(28, 40, 52, 0.12);
  background: rgba(255, 255, 255, 0.7);
  display: grid;
  gap: 6px;
}

.note-label {
  font-size: 12px;
  color: rgba(28, 40, 52, 0.6);
  letter-spacing: 1px;
  text-transform: uppercase;
}

.note-value {
  font-size: 14px;
  color: var(--ink-950);
}

@media (max-width: 900px) {
  .design-kpis,
  .design-notes {
    grid-template-columns: 1fr;
  }

  .control-row {
    align-items: flex-start;
  }

  .control-summary {
    margin-left: 0;
    text-align: left;
  }

  .control-field {
    width: 100%;
  }

  .control-field select,
  .control-field input {
    width: 100%;
  }
}
</style>
