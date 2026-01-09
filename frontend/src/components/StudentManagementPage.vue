<template>
  <main class="canvas">
    <section class="page-header" data-animate style="--delay: 0.05s">
      <div>
        <p class="eyebrow">学生管理</p>
        <h1>指导名单维护</h1>
        <p class="lead">
          维护指导学生列表，支持新增、删除与 CSV 批量导入，确保预约审批链可核验。
        </p>
      </div>
      <div class="page-actions">
        <button type="button" class="ghost" @click="downloadTemplate">
          下载导入模板
        </button>
        <button type="button" class="primary" @click="triggerFile">
          导入 CSV
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
            placeholder="搜索学号 / 姓名 / 导师工号"
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
                {{ student.studentNo }} ·
                {{ student.advisorNo || "导师未绑定" }} ·
                {{ student.college || "学院待补充" }}
              </p>
              <div class="chip-row">
                <span class="chip chip-neutral">
                  {{ student.advisorNo ? `导师 ${student.advisorNo}` : "导师未绑定" }}
                </span>
                <span class="chip" :class="student.active ? 'chip-good' : 'chip-warn'">
                  {{ student.active ? "在读" : "暂停" }}
                </span>
              </div>
            </div>
            <div class="student-meta">
              <p class="meta-title">创建时间</p>
              <p class="meta-value">{{ formatDate(student.createdAt) }}</p>
              <p class="meta-caption">联系方式：{{ student.contact || "未填写" }}</p>
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
        <p v-if="isLoading" class="form-hint">正在加载学生数据...</p>
        <p v-else-if="loadError" class="form-hint">{{ loadError }}</p>
        <p v-else-if="filteredStudents.length === 0" class="empty-state">
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
              <span>导师工号</span>
              <strong>{{ activeStudent.advisorNo || "未绑定" }}</strong>
            </div>
            <div class="summary-row">
              <span>学院</span>
              <strong>{{ activeStudent.college || "未填写" }}</strong>
            </div>
            <div class="summary-row">
              <span>联系方式</span>
              <strong>{{ activeStudent.contact || "未填写" }}</strong>
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
            导师工号
            <input v-model="form.advisorNo" type="text" />
          </label>
          <label>
            联系方式
            <input v-model="form.contact" type="text" />
          </label>
          <label>
            学院
            <input v-model="form.college" type="text" />
          </label>
          <button type="submit" class="primary">添加到名单</button>
          <p v-if="formError" class="form-hint">{{ formError }}</p>
          <p v-if="saved" class="form-hint">学生已添加到指导名单。</p>
        </form>
      </div>

      <div class="card">
        <div class="card-header">
          <div>
            <p class="card-kicker">CSV 导入</p>
            <h2>批量更新名单</h2>
          </div>
          <span class="chip chip-neutral">模板校验</span>
        </div>
        <div class="upload-panel">
          <label class="upload-drop">
            <input
              ref="fileInput"
              type="file"
              accept=".csv"
              @change="handleFile"
            />
            <span class="upload-title">拖拽 CSV 文件或点击上传</span>
            <span class="upload-meta">支持 .csv</span>
          </label>
          <div class="summary-list">
            <div class="summary-row">
              <span>文件名称</span>
              <strong>{{ fileName || "尚未选择" }}</strong>
            </div>
            <div class="summary-row">
              <span>导入策略</span>
              <strong>仅新增（学号重复跳过）</strong>
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
import { computed, reactive, ref, onMounted } from "vue";
import { staffAPI } from "../api";

const keyword = ref("");
const statusFilter = ref("all");
const saved = ref(false);
const formError = ref("");
const importMessage = ref("");
const fileName = ref("");
const selectedFile = ref(null);
const isLoading = ref(false);
const loadError = ref("");
const activeStudent = ref(null);
const fileInput = ref(null);

const students = ref([]);

const form = reactive({
  name: "",
  studentNo: "",
  advisorNo: "",
  contact: "",
  college: "",
});

