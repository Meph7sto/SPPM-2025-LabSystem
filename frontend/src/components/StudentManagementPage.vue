<template>
  <main class="canvas">
    <section class="page-header" data-animate style="--delay: 0.05s">
      <div>
        <p class="eyebrow">学生管理</p>
        <h1>指导名单维护</h1>
        <p class="lead">
          维护指导学生列表，支持新增、删除与 Excel 批量导入，确保预约审批链可核验。
        </p>
      </div>
      <div class="page-actions">
        <button type="button" class="ghost" @click="downloadTemplate">
          下载导入模板
        </button>
        <button type="button" class="primary" @click="triggerFile">
          导入 Excel
        </button>
      </div>
    </section>

    <section class="grid" data-animate style="--delay: 0.12s">
      <div class="card wide">
        <div class="card-header">
          <div>
            <p class="card-kicker">关系台账</p>
            <h2>指导学生列表</h2>
          </div>
          <div class="chip-row">
            <span class="chip chip-neutral">{{ filteredStudents.length }} 人</span>
            <span class="chip chip-accent">FR-28 / FR-29</span>
          </div>
        </div>
        <div class="student-toolbar">
          <input
            v-model="keyword"
            type="text"
            placeholder="搜索学号 / 姓名 / 专业"
          />
          <select v-model="statusFilter">
            <option value="all">全部状态</option>
            <option value="active">在读</option>
            <option value="inactive">暂停</option>
          </select>
          <button type="button" class="ghost" @click="resetFilters">
            清空筛选
          </button>
        </div>
        <div class="student-table">
          <div v-for="student in filteredStudents" :key="student.id" class="student-row">
            <div>
              <h3>{{ student.name }}</h3>
              <p>
                {{ student.studentNo }} · {{ student.major }} ·
                {{ student.college }}
              </p>
              <div class="chip-row">
                <span class="chip chip-neutral">{{ student.grade }}</span>
                <span class="chip" :class="student.active ? 'chip-good' : 'chip-warn'">
                  {{ student.active ? "在读" : "暂停" }}
                </span>
              </div>
            </div>
            <div class="student-meta">
              <p class="meta-title">最近更新</p>
              <p class="meta-value">{{ student.updated }}</p>
              <p class="meta-caption">来源：{{ student.source }}</p>
            </div>
            <div class="student-actions">
              <button type="button" class="ghost" @click="selectStudent(student)">
                查看
              </button>
              <button type="button" class="danger" @click="removeStudent(student.id)">
                移除
              </button>
            </div>
          </div>
        </div>
        <p v-if="filteredStudents.length === 0" class="empty-state">
          没有匹配的学生记录，请调整筛选条件。
        </p>
        <div v-if="activeStudent" class="student-detail">
          <div class="summary-list">
            <div class="summary-row">
              <span>学生姓名</span>
              <strong>{{ activeStudent.name }}</strong>
            </div>
            <div class="summary-row">
              <span>学号</span>
              <strong>{{ activeStudent.studentNo }}</strong>
            </div>
            <div class="summary-row">
              <span>专业 / 学院</span>
              <strong>{{ activeStudent.major }} · {{ activeStudent.college }}</strong>
            </div>
            <div class="summary-row">
              <span>审核状态</span>
              <strong>{{ activeStudent.active ? "在读" : "暂停" }}</strong>
            </div>
          </div>
          <button type="button" class="ghost" @click="activeStudent = null">
            清除选择
          </button>
        </div>
      </div>
    </section>

    <section class="grid" data-animate style="--delay: 0.18s">
      <div class="card">
        <div class="card-header">
          <div>
            <p class="card-kicker">单条录入</p>
            <h2>新增指导学生</h2>
          </div>
          <span class="chip chip-good">即时生效</span>
        </div>
        <form class="form" @submit.prevent="addStudent">
          <label>
            学生姓名
            <input v-model="form.name" type="text" />
          </label>
          <label>
            学号
            <input v-model="form.studentNo" type="text" />
          </label>
          <label>
            专业
            <input v-model="form.major" type="text" />
          </label>
          <label>
            学院
            <input v-model="form.college" type="text" />
          </label>
          <button type="submit" class="primary">添加到名单</button>
          <p v-if="saved" class="form-hint">学生已添加到指导名单。</p>
        </form>
      </div>

      <div class="card">
        <div class="card-header">
          <div>
            <p class="card-kicker">Excel 导入</p>
            <h2>批量更新名单</h2>
          </div>
          <span class="chip chip-neutral">模板校验</span>
        </div>
        <div class="upload-panel">
          <label class="upload-drop">
            <input
              ref="fileInput"
              type="file"
              accept=".xlsx,.xls,.csv"
              @change="handleFile"
            />
            <span class="upload-title">拖拽 Excel 文件或点击上传</span>
            <span class="upload-meta">支持 .xlsx / .xls / .csv</span>
          </label>
          <div class="summary-list">
            <div class="summary-row">
              <span>文件名称</span>
              <strong>{{ fileName || "尚未选择" }}</strong>
            </div>
            <div class="summary-row">
              <span>导入策略</span>
              <strong>新增 / 覆盖同学号</strong>
            </div>
            <div class="summary-row">
              <span>格式检查</span>
              <strong>{{ fileName ? "待导入" : "未检测" }}</strong>
            </div>
          </div>
          <button
            type="button"
            class="primary"
            :disabled="!fileName"
            @click="importStudents"
          >
            执行导入
          </button>
          <p v-if="importMessage" class="form-hint">{{ importMessage }}</p>
        </div>
      </div>
    </section>
  </main>
