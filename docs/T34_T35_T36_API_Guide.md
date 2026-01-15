# T34-T36 借出/归还登记与设备状态自动更新 API 指南

本文档说明 T34（借出登记）、T35（归还登记）和 T36（设备状态自动更新）功能的使用方法。

## 功能概述

### T34 - 借出登记（FR-25）
管理员在用户取走设备时进行借出登记，记录：
- 借出时间（自动记录为当前时间）
- 交接备注（设备状态、配件清单等）
- 预约状态更新为 `BORROWED`
- **设备状态自动更新为 `IN_USE`**（T36）

### T35 - 归还登记（FR-26）
管理员在用户归还设备时进行归还登记，记录：
- 归还时间（自动记录为当前时间）
- 归还备注（设备使用情况等）
- 设备当前状态（正常/损坏/待检修）
- 预约状态更新为 `COMPLETED`
- **设备状态自动更新**（T36）：
  - `normal` → 设备状态 `IDLE`（空闲）
  - `damaged` 或 `needs_maintenance` → 设备状态 `MAINTENANCE`（检修中）

### T36 - 设备状态自动更新
系统自动根据预约/借出/归还/检修操作更新设备状态：
1. **借出时**：设备状态 → `IN_USE`（使用中）
2. **归还时**：根据设备状态 → `IDLE`（正常）或 `MAINTENANCE`（损坏/待检修）
3. **设置检修窗口时**：设备状态 → `MAINTENANCE`（已在原有代码中实现）

## API 接口

### 1. 借出登记（T34）

**端点：** `POST /api/v1/reservations/{reservation_id}/borrow`

**权限：** 仅管理员（ADMIN）

**请求体：**
```json
{
  "handover_note": "设备状态良好，配件齐全：主机×1、电源线×1、说明书×1"
}
```

**字段说明：**
- `handover_note`（可选）：交接备注，最多 500 字符

**前置条件：**
- 预约状态必须为 `EFFECTIVE`（已生效）

**响应示例：**
```json
{
  "code": "OK",
  "message": "借出登记成功",
  "data": {
    "id": 123,
    "status": "borrowed",
    "borrow_time": "2026-01-15T10:30:00Z",
    "handover_note": "设备状态良好，配件齐全：主机×1、电源线×1、说明书×1",
    "device": {
      "id": 45,
      "device_no": "A001",
      "status": "in_use"
    },
    ...
  }
}
```

**错误情况：**
- `INVALID_REQUEST`: 预约状态不是 `EFFECTIVE`
- `NOT_FOUND`: 预约或设备不存在
- `INVALID_REQUEST`: 设备已报废

### 2. 归还登记（T35）

**端点：** `POST /api/v1/reservations/{reservation_id}/return`

**权限：** 仅管理员（ADMIN）

**请求体：**
```json
{
  "return_note": "设备使用正常，无损坏",
  "device_condition": "normal"
}
```

**字段说明：**
- `return_note`（可选）：归还备注，最多 500 字符
- `device_condition`（必填）：设备状态，可选值：
  - `normal`：正常（设备将变为 IDLE）
  - `damaged`：损坏（设备将变为 MAINTENANCE）
  - `needs_maintenance`：待检修（设备将变为 MAINTENANCE）

**前置条件：**
- 预约状态必须为 `BORROWED`（已借出）

**响应示例：**
```json
{
  "code": "OK",
  "message": "归还登记成功，设备状态：normal",
  "data": {
    "id": 123,
    "status": "completed",
    "borrow_time": "2026-01-15T10:30:00Z",
    "return_time": "2026-01-16T14:20:00Z",
    "handover_note": "设备状态良好，配件齐全：主机×1、电源线×1、说明书×1",
    "return_note": "设备使用正常，无损坏",
    "device": {
      "id": 45,
      "device_no": "A001",
      "status": "idle"
    },
    ...
  }
}
```

**错误情况：**
- `INVALID_REQUEST`: 预约状态不是 `BORROWED`
- `INVALID_REQUEST`: `device_condition` 值无效
- `NOT_FOUND`: 预约或设备不存在

## 前端调用示例

