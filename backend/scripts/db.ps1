param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("init", "upgrade", "downgrade", "revision")]
    [string]$Command,
    [string]$Message = "auto"
)

$ErrorActionPreference = "Stop"
<<<<<<< HEAD

$RepoRoot = (Get-Item $PSScriptRoot).Parent.Parent.FullName
=======
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot ".." "..")
>>>>>>> origin/develop
$MigrationsDir = Join-Path $RepoRoot "db-migrations"
$AlembicIni = Join-Path $MigrationsDir "alembic.ini"

Push-Location $MigrationsDir
try {
    $env:PYTHONPATH = $RepoRoot
    switch ($Command) {
<<<<<<< HEAD
        "init"      { alembic -c $AlembicIni upgrade head }
        "upgrade"   { alembic -c $AlembicIni upgrade head }
        "downgrade" { alembic -c $AlembicIni downgrade -1 }
        "revision"  { alembic -c $AlembicIni revision --autogenerate -m $Message }
    }
}
finally {
=======
        "init" { alembic -c $AlembicIni upgrade head }
        "upgrade" { alembic -c $AlembicIni upgrade head }
        "downgrade" { alembic -c $AlembicIni downgrade -1 }
        "revision" { alembic -c $AlembicIni revision --autogenerate -m $Message }
    }
} finally {
>>>>>>> origin/develop
    Pop-Location
}
