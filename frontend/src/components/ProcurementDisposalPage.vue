<template>
  <main class="canvas">
    <section class="page-header" data-animate style="--delay: 0.05s">
      <div>
        <p class="eyebrow">设备采购 / 报废</p>
        <h1>采购计划与报废流转</h1>
        <p class="lead">
          负责人统筹设备采购、升级与报废申请，保障资产规模与预算可控。
        </p>
      </div>
      <div class="page-actions">
        <button type="button" class="ghost">新增申请</button>
        <button type="button" class="primary">提交审批</button>
      </div>
    </section>

    <section class="grid" data-animate style="--delay: 0.12s">
      <div class="card">
        <div class="card-header">
          <div>
            <p class="card-kicker">采购计划</p>
            <h2>待推进清单</h2>
          </div>
          <span class="chip chip-neutral">6 项</span>
        </div>
        <div class="report-list">
          <div class="report-item">
            <div>
              <h3>超分辨显微镜</h3>
              <p>预算评审中 · 预计 6 月到货</p>
            </div>
            <span class="chip chip-warn">采购中</span>
          </div>
          <div class="report-item">
            <div>
              <h3>激光干涉仪</h3>
              <p>招标文件已发布 · 供应商 3 家</p>
            </div>
            <span class="chip chip-neutral">招标</span>
          </div>
          <div class="report-item">
            <div>
              <h3>材料分析平台升级</h3>
              <p>维保升级方案确认中</p>
            </div>
            <span class="chip chip-good">升级</span>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <div>
            <p class="card-kicker">报废申请</p>
            <h2>资产处对接</h2>
          </div>
          <span class="chip chip-alert">3 项</span>
        </div>
        <div class="report-list">
          <div class="report-item">
            <div>
              <h3>老旧光谱仪 A-217</h3>
              <p>专家评估完成 · 等待资产处确认</p>
            </div>
            <span class="chip chip-warn">待确认</span>
          </div>
          <div class="report-item">
            <div>
              <h3>离心机 C-109</h3>
              <p>安全隐患已记录 · 报废审批通过</p>
            </div>
            <span class="chip chip-good">已通过</span>
          </div>
          <div class="report-item">
            <div>
              <h3>热分析平台 B-203</h3>
              <p>暂缓报废，等待维修评估</p>
            </div>
            <span class="chip chip-neutral">评估中</span>
          </div>
        </div>
      </div>
    </section>

    <section class="grid" data-animate style="--delay: 0.2s">
      <div class="card wide">
        <div class="card-header">
          <div>
            <p class="card-kicker">预算与进度</p>
            <h2>年度采购概览</h2>
          </div>
          <span class="chip chip-accent">2025</span>
        </div>
        <div class="stat-grid">
          <div class="stat-card">
            <p class="stat-label">采购预算</p>
            <p class="stat-value">￥ 320 万</p>
            <p class="stat-meta">已使用 58%</p>
          </div>
          <div class="stat-card">
            <p class="stat-label">报废设备</p>
            <p class="stat-value">12 台</p>
            <p class="stat-meta">本季度完成 5 台</p>
          </div>
          <div class="stat-card">
            <p class="stat-label">升级项目</p>
            <p class="stat-value">7 项</p>
            <p class="stat-meta">2 项进入验收</p>
          </div>
        </div>
      </div>
    </section>
  </main>
</template>
