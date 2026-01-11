param(
    [string]$EnvName = "lesms",
    [switch]$SkipFrontend,
    [switch]$SkipMigrate,
    [switch]$CleanDB
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path $PSScriptRoot
Set-Location $RepoRoot

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  LESMS 一键启动脚本" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# 检查 conda
if (-not (Get-Command conda -ErrorAction SilentlyContinue)) {
    Write-Host "[错误] 未找到 Conda。请在 Anaconda Prompt 中运行此脚本，或将 conda 添加到 PATH。" -ForegroundColor Red
    exit 1
}

$CondaBase = (& conda info --base).Trim()
$CondaHook = Join-Path $CondaBase "shell\condabin\conda-hook.ps1"
if (-not (Test-Path $CondaHook)) {
    Write-Host "[错误] 未找到 Conda hook: $CondaHook" -ForegroundColor Red
    exit 1
}

. $CondaHook

# 检查并创建 conda 环境
Write-Host "[1/7] 检查 Conda 环境..." -ForegroundColor Yellow
$envExists = $false
$envList = conda env list --json | ConvertFrom-Json
foreach ($envPath in $envList.envs) {
    if ((Split-Path $envPath -Leaf) -eq $EnvName) {
        $envExists = $true
        break
    }
}

if (-not $envExists) {
    Write-Host "      创建 conda 环境 '$EnvName'..." -ForegroundColor Green
    conda create -y -n $EnvName python=3.11
}
else {
    Write-Host "      Conda 环境 '$EnvName' 已存在" -ForegroundColor Green
}

Write-Host "      激活环境 '$EnvName'..." -ForegroundColor Green
conda activate $EnvName

# 创建 .env 文件
Write-Host "[2/7] 检查配置文件..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "      已从 .env.example 创建 .env" -ForegroundColor Green
}
else {
    Write-Host "      .env 已存在" -ForegroundColor Green
}

# 解析和创建数据库目录
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

Write-Host "[3/7] 准备数据库..." -ForegroundColor Yellow
$dbUrl = Get-EnvValue ".env" "DB_URL"
if ($dbUrl -and $dbUrl -match '^sqlite:///') {
    if ($dbUrl -ne 'sqlite:///:memory:') {
        $pathPart = $dbUrl -replace '^sqlite:///', ''
        if ($pathPart.StartsWith('./') -or $pathPart.StartsWith('.\')) {
            $pathPart = $pathPart.Substring(2)
        }
        if ([System.IO.Path]::IsPathRooted($pathPart)) {
            $dbFile = $pathPart
        }
        else {
            $dbFile = Join-Path $RepoRoot $pathPart
        }
        $dbDir = Split-Path $dbFile -Parent
        if ($dbDir -and -not (Test-Path $dbDir)) {
            New-Item -ItemType Directory -Force -Path $dbDir | Out-Null
            Write-Host "      创建数据库目录: $dbDir" -ForegroundColor Green
        }
        
        # 清理数据库（如果指定）
        if ($CleanDB -and (Test-Path $dbFile)) {
            Remove-Item $dbFile -Force
            Write-Host "      已删除旧数据库文件" -ForegroundColor Yellow
        }
        
        Write-Host "      数据库文件: $dbFile" -ForegroundColor Green
    }
}

# 安装后端依赖
Write-Host "[4/7] 安装后端依赖..." -ForegroundColor Yellow
pip install -q -r backend/requirements.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "      后端依赖安装完成" -ForegroundColor Green
}
else {
    Write-Host "      [警告] 后端依赖安装可能有问题" -ForegroundColor Yellow
}

# 运行数据库迁移
if (-not $SkipMigrate) {
    Write-Host "[5/7] 初始化数据库..." -ForegroundColor Yellow
    $dbScriptPath = "$RepoRoot\backend\scripts\db.ps1"
    if (Test-Path $dbScriptPath) {
        try {
            & $dbScriptPath init
            Write-Host "      数据库初始化完成" -ForegroundColor Green
        }
        catch {
            Write-Host "      [警告] 数据库初始化失败: $_" -ForegroundColor Yellow
            Write-Host "      尝试继续运行..." -ForegroundColor Yellow
        }
    }
    else {
        Write-Host "      [警告] 未找到数据库脚本: $dbScriptPath" -ForegroundColor Yellow
    }
}
else {
    Write-Host "[5/7] 跳过数据库迁移 (使用了 -SkipMigrate)" -ForegroundColor Yellow
}

# 安装前端依赖并启动
if (-not $SkipFrontend) {
    Write-Host "[6/7] 准备前端..." -ForegroundColor Yellow
    $frontendDir = Join-Path $RepoRoot "frontend"
    if (Test-Path (Join-Path $frontendDir "package.json")) {
        if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
            Write-Host "      [警告] 未找到 npm，跳过前端" -ForegroundColor Yellow
        }
        else {
            if (-not (Test-Path (Join-Path $frontendDir "node_modules"))) {
                Write-Host "      安装前端依赖..." -ForegroundColor Green
                Push-Location $frontendDir
                npm install
                Pop-Location
            }
            else {
                Write-Host "      前端依赖已存在" -ForegroundColor Green
            }
            Write-Host "      启动前端开发服务器..." -ForegroundColor Green
            $frontendCommand = "cd `"$frontendDir`"; Write-Host 'Frontend: http://localhost:5173' -ForegroundColor Cyan; npm run dev -- --host"
            Start-Process -FilePath "powershell" -ArgumentList "-NoLogo", "-NoExit", "-Command", $frontendCommand
            Start-Sleep -Seconds 1
        }
    }
}
else {
    Write-Host "[6/7] 跳过前端 (使用了 -SkipFrontend)" -ForegroundColor Yellow
}

Write-Host "[7/7] 启动后端 API 服务器..." -ForegroundColor Yellow

# 检查端口 11451 是否被占用
$portInUse = netstat -ano | Select-String ":11451.*LISTENING"
if ($portInUse) {
    Write-Host "      [警告] 端口 11451 已被占用" -ForegroundColor Yellow
    Write-Host "      正在尝试释放端口..." -ForegroundColor Yellow
    
    $processIds = $portInUse | ForEach-Object {
        if ($_ -match '\s+(\d+)\s*$') {
            $matches[1]
        }
    } | Select-Object -Unique
    
    foreach ($processId in $processIds) {
        try {
            $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
            if ($process -and $process.ProcessName -match "python|uvicorn") {
                Write-Host "      终止旧的后端进程 (PID: $processId)..." -ForegroundColor Yellow
                Stop-Process -Id $processId -Force
                Start-Sleep -Seconds 2
            }
        }
        catch {
            Write-Host "      无法终止进程 $processId，请手动处理" -ForegroundColor Red
        }
    }
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  服务已启动！" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  后端 API: http://localhost:11451" -ForegroundColor Green
Write-Host "  API 文档: http://localhost:11451/api/v1/docs" -ForegroundColor Green
if (-not $SkipFrontend) {
    Write-Host "  前端应用: http://localhost:5173" -ForegroundColor Green
}
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "按 Ctrl+C 停止服务器" -ForegroundColor Yellow
Write-Host ""

uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 11451