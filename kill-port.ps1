param(
    [int[]]$Ports = @(11451, 5173),
    [switch]$Force
)

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  LESMS 端口清理脚本" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

foreach ($Port in $Ports) {
    Write-Host "检查端口 $Port..." -ForegroundColor Yellow
    $pids = @()

    # 尝试使用 Get-NetTCPConnection (较快)
    try {
        $tcp = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
        if ($tcp) {
            $pids += $tcp | Select-Object -ExpandProperty OwningProcess
        }
    } catch {}

    # 尝试使用 Get-NetUDPEndpoint
    try {
        $udp = Get-NetUDPEndpoint -LocalPort $Port -ErrorAction SilentlyContinue
        if ($udp) {
            $pids += $udp | Select-Object -ExpandProperty OwningProcess
        }
    } catch {}

    # 如果上述方法未找到，使用 netstat 作为后备
    if (-not $pids) {
        $netstat = netstat -ano | Select-String ":$Port\s+.*LISTENING"
        if ($netstat) {
            foreach ($line in $netstat) {
                if ($line -match '\s+(\d+)\s*$') {
                    $pids += $matches[1]
                }
            }
        }
    }

    $pids = $pids | Where-Object { $_ -and $_ -ne 0 } | Sort-Object -Unique

    if (-not $pids) {
        Write-Host "      端口 $Port 未被占用" -ForegroundColor Green
        continue
    }

    foreach ($processId in $pids) {
        $proc = Get-Process -Id $processId -ErrorAction SilentlyContinue
        if ($proc) {
            $name = $proc.ProcessName
            try {
                if ($Force) {
                    Stop-Process -Id $processId -Force
                    Write-Host "      已强制强制结束 $name (PID: $processId) 占用的端口 $Port" -ForegroundColor Green
                } else {
                    Stop-Process -Id $processId
                    Write-Host "      已结束 $name (PID: $processId) 占用的端口 $Port" -ForegroundColor Green
                }
            } catch {
                Write-Host "      [错误] 无法结束 PID $processId (端口 $Port): $($_.Exception.Message)" -ForegroundColor Red
            }
        } else {
            Write-Host "      未找到相关的进程 (PID: $processId)" -ForegroundColor Gray
        }
    }
}

Write-Host ""
Write-Host "清理任务完成。" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
