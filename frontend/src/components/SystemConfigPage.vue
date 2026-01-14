<script setup>
import { systemConfigAPI } from '../api.js'
import { ref, onMounted } from 'vue'

// 配置数据
const configData = ref({})
const loading = ref(false)
const message = ref('')

// 从后端获取配置
const fetchConfig = async () => {
  try {
    const response = await systemConfigAPI.getConfig()
    configData.value = response.data || response || {}
    message.value = '配置加载成功'
  } catch (error) {
    console.error('获取配置失败:', error)
    message.value = '获取配置失败'
  }
}

// 保存配置到后端
const saveConfig = async () => {
  loading.value = true
  message.value = ''
  try {
    const response = await systemConfigAPI.updateConfig(configData.value)
    message.value = response.message || '配置保存成功！'
  } catch (error) {
    console.error('保存配置失败:', error)
    message.value = '保存失败，请重试'
  } finally {
    loading.value = false
  }
}

// 查看配置快照
const viewSnapshot = () => {
  alert('当前配置：\n' + JSON.stringify(configData.value, null, 2))
}

onMounted(() => {
  fetchConfig()
})
</script>

<template>
  <main class="canvas">
    <div v-if="message" class="message">{{ message }}</div>

    <section class="page-header" data-animate style="--delay: 0.05s">
      <div>
        <p class="eyebrow">系统配置</p>
        <h1>流程、权限与策略设置</h1>
        <p class="lead">
          负责人可配置审批链、访问范围与通知策略，确保业务规则落地执行。
        </p>
      </div>
      <div class="page-actions">
        <button @click="viewSnapshot" type="button" class="ghost">查看配置快照</button>
        <button @click="saveConfig" :disabled="loading" type="button" class="primary">
          {{ loading ? '保存中...' : '保存配置' }}
        </button>
      </div>
    </section>

    <section class="grid" data-animate style="--delay: 0.12s">
      <div class="card">
        <div class="card-header">
          <div>
            <p class="card-kicker">流程与权限</p>
            <h2>审批链设置</h2>
          </div>
          <span class="chip chip-neutral">RBAC</span>
        </div>
        <div class="rule-list">
          <div class="rule-item">
            <span class="rule-title">校外审批链</span>
            <input v-model="configData.approval_external_chain"
                   class="config-input"
                   placeholder="管理员初审 → 负责人终审 → 缴费确认" />
          </div>
          <div class="rule-item">
            <span class="rule-title">校内学生审批</span>
            <input v-model="configData.approval_student_chain"
                   class="config-input"
                   placeholder="导师审批 → 管理员审批" />
          </div>
          <div class="rule-item">
            <span class="rule-title">权限分配</span>
            <input v-model="configData.permission_rules"
                   class="config-input"
                   placeholder="负责人可配置审批人、停用账号与审计策略" />
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <div>
            <p class="card-kicker">系统策略</p>
            <h2>访问与通知</h2>
          </div>
          <span class="chip chip-accent">局域网</span>
        </div>
        <div class="rule-list">
          <div class="rule-item">
            <span class="rule-title">局域网访问</span>
            <input v-model="configData.network_lan_access"
                   class="config-input"
                   placeholder="工作人员端仅允许校内 IP 访问" />
          </div>
          <div class="rule-item">
            <span class="rule-title">通知触发</span>
            <input v-model="configData.notification_triggers"
                   class="config-input"
                   placeholder="提交、审批、缴费、撤销节点自动提醒" />
          </div>
          <div class="rule-item">
            <span class="rule-title">定时任务</span>
            <input v-model="configData.scheduled_tasks"
                   class="config-input"
                   placeholder="周报/月报/年报自动生成并归档" />
          </div>
        </div>
      </div>
    </section>

    <section class="grid" data-animate style="--delay: 0.2s">
      <div class="card wide">
        <div class="card-header">
          <div>
            <p class="card-kicker">配置留痕</p>
            <h2>最近变更记录</h2>
          </div>
          <span class="chip chip-neutral">审计</span>
        </div>
        <div class="report-list">
          <div class="report-item">
            <div>
              <h3>审批链更新</h3>
              <p>新增校外缴费确认节点 · 2025-04-11 09:20</p>
            </div>
            <span class="chip chip-good">已生效</span>
          </div>
          <div class="report-item">
            <div>
              <h3>访问策略调整</h3>
              <p>新增 2 个局域网白名单 · 2025-04-10 16:30</p>
            </div>
            <span class="chip chip-neutral">完成</span>
          </div>
          <div class="report-item">
            <div>
              <h3>通知模板</h3>
              <p>补充缴费失败提醒文案 · 2025-04-09 13:45</p>
            </div>
            <span class="chip chip-warn">待复核</span>
          </div>
        </div>
      </div>
    </section>
  </main>
</template>

<style scoped>
.message {
  background: #4CAF50;
  color: white;
  padding: 10px;
  border-radius: 4px;
  margin: 10px 0;
  text-align: center;
}

.config-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  margin-left: 10px;
  box-sizing: border-box;
}

.rule-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.rule-title {
  min-width: 120px;
  font-weight: 500;
}

.chip-good { background: #d4edda; color: #155724; }
.chip-warn { background: #fff3cd; color: #856404; }
.chip-neutral { background: #f8f9fa; color: #495057; }
.chip-accent { background: #cce5ff; color: #004085; }
</style>