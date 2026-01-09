# PowerShell 脚本: 数据库管理工具
# 用法: .\db.ps1 {init|upgrade|downgrade|revision} [message]

param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("init", "upgrade", "downgrade", "revision")]
    [string]$Command, # 执行的命令：初始化、升级、降级或生成修订版本
    [string]$Message = "auto" # 迁移消息 (仅 revision 命令需要)
)

$ErrorActionPreference = "Stop" # 遇到错误立即停止

# 计算路径
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot ".." "..")
$MigrationsDir = Join-Path $RepoRoot "db-migrations"
$AlembicIni = Join-Path $MigrationsDir "alembic.ini"

# 切换到迁移目录执行 alembic
Push-Location $MigrationsDir
try {
    # 设置 PYTHONPATH 确保 alembic 能导入 backend 代码
    $env:PYTHONPATH = $RepoRoot
    switch ($Command) {
        "init" {
            # 初始化数据库到最新版本
            alembic -c $AlembicIni upgrade head
        }
        "upgrade" {
            # 升级数据库到最新版本
            alembic -c $AlembicIni upgrade head
        }
        "downgrade" {
            # 撤销最近一次迁移
            alembic -c $AlembicIni downgrade -1
        }
        "revision" {
            # 自动检测模型变更并生成新的迁移脚本
            alembic -c $AlembicIni revision --autogenerate -m $Message
        }
    }
} finally {
    # 恢复原始目录
    Pop-Location
}
