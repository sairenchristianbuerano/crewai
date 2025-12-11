# CrewAI Services - Standalone Stop Script (PowerShell)
# Stops both component-index and component-generator services

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# PID files
$IndexPidFile = Join-Path $ScriptDir ".component-index.pid"
$GeneratorPidFile = Join-Path $ScriptDir ".component-generator.pid"

Write-Host "=============================================="
Write-Host "Stopping CrewAI Services"
Write-Host "=============================================="
Write-Host ""

# Stop Component Generator
if (Test-Path $GeneratorPidFile) {
    $GeneratorPid = Get-Content $GeneratorPidFile

    $Process = Get-Process -Id $GeneratorPid -ErrorAction SilentlyContinue
    if ($Process) {
        Write-Host "Stopping Component Generator (PID: $GeneratorPid)..."
        Stop-Process -Id $GeneratorPid -Force -ErrorAction SilentlyContinue

        # Wait for process to stop
        for ($i = 1; $i -le 10; $i++) {
            $Process = Get-Process -Id $GeneratorPid -ErrorAction SilentlyContinue
            if (-not $Process) {
                break
            }
            Start-Sleep -Seconds 1
        }

        Write-Host "✓ Component Generator stopped" -ForegroundColor Green
    } else {
        Write-Host "⚠ Component Generator not running (stale PID file)" -ForegroundColor Yellow
    }

    Remove-Item $GeneratorPidFile -Force -ErrorAction SilentlyContinue
} else {
    Write-Host "⚠ Component Generator PID file not found" -ForegroundColor Yellow
}

# Stop Component Index
if (Test-Path $IndexPidFile) {
    $IndexPid = Get-Content $IndexPidFile

    $Process = Get-Process -Id $IndexPid -ErrorAction SilentlyContinue
    if ($Process) {
        Write-Host "Stopping Component Index (PID: $IndexPid)..."
        Stop-Process -Id $IndexPid -Force -ErrorAction SilentlyContinue

        # Wait for process to stop
        for ($i = 1; $i -le 10; $i++) {
            $Process = Get-Process -Id $IndexPid -ErrorAction SilentlyContinue
            if (-not $Process) {
                break
            }
            Start-Sleep -Seconds 1
        }

        Write-Host "✓ Component Index stopped" -ForegroundColor Green
    } else {
        Write-Host "⚠ Component Index not running (stale PID file)" -ForegroundColor Yellow
    }

    Remove-Item $IndexPidFile -Force -ErrorAction SilentlyContinue
} else {
    Write-Host "⚠ Component Index PID file not found" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✓ All services stopped" -ForegroundColor Green
Write-Host ""
