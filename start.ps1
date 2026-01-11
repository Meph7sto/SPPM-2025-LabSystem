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
Write-Host "LESMS 一键启动脚本" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "按 Ctrl+C 停止服务器" -ForegroundColor Yellow

uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 11451
