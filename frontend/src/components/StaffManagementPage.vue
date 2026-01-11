<template>
  <main class="canvas">
    <section class="page-header" data-animate style="--delay: 0.05s">
      <div>
        <p class="eyebrow">员工管理</p>
        <h1>实验室人员与岗位编制</h1>
        <p class="lead">
          负责人可维护设备管理员名单、岗位分工与值班安排，确保审批与监管到位。
        </p>
      </div>
      <div class="page-actions">
        <button type="button" class="ghost">导入员工</button>
        <button type="button" class="primary">新增员工</button>
      </div>
    </section>

    <section class="grid" data-animate style="--delay: 0.12s">
      <div class="card">
        <div class="card-header">
          <div>
            <p class="card-kicker">岗位分布</p>
            <h2>当前编制</h2>
          </div>
          <span class="chip chip-neutral">本周</span>
        </div>
        <div class="stat-grid">
          <div class="stat-card">
            <p class="stat-label">设备管理员</p>
            <p class="stat-value">9 人</p>
            <p class="stat-meta">含夜间值班 3 人</p>
          </div>
          <div class="stat-card">
            <p class="stat-label">实验室助理</p>
            <p class="stat-value">6 人</p>
            <p class="stat-meta">覆盖 4 个实验室</p>
          </div>
          <div class="stat-card">
            <p class="stat-label">安全与审计</p>
            <p class="stat-value">2 人</p>
            <p class="stat-meta">巡检本周 4 次</p>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <div>
            <p class="card-kicker">变更记录</p>
            <h2>最近调整</h2>
          </div>
          <span class="chip chip-neutral">留痕</span>
        </div>
        <div class="report-list">
          <div class="report-item">
            <div>
              <h3>李珊珊</h3>
              <p>新增为设备管理员 · 2025-04-10</p>
            </div>
            <span class="chip chip-good">新增</span>
          </div>
          <div class="report-item">
            <div>
              <h3>赵云峰</h3>
              <p>岗位调整为安全审计 · 2025-04-09</p>
            </div>
            <span class="chip chip-warn">调整</span>
          </div>
          <div class="report-item">
            <div>
              <h3>王琳</h3>
              <p>离职交接完成 · 2025-04-08</p>
            </div>
            <span class="chip chip-neutral">离职</span>
          </div>
        </div>
      </div>
    </section>

    <section class="grid" data-animate style="--delay: 0.2s">
      <div class="card wide">
        <div class="card-header">
          <div>
            <p class="card-kicker">值班与授权</p>
            <h2>岗位安排</h2>
          </div>
          <span class="chip chip-accent">按实验室</span>
        </div>
        <div class="approval-queue">
          <div class="approval-card">
            <div>
              <h3>材料实验室</h3>
              <p>值班：李珊珊 / 朱铭 · 08:00 - 20:00</p>
              <div class="chip-row">
                <span class="chip chip-good">在岗</span>
                <span class="chip chip-neutral">审批权限已授权</span>
              </div>
            </div>
            <div class="approval-actions">
              <button type="button" class="ghost">调整排班</button>
            </div>
          </div>
          <div class="approval-card">
            <div>
              <h3>光学实验室</h3>
              <p>值班：周天琪 · 10:00 - 18:00</p>
              <div class="chip-row">
                <span class="chip chip-warn">需补岗</span>
                <span class="chip chip-neutral">夜班缺口 1 人</span>
              </div>
            </div>
            <div class="approval-actions">
              <button type="button" class="primary">安排值班</button>
            </div>
          </div>
          <div class="approval-card">
            <div>
              <h3>化学实验室</h3>
              <p>值班：冯思雨 / 赵云峰 · 24 小时覆盖</p>
              <div class="chip-row">
                <span class="chip chip-good">覆盖充分</span>
                <span class="chip chip-neutral">审批链正常</span>
              </div>
            </div>
            <div class="approval-actions">
              <button type="button" class="ghost">查看详情</button>
            </div>
          </div>
        </div>
      </div>
    </section>
  </main>
</template>
