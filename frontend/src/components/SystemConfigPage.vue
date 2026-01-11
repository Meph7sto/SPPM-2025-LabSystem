<template>
  <main class="canvas">
    <section class="page-header" data-animate style="--delay: 0.05s">
      <div>
        <p class="eyebrow">系统配置</p>
        <h1>流程、权限与策略设置</h1>
        <p class="lead">
          负责人可配置审批链、访问范围与通知策略，确保业务规则落地执行。
        </p>
      </div>
      <div class="page-actions">
        <button type="button" class="ghost">查看配置快照</button>
        <button type="button" class="primary">保存配置</button>
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
            <span class="rule-desc">管理员初审 → 负责人终审 → 缴费确认</span>
          </div>
          <div class="rule-item">
            <span class="rule-title">校内学生审批</span>
            <span class="rule-desc">导师审批 → 管理员审批</span>
          </div>
          <div class="rule-item">
            <span class="rule-title">权限分配</span>
            <span class="rule-desc">负责人可配置审批人、停用账号与审计策略</span>
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
            <span class="rule-desc">工作人员端仅允许校内 IP 访问</span>
          </div>
          <div class="rule-item">
            <span class="rule-title">通知触发</span>
            <span class="rule-desc">提交、审批、缴费、撤销节点自动提醒</span>
          </div>
          <div class="rule-item">
            <span class="rule-title">定时任务</span>
            <span class="rule-desc">周报/月报/年报自动生成并归档</span>
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
