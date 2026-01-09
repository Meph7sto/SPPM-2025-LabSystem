param(
    [Parameter(Mandatory = $true)]
    [int]$Port,
    [switch]$Force
)

$pids = @()

try {
    $tcp = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    if ($tcp) {
        $pids += $tcp | Select-Object -ExpandProperty OwningProcess
    }
} catch {
    Write-Host "Get-NetTCPConnection not available or failed: $($_.Exception.Message)"
}

try {
    $udp = Get-NetUDPEndpoint -LocalPort $Port -ErrorAction SilentlyContinue
    if ($udp) {
        $pids += $udp | Select-Object -ExpandProperty OwningProcess
    }
} catch {
    Write-Host "Get-NetUDPEndpoint not available or failed: $($_.Exception.Message)"
}

$pids = $pids | Where-Object { $_ -and $_ -ne 0 } | Sort-Object -Unique

if (-not $pids) {
    Write-Host "No process is using port $Port."
    exit 0
}

foreach ($pid in $pids) {
    $proc = Get-Process -Id $pid -ErrorAction SilentlyContinue
    if (-not $proc) {
        Write-Host "Process $pid not found."
        continue
    }

    $name = $proc.ProcessName
    if ($Force) {
        Stop-Process -Id $pid -Force
        Write-Host "Killed $name (PID $pid) on port $Port."
    } else {
        Stop-Process -Id $pid
        Write-Host "Stopped $name (PID $pid) on port $Port."
    }
}
