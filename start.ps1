param(
    [string]$EnvName = "lesms",
    [switch]$SkipFrontend,
    [switch]$SkipMigrate
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path $PSScriptRoot
Set-Location $RepoRoot

if (-not (Get-Command conda -ErrorAction SilentlyContinue)) {
    Write-Error "Conda not found on PATH. Open an Anaconda Prompt or add conda to PATH."
    exit 1
}

$CondaBase = (& conda info --base).Trim()
$CondaHook = Join-Path $CondaBase "shell\condabin\conda-hook.ps1"
if (-not (Test-Path $CondaHook)) {
    Write-Error "Conda hook not found: $CondaHook"
    exit 1
}

. $CondaHook

$envExists = $false
$envList = conda env list --json | ConvertFrom-Json
foreach ($envPath in $envList.envs) {
    if ((Split-Path $envPath -Leaf) -eq $EnvName) {
        $envExists = $true
        break
    }
}

if (-not $envExists) {
    Write-Host "Creating conda env '$EnvName'..."
    conda create -y -n $EnvName python=3.11
}

conda activate $EnvName

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example. Please update DB_URL if needed."
}

function Get-EnvValue([string]$Path, [string]$Name) {
    if (-not (Test-Path $Path)) {
        return $null
    }
    $pattern = "^\s*$Name\s*="
    $line = Get-Content $Path | Where-Object { $_ -match $pattern } | Select-Object -First 1
    if (-not $line) {
        return $null
    }
    return ($line -replace $pattern, "").Trim()
}

$dbUrl = Get-EnvValue ".env" "DB_URL"
if ($dbUrl -and $dbUrl -match '^sqlite:///') {
    if ($dbUrl -ne 'sqlite:///:memory:') {
        $pathPart = $dbUrl -replace '^sqlite:///', ''
        if ($pathPart.StartsWith('./') -or $pathPart.StartsWith('.\\')) {
            $pathPart = $pathPart.Substring(2)
        }
        if ([System.IO.Path]::IsPathRooted($pathPart)) {
            $dbFile = $pathPart
        } else {
            $dbFile = Join-Path $RepoRoot $pathPart
        }
        $dbDir = Split-Path $dbFile -Parent
        if ($dbDir -and -not (Test-Path $dbDir)) {
            New-Item -ItemType Directory -Force -Path $dbDir | Out-Null
        }
    }
}

Write-Host "Installing backend dependencies..."
pip install -r backend/requirements.txt

if (-not $SkipMigrate) {
    Write-Host "Running database migrations..."
    & "$RepoRoot\backend\scripts\db.ps1" init
}

if (-not $SkipFrontend) {
    $frontendDir = Join-Path $RepoRoot "frontend"
    if (Test-Path (Join-Path $frontendDir "package.json")) {
        if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
            Write-Warning "npm not found. Skipping frontend."
        } else {
            if (-not (Test-Path (Join-Path $frontendDir "node_modules"))) {
                Write-Host "Installing frontend dependencies..."
                Push-Location $frontendDir
                npm install
                Pop-Location
            }
            $frontendCommand = "cd `"$frontendDir`"; npm run dev -- --host"
            Start-Process -FilePath "powershell" -ArgumentList "-NoLogo", "-NoExit", "-Command", $frontendCommand | Out-Null
        }
    }
}

Write-Host "Starting API server..."
uvicorn backend.app.main:app --reload
