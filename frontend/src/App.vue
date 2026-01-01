<template>
  <div class="grain" aria-hidden="true"></div>
  <LoginView
    v-if="activeView === 'login'"
    :default-role="defaultRole"
    @enter="enterDashboard"
    @register="enterRegister"
  />
  <RegisterView
    v-else-if="activeView === 'register'"
    :default-role="defaultRole"
    @registered="completeRegister"
    @back="exitToLogin"
  />
  <div v-else class="app" :data-mode="mode">
    <Sidebar
      :role-type="mode"
      :role-label="roleLabel"
      :borrower-role="borrowerRole"
      :timestamp="timestamp"
      @exit="exitToLogin"
      :active-page="activePage"
      @navigate="navigatePage"
    />
    <BorrowerDashboard
      v-if="mode === 'borrower' && activePage === 'dashboard'"
    />
    <AvailabilityPage
      v-else-if="mode === 'borrower' && activePage === 'availability'"
    />
    <ReservationPage
      v-else-if="mode === 'borrower' && activePage === 'reservation'"
    />
    <MyReservationsPage
      v-else-if="mode === 'borrower' && activePage === 'my-reservations'"
      :borrower-role="borrowerRole"
    />
    <StudentManagementPage
      v-else-if="
        mode === 'borrower' &&
        borrowerRole === 'teacher' &&
        activePage === 'students'
      "
    />
    <ProfileView v-else-if="mode === 'borrower' && activePage === 'profile'" />
    <NotificationsPage
      v-else-if="mode === 'borrower' && activePage === 'notifications'"
    />
    <ReportsPage v-else-if="mode === 'borrower' && activePage === 'reports'" />
    <AdminDashboard
      v-else-if="mode === 'admin' && activePage === 'dashboard'"
    />
    <ApprovalsPage
      v-else-if="mode === 'admin' && activePage === 'approvals'"
    />
    <AvailabilityPage
      v-else-if="mode === 'admin' && activePage === 'availability'"
    />
    <LedgerPage v-else-if="mode === 'admin' && activePage === 'ledger'" />
    <PaymentsPage v-else-if="mode === 'admin' && activePage === 'payments'" />
    <ReportsPage v-else-if="mode === 'admin' && activePage === 'reports'" />
    <HeadDashboard
      v-else-if="mode === 'head' && activePage === 'dashboard'"
    />
    <ApprovalsPage
      v-else-if="mode === 'head' && activePage === 'approvals'"
    />
    <StaffManagementPage
      v-else-if="mode === 'head' && activePage === 'staff'"
    />
    <ProcurementDisposalPage
      v-else-if="mode === 'head' && activePage === 'procurement'"
    />
    <SystemConfigPage
      v-else-if="mode === 'head' && activePage === 'system-config'"
    />
    <ReportsPage v-else-if="mode === 'head' && activePage === 'reports'" />
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import LoginView from "./components/LoginView.vue";
import RegisterView from "./components/RegisterView.vue";
import Sidebar from "./components/Sidebar.vue";
import BorrowerDashboard from "./components/BorrowerDashboard.vue";
import AdminDashboard from "./components/AdminDashboard.vue";
import AvailabilityPage from "./components/AvailabilityPage.vue";
import ReservationPage from "./components/ReservationPage.vue";
import MyReservationsPage from "./components/MyReservationsPage.vue";
import ProfileView from "./components/ProfileView.vue";
import ApprovalsPage from "./components/ApprovalsPage.vue";
import PaymentsPage from "./components/PaymentsPage.vue";
import NotificationsPage from "./components/NotificationsPage.vue";
import ReportsPage from "./components/ReportsPage.vue";
import LedgerPage from "./components/LedgerPage.vue";
import HeadDashboard from "./components/HeadDashboard.vue";
import StaffManagementPage from "./components/StaffManagementPage.vue";
import ProcurementDisposalPage from "./components/ProcurementDisposalPage.vue";
import SystemConfigPage from "./components/SystemConfigPage.vue";
import StudentManagementPage from "./components/StudentManagementPage.vue";

const activeView = ref("login");
const activePage = ref("dashboard");
const mode = ref("borrower");
const roleLabel = ref("");
const timestamp = ref("");
const defaultRole = ref("");
const borrowerRole = ref("student");

const roleMeta = {
  teacher: { label: "校内教师", type: "borrower" },
  student: { label: "校内学生", type: "borrower" },
  external: { label: "校外人员", type: "borrower" },
  admin: { label: "设备管理员", type: "admin" },
  head: { label: "实验室负责人", type: "head" },
};

const enterDashboard = (role) => {
  const meta = roleMeta[role] ?? roleMeta.student;
  mode.value = meta.type;
  roleLabel.value = meta.label;
  borrowerRole.value = role;
  activePage.value = "dashboard";
  activeView.value = "dashboard";
};

const enterRegister = (role) => {
  defaultRole.value = role;
  activeView.value = "register";
};

const completeRegister = (role) => {
  defaultRole.value = role;
  activeView.value = "login";
};

const exitToLogin = () => {
  activeView.value = "login";
  roleLabel.value = "";
};

const navigatePage = (page) => {
  activePage.value = page;
};

onMounted(() => {
  const formatter = new Intl.DateTimeFormat("zh-CN", {
    dateStyle: "medium",
    timeStyle: "short",
  });
  timestamp.value = `更新于 ${formatter.format(new Date())}`;
});
</script>
