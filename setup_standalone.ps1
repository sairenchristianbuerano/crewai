# CrewAI Services - Standalone Setup Script (PowerShell)
# Creates virtual environments and installs dependencies for both services

$ErrorActionPreference = "Stop"

Write-Host "=============================================="
Write-Host "CrewAI Services - Standalone Setup"
Write-Host "=============================================="
Write-Host ""

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Check Python version
try {
    $PythonVersion = & python --version 2>&1 | Select-String -Pattern "\d+\.\d+\.\d+" | ForEach-Object { $_.Matches.Value }
    Write-Host "✓ Found Python $PythonVersion"

    $VersionParts = $PythonVersion.Split('.')
    $Major = [int]$VersionParts[0]
    $Minor = [int]$VersionParts[1]

    if ($Major -lt 3 -or ($Major -eq 3 -and $Minor -lt 11)) {
        Write-Host "⚠ WARNING: Python 3.11+ is recommended (you have $PythonVersion)" -ForegroundColor Yellow
        Write-Host ""
    }
} catch {
    Write-Host "❌ ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "   Please install Python 3.11 or higher from python.org"
    exit 1
}

# Check pip
try {
    $PipVersion = & pip --version 2>&1 | Select-String -Pattern "\d+\.\d+\.\d+" | ForEach-Object { $_.Matches.Value }
    Write-Host "✓ Found pip $PipVersion"
} catch {
    Write-Host "❌ ERROR: pip is not installed" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Setup Component Index
Write-Host "=============================================="
Write-Host "Setting up Component Index Service"
Write-Host "=============================================="
Write-Host ""

Set-Location component-index

if (Test-Path "venv") {
    Write-Host "⚠ venv already exists, removing..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force venv
}

Write-Host "Creating virtual environment..."
& python -m venv venv

Write-Host "Activating virtual environment..."
& .\venv\Scripts\Activate.ps1

Write-Host "Upgrading pip..."
try {
    & pip install --upgrade pip --quiet
} catch {
    Write-Host "⚠ Pip upgrade skipped" -ForegroundColor Yellow
}

Write-Host "Installing dependencies from requirements.txt..."
& pip install -r requirements.txt

# Pre-download sentence transformer model
Write-Host "Pre-downloading sentence transformer model (this may take a minute)..."
try {
    & python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"
} catch {
    Write-Host "⚠ Model download skipped" -ForegroundColor Yellow
}

deactivate
Write-Host "✓ Component Index setup complete" -ForegroundColor Green
Write-Host ""

Set-Location $ScriptDir

# Setup Component Generator
Write-Host "=============================================="
Write-Host "Setting up Component Generator Service"
Write-Host "=============================================="
Write-Host ""

Set-Location component-generator

if (Test-Path "venv") {
    Write-Host "⚠ venv already exists, removing..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force venv
}

Write-Host "Creating virtual environment..."
& python -m venv venv

Write-Host "Activating virtual environment..."
& .\venv\Scripts\Activate.ps1

Write-Host "Upgrading pip..."
try {
    & pip install --upgrade pip --quiet
} catch {
    Write-Host "⚠ Pip upgrade skipped" -ForegroundColor Yellow
}

Write-Host "Installing dependencies from requirements.txt..."
& pip install -r requirements.txt

deactivate
Write-Host "✓ Component Generator setup complete" -ForegroundColor Green
Write-Host ""

Set-Location $ScriptDir

# Create data directories
Write-Host "=============================================="
Write-Host "Creating data directories"
Write-Host "=============================================="
Write-Host ""

New-Item -ItemType Directory -Force -Path "component-index\data\components" | Out-Null
New-Item -ItemType Directory -Force -Path "component-index\data\chromadb" | Out-Null
New-Item -ItemType Directory -Force -Path "component-index\data\crewai_components" | Out-Null
New-Item -ItemType Directory -Force -Path "component-generator\data" | Out-Null
Write-Host "✓ Data directories created" -ForegroundColor Green
Write-Host ""

# Create .env.standalone if it doesn't exist
if (-Not (Test-Path ".env.standalone")) {
    if (Test-Path ".env.standalone.example") {
        Write-Host "Creating .env.standalone from example..."
        Copy-Item ".env.standalone.example" ".env.standalone"
        Write-Host "⚠ IMPORTANT: Edit .env.standalone and add your ANTHROPIC_API_KEY" -ForegroundColor Yellow
    } else {
        Write-Host "⚠ No .env.standalone.example found, skipping .env creation" -ForegroundColor Yellow
    }
} else {
    Write-Host "✓ .env.standalone already exists" -ForegroundColor Green
}

Write-Host ""
Write-Host "=============================================="
Write-Host "Setup Complete!"
Write-Host "=============================================="
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Edit .env.standalone and add your ANTHROPIC_API_KEY"
Write-Host "  2. Run: .\run_standalone.ps1"
Write-Host ""
Write-Host "Virtual environments created at:"
Write-Host "  - component-index\venv"
Write-Host "  - component-generator\venv"
Write-Host ""
