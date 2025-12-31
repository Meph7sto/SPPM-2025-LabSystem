#!/usr/bin/env bash
set -euo pipefail

command="${1:-}"
message="${2:-auto}"
root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
migrations_dir="${root_dir}/db-migrations"
alembic_ini="${migrations_dir}/alembic.ini"

export PYTHONPATH="${root_dir}"

case "${command}" in
  init|upgrade)
    (cd "${migrations_dir}" && alembic -c "${alembic_ini}" upgrade head)
    ;;
  downgrade)
    (cd "${migrations_dir}" && alembic -c "${alembic_ini}" downgrade -1)
    ;;
  revision)
    (cd "${migrations_dir}" && alembic -c "${alembic_ini}" revision --autogenerate -m "${message}")
    ;;
  *)
    echo "Usage: $0 {init|upgrade|downgrade|revision} [message]" >&2
    exit 1
    ;;
esac