const filteredStudents = computed(() => {
  const keywordValue = keyword.value.trim().toLowerCase();
  return students.value.filter((student) => {
    const matchesKeyword =
      !keywordValue ||
      student.name.toLowerCase().includes(keywordValue) ||
      student.studentNo.toLowerCase().includes(keywordValue) ||
      (student.advisorNo || "").toLowerCase().includes(keywordValue) ||
      (student.college || "").toLowerCase().includes(keywordValue) ||
      (student.contact || "").toLowerCase().includes(keywordValue);
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

const formatDate = (value) => {
  if (!value) return "未知";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleDateString("zh-CN");
};

const mapStudent = (item) => ({
  id: item.id,
  name: item.name,
  studentNo: item.student_no || "",
  advisorNo: item.advisor_no || "",
  contact: item.contact || "",
  college: item.college || "",
  active: item.is_active ?? true,
  createdAt: item.created_at,
});

const fetchStudents = async () => {
  isLoading.value = true;
  loadError.value = "";
  try {
    const res = await staffAPI.listStudents({ skip: 0, limit: 100 });
    const items = res.data?.items || [];
    const mapped = items.map(mapStudent);
    students.value = mapped;
    if (activeStudent.value) {
      activeStudent.value =
        mapped.find((student) => student.id === activeStudent.value.id) || null;
    }
  } catch (error) {
    console.error("Failed to fetch students:", error);
    loadError.value = "加载失败，请稍后重试。";
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  fetchStudents();
});

const addStudent = async () => {
  formError.value = "";
  const payload = {
    name: form.name.trim(),
    student_no: form.studentNo.trim(),
    advisor_no: form.advisorNo.trim(),
    contact: form.contact.trim(),
    college: form.college.trim(),
  };

  if (
    !payload.name ||
    !payload.student_no ||
    !payload.advisor_no ||
    !payload.contact ||
    !payload.college
  ) {
    formError.value = "请填写学生姓名、学号、导师工号、联系方式和学院。";
    return;
  }

  try {
    const res = await staffAPI.createStudent(payload);
    if (res.data) {
      students.value.unshift(mapStudent(res.data));
    }
    form.name = "";
    form.studentNo = "";
    form.advisorNo = "";
    form.contact = "";
    form.college = "";
    saved.value = true;
    setTimeout(() => {
      saved.value = false;
    }, 2000);
  } catch (error) {
    console.error("Failed to add student:", error);
    formError.value = error.message || "新增失败，请稍后重试。";
  }
};

const removeStudent = async (id) => {
  try {
    await staffAPI.deleteStudent(id);
    students.value = students.value.filter((student) => student.id !== id);
    if (activeStudent.value?.id === id) {
      activeStudent.value = null;
    }
  } catch (error) {
    console.error("Failed to remove student:", error);
    alert("删除失败，请稍后重试。");
  }
};

const selectStudent = (student) => {
  activeStudent.value = student;
};

const downloadTemplate = () => {
  const content =
    "studentNo,name,advisorNo,contact,college\n20241234,张欣怡,T2023001,18800001111,材料学院\n";
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
  selectedFile.value = file || null;
  fileName.value = file ? file.name : "";
  importMessage.value = "";
};

const parseCsvRows = (text) => {
  const lines = text
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);
  if (lines.length < 2) return [];
  const headers = lines[0].split(",").map((header) => header.trim());
  return lines.slice(1).map((line) => {
    const values = line.split(",").map((value) => value.trim());
    const row = {};
    headers.forEach((header, index) => {
      row[header] = values[index] ?? "";
    });
    return row;
  });
};

const importStudents = async () => {
  if (!selectedFile.value) return;
  importMessage.value = "正在导入...";
  try {
    const text = await selectedFile.value.text();
    const rows = parseCsvRows(text);
    if (!rows.length) {
      importMessage.value = "未读取到有效数据，请检查模板。";
      return;
    }

    let success = 0;
    let failed = 0;
    const created = [];

    for (const row of rows) {
      const payload = {
        name: (row.name || "").trim(),
        student_no: (row.studentNo || "").trim(),
        advisor_no: (row.advisorNo || "").trim(),
        contact: (row.contact || "").trim(),
        college: (row.college || "").trim(),
      };

      if (
        !payload.name ||
        !payload.student_no ||
        !payload.advisor_no ||
        !payload.contact ||
        !payload.college
      ) {
        failed += 1;
        continue;
      }

      try {
        const res = await staffAPI.createStudent(payload);
        if (res.data) {
          created.push(mapStudent(res.data));
        }
        success += 1;
      } catch (error) {
        failed += 1;
      }
    }

    if (created.length) {
      students.value = [...created, ...students.value];
    }

    importMessage.value = `导入完成：新增 ${success} 条，失败 ${failed} 条。`;
  } catch (error) {
    console.error("Failed to import students:", error);
    importMessage.value = "导入失败，请检查文件格式。";
  } finally {
    setTimeout(() => {
      importMessage.value = "";
    }, 2400);
    selectedFile.value = null;
    fileName.value = "";
    if (fileInput.value) {
      fileInput.value.value = "";
    }
  }
};
</script>
