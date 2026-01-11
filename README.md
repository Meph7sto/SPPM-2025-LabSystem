# LESMS

Laboratory Equipment Service Management System for Jiangnan University.

实验室设备服务管理系统 - 江南大学

## 📋 项目结构

```
SPPM-2025-LabSystem/
├── backend/          # FastAPI 后端服务
├── frontend/         # Vue3 前端应用
├── db-migrations/    # Alembic 数据库迁移脚本
├── docs/            # 系统文档
└── start.ps1        # 一键启动脚本（Windows/Conda）
```

## 🚀 快速启动（推荐）

### 使用一键启动脚本（Windows + Conda）

在 **Anaconda Prompt** 或已配置 Conda 的 PowerShell 中运行：

```powershell
# 进入项目目录
cd SPPM-2025-LabSystem

# 一键启动（会自动创建环境、安装依赖、初始化数据库、启动前后端）
.\start.ps1
```

**脚本参数说明：**
- `-EnvName "自定义名称"` - 指定 conda 环境名（默认: lesms）
- `-SkipFrontend` - 仅启动后端，跳过前端
- `-SkipMigrate` - 跳过数据库迁移
- `-CleanDB` - 清空并重新初始化数据库

**示例：**
```powershell
# 重新初始化数据库
.\start.ps1 -CleanDB

# 仅启动后端
.\start.ps1 -SkipFrontend

# 使用自定义环境名
.\start.ps1 -EnvName "my-lesms-env"
```

### 服务地址

启动成功后可访问：

- **前端应用**: http://localhost:5173
- **后端 API**: http://localhost:11451
- **API 文档**: http://localhost:11451/api/v1/docs （Swagger UI）
- **API 文档（备选）**: http://localhost:11451/api/v1/redoc （ReDoc）

## 🛠️ 手动启动（开发者）

### 1. 环境要求

- Python 3.11+
- Node.js 18+
- Conda（推荐）或 venv
- SQLite（内置）或 PostgreSQL

### 2. 后端启动

```powershell
# 创建并激活 conda 环境
conda create -n lesms python=3.11
conda activate lesms

# 安装依赖
pip install -r backend/requirements.txt

# 创建配置文件
copy .env.example .env

# 初始化数据库
.\backend\scripts\db.ps1 init

# 启动后端
uvicorn backend.app.main:app --reload
```

### 3. 前端启动

```powershell
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 🗄️ 数据库配置

默认使用 SQLite，数据库文件位于 `data/lesms.db`。

如需使用 PostgreSQL，修改 `.env` 文件：

```env
# SQLite（默认）
DB_URL=sqlite:///./data/lesms.db

# PostgreSQL
DB_URL=postgresql+psycopg://lesms:lesms@localhost:5432/lesms
```

### 数据库管理命令

```powershell
# 初始化数据库
.\backend\scripts\db.ps1 init

# 创建迁移
.\backend\scripts\db.ps1 migrate "描述信息"

# 升级到最新版本
.\backend\scripts\db.ps1 upgrade

# 回滚一个版本
.\backend\scripts\db.ps1 downgrade
```

## 📚 API 使用指南

### 认证流程

1. **注册用户**
```bash
POST /api/v1/auth/register
{
  "role": "student",          # teacher/student/external
  "name": "张三",
  "contact": "13800138000",
  "college": "计算机学院",
  "student_no": "S20251234",
  "advisor_no": "T20200001",
  "password": "password123"
}
```

2. **登录获取 Token**
```bash
POST /api/v1/auth/login
{
  "account": "S20251234",
  "password": "password123",
  "role": "student"           # teacher/student/external/admin/head
}
```

3. **使用 Token 访问受保护接口**
```bash
GET /api/v1/auth/me
Headers: Authorization: Bearer <your_token>
```

### 个人资料管理

```bash
# 获取个人资料
GET /api/v1/users/me/profile

# 更新个人资料
PUT /api/v1/users/me/profile
{
  "name": "李四",
  "contact": "13900139000",
  "college": "材料学院"
}
```

## 🧪 测试

测试数据会在首次运行时自动创建。默认用户：

| 角色 | 账号 | 密码 | 说明 |
|------|------|------|------|
| 管理员 | admin | admin123 | 设备管理员 |
| 负责人 | head | head123 | 实验室负责人 |
| 教师 | T001 | teacher123 | 校内教师 |
| 学生 | S001 | student123 | 校内学生 |

## 📝 开发说明

### 技术栈

**后端:**
- FastAPI - 现代高性能 Web 框架
- SQLAlchemy - ORM
- Alembic - 数据库迁移
- Pydantic - 数据验证
- JWT - 身份认证

**前端:**
- Vue 3 - 渐进式框架
- Vite - 构建工具
- Vanilla CSS - 样式

### 项目规范

- 后端遵循 REST API 设计规范
- 统一的错误码和返回格式
- 基于角色的访问控制（RBAC）
- 所有接口需要认证（除注册/登录）

## 🔧 故障排查

### 常见问题

**1. Conda 环境激活失败**
```powershell
# 确保在 Anaconda Prompt 中运行
# 或手动初始化 conda
conda init powershell
```

**2. 数据库初始化失败**
```powershell
# 删除旧数据库并重新初始化
.\start.ps1 -CleanDB
```

**3. 端口被占用**
```powershell
# 使用项目内置脚本清理占用端口
.\kill-port.ps1

# 如果需要强制终止：
.\kill-port.ps1 -Force
```

**4. 前端无法连接后端**
- 确保后端已启动（http://localhost:11451）
- 检查浏览器控制台的 CORS 错误
- 确认 API_BASE_URL 配置正确（frontend/src/api.js）

## 📖 更多文档

详细文档请查看 `docs/` 目录。

## 📄 License

Copyright © 2025 Jiangnan University

