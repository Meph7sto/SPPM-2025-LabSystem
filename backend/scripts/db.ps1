param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("init", "upgrade", "downgrade", "revision")]
    [string]$Command,
    [string]$Message = "auto"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot ".." "..")
$MigrationsDir = Join-Path $RepoRoot "db-migrations"
$AlembicIni = Join-Path $MigrationsDir "alembic.ini"

Push-Location $MigrationsDir
try {
    $env:PYTHONPATH = $RepoRoot
    switch ($Command) {
        "init" { alembic -c $AlembicIni upgrade head }
        "upgrade" { alembic -c $AlembicIni upgrade head }
        "downgrade" { alembic -c $AlembicIni downgrade -1 }
        "revision" { alembic -c $AlembicIni revision --autogenerate -m $Message }
    }
} finally {
    Pop-Location
}