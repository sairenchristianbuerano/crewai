# CrewAI Services - Standalone Run Script (PowerShell)
# Starts both component-index and component-generator services

$ErrorActionPreference = "Stop"

Write-Host "=============================================="
Write-Host "CrewAI Services - Standalone Mode"
Write-Host "=============================================="
Write-Host ""

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# PID files
$IndexPidFile = Join-Path $ScriptDir ".component-index.pid"
$GeneratorPidFile = Join-Path $ScriptDir ".component-generator.pid"

# Log files
$IndexLog = Join-Path $ScriptDir "component-index.log"
$GeneratorLog = Join-Path $ScriptDir "component-generator.log"

# Check if services are already running
if (Test-Path $IndexPidFile) {
    $IndexPid = Get-Content $IndexPidFile
    if (Get-Process -Id $IndexPid -ErrorAction SilentlyContinue) {
        Write-Host "⚠ Component Index is already running (PID: $IndexPid)" -ForegroundColor Yellow
        Write-Host "  Run .\stop_standalone.ps1 first to stop existing services"
        exit 1
    }
}

if (Test-Path $GeneratorPidFile) {
    $GeneratorPid = Get-Content $GeneratorPidFile
    if (Get-Process -Id $GeneratorPid -ErrorAction SilentlyContinue) {
        Write-Host "⚠ Component Generator is already running (PID: $GeneratorPid)" -ForegroundColor Yellow
        Write-Host "  Run .\stop_standalone.ps1 first to stop existing services"
        exit 1
    }
}

# Load environment variables
if (Test-Path ".env.standalone") {
    Write-Host "✓ Loading environment from .env.standalone"
    Get-Content ".env.standalone" | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]+)=(.*)$') {
            [Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim(), "Process")
        }
    }
} elseif (Test-Path ".env") {
    Write-Host "✓ Loading environment from .env"
    Get-Content ".env" | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]+)=(.*)$') {
            [Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim(), "Process")
        }
    }
} else {
    Write-Host "⚠ No .env.standalone or .env file found" -ForegroundColor Yellow
}

# Set default environment variables
$env:COMPONENT_RAG_URL = if ($env:COMPONENT_RAG_URL) { $env:COMPONENT_RAG_URL } else { "http://localhost:8086" }
$env:PORT_INDEX = if ($env:PORT_INDEX) { $env:PORT_INDEX } else { "8086" }
$env:PORT_GENERATOR = if ($env:PORT_GENERATOR) { $env:PORT_GENERATOR } else { "8085" }

# Check required dependencies
if (-not $env:ANTHROPIC_API_KEY) {
    Write-Host ""
    Write-Host "❌ ERROR: ANTHROPIC_API_KEY is required" -ForegroundColor Red
    Write-Host ""
    Write-Host "Set it in .env.standalone:"
    Write-Host "  ANTHROPIC_API_KEY=your_key_here"
    Write-Host ""
    exit 1
}

# Check if venvs exist
if (-not (Test-Path "component-index\venv")) {
    Write-Host "❌ ERROR: component-index\venv not found" -ForegroundColor Red
    Write-Host "   Run .\setup_standalone.ps1 first"
    exit 1
}

if (-not (Test-Path "component-generator\venv")) {
    Write-Host "❌ ERROR: component-generator\venv not found" -ForegroundColor Red
    Write-Host "   Run .\setup_standalone.ps1 first"
    exit 1
}

Write-Host ""
Write-Host "Configuration:"
Write-Host "  Component Index Port: $env:PORT_INDEX"
Write-Host "  Component Generator Port: $env:PORT_GENERATOR"
Write-Host "  RAG URL: $env:COMPONENT_RAG_URL"
Write-Host ""

# Cleanup function
function Stop-Services {
    Write-Host ""
    Write-Host "Shutting down services..."
    & "$ScriptDir\stop_standalone.ps1"
}

# Register cleanup on exit
$null = Register-EngineEvent PowerShell.Exiting -Action { Stop-Services }

# Start Component Index
Write-Host "=============================================="
Write-Host "Starting Component Index Service"
Write-Host "=============================================="
Write-Host ""

Set-Location "component-index"

$env:PORT = $env:PORT_INDEX
$env:STORAGE_PATH = ".\data\components"
$env:TOOLS_DIR = ".\data\crewai_components"
$env:CHROMADB_DIR = ".\data\chromadb"

Write-Host "Starting on port $env:PORT_INDEX..."

