<template>
  <div class="card wide">
    <div class="card-header">
      <div>
        <p class="card-kicker">可用性矩阵</p>
        <h2>设备 A-417 时间线</h2>
      </div>
      <span class="chip chip-good">无冲突</span>
    </div>
    <div class="matrix">
      <div class="matrix-row head">
        <span>时间</span>
        <span>周一</span>
        <span>周二</span>
        <span>周三</span>
        <span>周四</span>
        <span>周五</span>
      </div>
      <div class="matrix-row">
        <span>08:00</span>
        <span class="slot free">可用</span>
        <span class="slot busy">已占用</span>
        <span class="slot free">可用</span>
        <span class="slot busy">已占用</span>
        <span class="slot free">可用</span>
      </div>
      <div class="matrix-row">
        <span>10:00</span>
        <span class="slot busy">已占用</span>
        <span class="slot busy">已占用</span>
        <span class="slot free">可用</span>
        <span class="slot free">可用</span>
        <span class="slot free">可用</span>
      </div>
      <div class="matrix-row">
        <span>14:00</span>
        <span class="slot free">可用</span>
        <span class="slot maint">检修</span>
        <span class="slot free">可用</span>
        <span class="slot free">可用</span>
        <span class="slot busy">已占用</span>
      </div>
      <div class="matrix-row">
        <span>18:00</span>
        <span class="slot free">可用</span>
        <span class="slot free">可用</span>
        <span class="slot free">可用</span>
        <span class="slot busy">已占用</span>
        <span class="slot free">可用</span>
      </div>
    </div>
  </div>
</template>
