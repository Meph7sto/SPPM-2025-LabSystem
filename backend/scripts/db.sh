#!/usr/bin/env bash
# Shell 脚本: 数据库管理工具
# 用法: ./db.sh {init|upgrade|downgrade|revision} [message]

set -euo pipefail

command="${1:-}"
message="${2:-auto}"

# 计算路径
root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
migrations_dir="${root_dir}/db-migrations"
alembic_ini="${migrations_dir}/alembic.ini"

# 设置 PYTHONPATH 确保 alembic 能导入 backend 代码
export PYTHONPATH="${root_dir}"

case "${command}" in
  init|upgrade)
    # 初始化/升级数据库到最新版本
    (cd "${migrations_dir}" && alembic -c "${alembic_ini}" upgrade head)
    ;;
  downgrade)
    # 撤销最近一次迁移
    (cd "${migrations_dir}" && alembic -c "${alembic_ini}" downgrade -1)
    ;;
  revision)
    # 自动检测模型变更并生成新的迁移脚本
    (cd "${migrations_dir}" && alembic -c "${alembic_ini}" revision --autogenerate -m "${message}")
    ;;
  *)
    echo "Usage: $0 {init|upgrade|downgrade|revision} [message]" >&2
    exit 1
    ;;
esac