### JavaScript/Vue 调用

```javascript
import { reservationAPI } from './api.js';

// 借出登记
async function borrowEquipment(reservationId) {
  try {
    const result = await reservationAPI.borrow(reservationId, {
      handover_note: "设备状态良好，配件齐全"
    });
    console.log("借出成功:", result.data);
    alert(result.message);
  } catch (error) {
    console.error("借出失败:", error);
    alert("借出登记失败: " + error.message);
  }
}

// 归还登记
async function returnEquipment(reservationId, condition) {
  try {
    const result = await reservationAPI.return(reservationId, {
      return_note: "设备使用正常",
      device_condition: condition // "normal", "damaged", 或 "needs_maintenance"
    });
    console.log("归还成功:", result.data);
    alert(result.message);
  } catch (error) {
    console.error("归还失败:", error);
    alert("归还登记失败: " + error.message);
  }
}
```

## 设备状态流转图（T36）

```
预约创建 → 审批通过 → 最终确认
                          ↓
                     EFFECTIVE (已生效)
                          ↓
                    【借出登记】T34
                          ↓
            设备状态: IDLE → IN_USE
            预约状态: EFFECTIVE → BORROWED
                          ↓
                    【归还登记】T35
                          ↓
            ┌─────────────┴─────────────┐
            ↓                           ↓
      normal (正常)              damaged/needs_maintenance
            ↓                           ↓
   设备状态: IN_USE → IDLE      设备状态: IN_USE → MAINTENANCE
   预约状态: BORROWED → COMPLETED  预约状态: BORROWED → COMPLETED
```

## 业务流程

### 完整借用流程

1. **用户提交预约** → `PENDING`
2. **审批流程** → `ADVISOR_APPROVED` / `ADMIN_APPROVED` / `HEAD_APPROVED`
3. **支付确认**（校外）→ `PAID`
4. **最终确认** → `EFFECTIVE`（已生效，可借出）
   - 设备状态：`IDLE`（空闲，可预约）
5. **【借出登记】** → `BORROWED`（已借出）✨ T34
   - 设备状态：`IDLE` → `IN_USE`（使用中）✨ T36
6. **【归还登记】** → `COMPLETED`（已完成）✨ T35
   - 设备状态：`IN_USE` → `IDLE` 或 `MAINTENANCE`（根据设备状态）✨ T36

## 注意事项

1. **权限控制**：借出和归还登记仅限管理员操作
2. **状态校验**：
   - 借出前必须确保预约状态为 `EFFECTIVE`
   - 归还前必须确保预约状态为 `BORROWED`
3. **设备状态**：设备状态会自动更新，无需手动修改
4. **报废设备**：已报废设备无法借出
5. **时间记录**：借出和归还时间自动记录为当前服务器时间（UTC）
6. **交接备注**：建议在借出时详细记录设备状态和配件清单，方便归还时核对

## 数据库字段

### Reservation 表相关字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `borrow_time` | DateTime | 实际借出时间 |
| `return_time` | DateTime | 实际归还时间 |
| `handover_note` | Text | 交接备注（借出时填写）|
| `return_note` | Text | 归还备注（归还时填写）|
| `status` | Enum | 预约状态 |

### Device 表相关字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `status` | Enum | 设备状态（idle/in_use/maintenance/scrapped）|

## 扩展可能性

未来可以考虑以下扩展：
1. 设备归还时拍照上传功能
2. 设备损坏程度分级
3. 维修工单自动生成（设备状态为 damaged 时）
4. 设备使用时长统计
5. 超期自动计算超期费用

## 测试建议

1. **正常流程测试**：
   - 创建预约 → 审批通过 → 最终确认 → 借出 → 归还
   - 验证设备状态在各阶段的正确性

2. **异常流程测试**：
   - 尝试在非 EFFECTIVE 状态下借出
   - 尝试在非 BORROWED 状态下归还
   - 测试设备状态错误输入

3. **权限测试**：
   - 非管理员用户尝试借出/归还（应被拒绝）

4. **设备状态测试**：
   - 归还时选择不同的设备状态，验证设备状态更新是否正确