</template>

<script setup>
import { computed, reactive, ref } from "vue";

const keyword = ref("");
const statusFilter = ref("all");
const saved = ref(false);
const importMessage = ref("");
const fileName = ref("");
const activeStudent = ref(null);
const fileInput = ref(null);

const students = ref([
  {
    id: "S-1021",
    name: "张欣怡",
    studentNo: "20241234",
    major: "材料科学与工程",
    college: "材料学院",
    grade: "2022 级",
    active: true,
    updated: "2 天前",
    source: "手动新增",
  },
  {
    id: "S-1034",
    name: "李文博",
    studentNo: "20240156",
    major: "化学工程",
    college: "化工学院",
    grade: "2021 级",
    active: true,
    updated: "4 小时前",
    source: "Excel 导入",
  },
  {
    id: "S-1088",
    name: "周语晴",
    studentNo: "20231287",
    major: "生物工程",
    college: "生物学院",
    grade: "2020 级",
    active: false,
    updated: "1 周前",
    source: "暂停借用",
  },
]);

const form = reactive({
  name: "",
  studentNo: "",
  major: "",
  college: "",
});

const filteredStudents = computed(() => {
  const keywordValue = keyword.value.trim().toLowerCase();
  return students.value.filter((student) => {
    const matchesKeyword =
      !keywordValue ||
      student.name.toLowerCase().includes(keywordValue) ||
      student.studentNo.includes(keywordValue) ||
      student.major.toLowerCase().includes(keywordValue);
    const matchesStatus =
      statusFilter.value === "all" ||
      (statusFilter.value === "active" && student.active) ||
      (statusFilter.value === "inactive" && !student.active);
    return matchesKeyword && matchesStatus;
  });
});

const resetFilters = () => {
  keyword.value = "";
  statusFilter.value = "all";
};

const addStudent = () => {
  if (!form.name || !form.studentNo) return;
  students.value.unshift({
    id: `S-${Math.floor(Math.random() * 9000 + 1000)}`,
    name: form.name,
    studentNo: form.studentNo,
    major: form.major || "待补充",
    college: form.college || "待补充",
    grade: "待确认",
    active: true,
    updated: "刚刚",
    source: "手动新增",
  });
  form.name = "";
  form.studentNo = "";
  form.major = "";
  form.college = "";
  saved.value = true;
  setTimeout(() => {
    saved.value = false;
  }, 2000);
};

const removeStudent = (id) => {
  students.value = students.value.filter((student) => student.id !== id);
  if (activeStudent.value?.id === id) {
    activeStudent.value = null;
  }
};

const selectStudent = (student) => {
  activeStudent.value = student;
};

const downloadTemplate = () => {
  const content =
    "studentNo,name,major,college,grade\n20241234,张欣怡,材料科学与工程,材料学院,2022\n";
  const blob = new Blob([content], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "导师学生名单模板.csv";
  link.click();
  URL.revokeObjectURL(url);
};

const triggerFile = () => {
  fileInput.value?.click();
};

const handleFile = (event) => {
  const file = event.target.files?.[0];
  fileName.value = file ? file.name : "";
};

const importStudents = () => {
  if (!fileName.value) return;
  students.value.unshift(
    {
      id: "S-2012",
      name: "宋嘉昊",
      studentNo: "20251221",
      major: "机械工程",
      college: "机电学院",
      grade: "2023 级",
      active: true,
      updated: "刚刚",
      source: "Excel 导入",
    },
    {
      id: "S-2013",
      name: "韩子衿",
      studentNo: "20251008",
      major: "计算机科学",
      college: "信息学院",
      grade: "2023 级",
      active: true,
      updated: "刚刚",
      source: "Excel 导入",
    }
  );
  importMessage.value = "导入完成：新增 2 条，覆盖 0 条。";
  setTimeout(() => {
    importMessage.value = "";
  }, 2400);
};
</script>
