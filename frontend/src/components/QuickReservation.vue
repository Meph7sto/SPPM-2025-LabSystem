<template>
  <div class="card">
    <div class="card-header">
      <div>
        <p class="card-kicker">快捷预约</p>
        <h2>借用申请</h2>
      </div>
      <span class="chip chip-warn">最小 2 小时</span>
    </div>
    <form class="form">
      <label>
        设备
        <select>
          <option>A-417 光谱仪</option>
          <option>B-203 热分析平台</option>
          <option>C-118 光学平台</option>
        </select>
      </label>
      <label>
        时间段
        <select>
          <option>4 月 12 日 08:00 - 10:00</option>
          <option>4 月 13 日 10:00 - 12:00</option>
          <option>4 月 15 日 14:00 - 16:00</option>
        </select>
      </label>
      <label>
        用途
        <input type="text" placeholder="项目编号或实验目标" />
      </label>
      <button type="button" class="primary">提交申请</button>
    </form>
  </div>
</template>
