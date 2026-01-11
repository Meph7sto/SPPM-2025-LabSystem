<template>
  <main class="canvas">
    <section class="hero head-hero" data-animate style="--delay: 0.05s">
      <div class="hero-text">
        <p class="eyebrow">治理驾驶舱</p>
        <h1>面向全局的实验室决策面板。</h1>
        <p class="lead">
          关注审批终审、人员编制、采购报废与制度配置，确保校内优先与审计留痕。
        </p>
        <div class="hero-actions">
          <button type="button" class="primary">发布管理制度</button>
          <button type="button" class="ghost">查看员工编制</button>
        </div>
        <div class="ribbon">
          <span class="ribbon-step active">审批终审</span>
          <span class="ribbon-step">缴费确认</span>
          <span class="ribbon-step">最终确认</span>
          <span class="ribbon-step">借出监管</span>
          <span class="ribbon-step">报表归档</span>
        </div>
      </div>
      <div class="hero-panel">
        <div class="panel-card">
          <div class="panel-title">外部审批</div>
          <div class="panel-value">待终审 2 条</div>
          <div class="panel-caption">含缴费待确认 1 条</div>
          <div class="chip-row">
            <span class="chip chip-warn">校外流程</span>
            <span class="chip chip-neutral">校内优先</span>
          </div>
        </div>
        <div class="panel-card">
          <div class="panel-title">人员配置</div>
          <div class="panel-value">管理员 9 人</div>
          <div class="panel-caption">今日缺岗 1 人</div>
          <div class="signal-grid">
            <span class="signal good"></span>
            <span class="signal good"></span>
            <span class="signal good"></span>
            <span class="signal warn"></span>
            <span class="signal good"></span>
            <span class="signal good"></span>
            <span class="signal alert"></span>
            <span class="signal good"></span>
            <span class="signal good"></span>
          </div>
        </div>
      </div>
    </section>

    <section class="grid" data-animate style="--delay: 0.12s">
      <ReportsSection />
      <div class="card">
        <div class="card-header">
          <div>
            <p class="card-kicker">审批监管</p>
            <h2>关键节点</h2>
          </div>
          <span class="chip chip-accent">负责人终审</span>
        </div>
        <div class="report-list">
          <div class="report-item">
            <div>
              <h3>校外 · 产业合作</h3>
              <p>管理员初审已过，待负责人终审</p>
            </div>
            <span class="chip chip-warn">待终审</span>
          </div>
          <div class="report-item">
            <div>
              <h3>校外 · 新材料企业</h3>
              <p>缴费确认中，等待管理员最终确认</p>
            </div>
            <span class="chip chip-neutral">缴费中</span>
          </div>
          <div class="report-item">
            <div>
              <h3>校内冲突预约</h3>
              <p>跨实验室资源冲突，需复核优先级</p>
            </div>
            <span class="chip chip-alert">冲突</span>
          </div>
        </div>
      </div>
    </section>

    <section class="grid" data-animate style="--delay: 0.18s">
      <div class="card">
        <div class="card-header">
          <div>
            <p class="card-kicker">人员与制度</p>
            <h2>岗位与规范</h2>
          </div>
          <span class="chip chip-neutral">制度更新</span>
        </div>
        <div class="rule-list">
          <div class="rule-item">
            <span class="rule-title">值班排班</span>
            <span class="rule-desc">本周设备管理员排班已确认，缺岗 1 人</span>
          </div>
          <div class="rule-item">
            <span class="rule-title">审批权限</span>
            <span class="rule-desc">校外申请终审仅限负责人角色操作</span>
          </div>
          <div class="rule-item">
            <span class="rule-title">校内优先</span>
            <span class="rule-desc">资源冲突时优先处理校内申请</span>
          </div>
        </div>
      </div>
      <div class="card">
        <div class="card-header">
          <div>
            <p class="card-kicker">采购与报废</p>
            <h2>窗口管理</h2>
          </div>
          <span class="chip chip-neutral">本月计划</span>
        </div>
        <div class="report-list">
          <div class="report-item">
            <div>
              <h3>高精度显微镜</h3>
              <p>预算审核中 · 预计 6 月到货</p>
            </div>
            <span class="chip chip-warn">采购</span>
          </div>
          <div class="report-item">
            <div>
              <h3>老旧光谱仪</h3>
              <p>报废审批完成，待资产处确认</p>
            </div>
            <span class="chip chip-good">报废</span>
          </div>
          <div class="report-item">
            <div>
              <h3>设备升级包</h3>
              <p>维保升级，等待供应商排期</p>
            </div>
            <span class="chip chip-neutral">升级</span>
          </div>
        </div>
      </div>
    </section>
  </main>
</template>

<script setup>
import ReportsSection from "./ReportsSection.vue";
</script>