$IndexProcess = Start-Process -FilePath ".\venv\Scripts\python.exe" `
    -ArgumentList "src\service.py" `
    -RedirectStandardOutput $IndexLog `
    -RedirectStandardError $IndexLog `
    -PassThru `
    -WindowStyle Hidden

$IndexProcess.Id | Out-File -FilePath $IndexPidFile -Encoding ASCII

Set-Location $ScriptDir

Write-Host "✓ Component Index started (PID: $($IndexProcess.Id))" -ForegroundColor Green
Write-Host "  Logs: $IndexLog"
Write-Host ""

# Wait for component-index to be healthy
Write-Host "Waiting for Component Index to become healthy..."
$HealthCheckUrl = "http://localhost:$env:PORT_INDEX/api/crewai/component-index/health"

for ($i = 1; $i -le 30; $i++) {
    try {
        $response = Invoke-WebRequest -Uri $HealthCheckUrl -UseBasicParsing -TimeoutSec 1 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "✓ Component Index is healthy" -ForegroundColor Green
            break
        }
    } catch {
        # Continue waiting
    }

    if ($i -eq 30) {
        Write-Host "❌ Component Index failed to start within 30 seconds" -ForegroundColor Red
        Write-Host "   Check logs: Get-Content $IndexLog -Tail 50"
        Stop-Services
        exit 1
    }

    Start-Sleep -Seconds 1
    Write-Host -NoNewline "."
}

Write-Host ""
Write-Host ""

# Start Component Generator
Write-Host "=============================================="
Write-Host "Starting Component Generator Service"
Write-Host "=============================================="
Write-Host ""

Set-Location "component-generator"

$env:PORT = $env:PORT_GENERATOR
$env:RAG_SERVICE_URL = $env:COMPONENT_RAG_URL

Write-Host "Starting on port $env:PORT_GENERATOR..."

$GeneratorProcess = Start-Process -FilePath ".\venv\Scripts\python.exe" `
    -ArgumentList "src\service.py" `
    -RedirectStandardOutput $GeneratorLog `
    -RedirectStandardError $GeneratorLog `
    -PassThru `
    -WindowStyle Hidden

$GeneratorProcess.Id | Out-File -FilePath $GeneratorPidFile -Encoding ASCII

Set-Location $ScriptDir

Write-Host "✓ Component Generator started (PID: $($GeneratorProcess.Id))" -ForegroundColor Green
Write-Host "  Logs: $GeneratorLog"
Write-Host ""

# Wait for component-generator to be healthy
Write-Host "Waiting for Component Generator to become healthy..."
$HealthCheckUrl = "http://localhost:$env:PORT_GENERATOR/api/crewai/component-generator/health"

for ($i = 1; $i -le 30; $i++) {
    try {
        $response = Invoke-WebRequest -Uri $HealthCheckUrl -UseBasicParsing -TimeoutSec 1 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "✓ Component Generator is healthy" -ForegroundColor Green
            break
        }
    } catch {
        # Continue waiting
    }

    if ($i -eq 30) {
        Write-Host "❌ Component Generator failed to start within 30 seconds" -ForegroundColor Red
        Write-Host "   Check logs: Get-Content $GeneratorLog -Tail 50"
        Stop-Services
        exit 1
    }

    Start-Sleep -Seconds 1
    Write-Host -NoNewline "."
}

Write-Host ""
Write-Host ""
Write-Host "=============================================="
Write-Host "All Services Running!"
Write-Host "=============================================="
Write-Host ""
Write-Host "Component Index:      http://localhost:$env:PORT_INDEX"
Write-Host "Component Generator:  http://localhost:$env:PORT_GENERATOR"
Write-Host ""
Write-Host "API Documentation:"
Write-Host "  Component Index:     http://localhost:$env:PORT_INDEX/docs"
Write-Host "  Component Generator: http://localhost:$env:PORT_GENERATOR/docs"
Write-Host ""
Write-Host "Logs:"
Write-Host "  Component Index:     Get-Content $IndexLog -Wait"
Write-Host "  Component Generator: Get-Content $GeneratorLog -Wait"
Write-Host ""
Write-Host "To stop services: .\stop_standalone.ps1"
Write-Host ""
Write-Host "Press Ctrl+C to stop all services and exit..."
Write-Host ""

# Keep script running and tail logs
try {
    while ($true) {
        Start-Sleep -Seconds 1

        # Check if processes are still running
        if (-not (Get-Process -Id $IndexProcess.Id -ErrorAction SilentlyContinue)) {
            Write-Host "⚠ Component Index process has stopped unexpectedly" -ForegroundColor Yellow
            break
        }
        if (-not (Get-Process -Id $GeneratorProcess.Id -ErrorAction SilentlyContinue)) {
            Write-Host "⚠ Component Generator process has stopped unexpectedly" -ForegroundColor Yellow
            break
        }
    }
} finally {
    Stop-Services
}
