# BPM Windows Build Script
# Run this script to create a standalone Windows executable

param(
    [switch]$Clean,
    [switch]$SkipVenv
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  BPM Windows Build Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get project root
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

# Clean previous builds
if ($Clean) {
    Write-Host "[1/5] Cleaning previous builds..." -ForegroundColor Yellow
    Remove-Item -Path "build" -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "dist" -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "*.spec.bak" -Force -ErrorAction SilentlyContinue
} else {
    Write-Host "[1/5] Skipping clean (use -Clean to remove previous builds)" -ForegroundColor Gray
}

# Setup virtual environment
if (-not $SkipVenv) {
    Write-Host "[2/5] Setting up virtual environment..." -ForegroundColor Yellow

    if (-not (Test-Path "venv")) {
        python -m venv venv
    }

    # Activate venv
    . .\venv\Scripts\Activate.ps1

    Write-Host "[3/5] Installing dependencies..." -ForegroundColor Yellow
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install pyinstaller
} else {
    Write-Host "[2/5] Skipping venv setup (use existing environment)" -ForegroundColor Gray
    Write-Host "[3/5] Skipping dependency install" -ForegroundColor Gray
}

# Build with PyInstaller
Write-Host "[4/5] Building executable with PyInstaller..." -ForegroundColor Yellow
pyinstaller BPM.spec --noconfirm

# Check result
if (Test-Path "dist\BPM.exe") {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  BUILD SUCCESSFUL!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Executable created at:" -ForegroundColor White
    Write-Host "  dist\BPM.exe" -ForegroundColor Cyan
    Write-Host ""

    # Get file size
    $size = (Get-Item "dist\BPM.exe").Length / 1MB
    Write-Host "File size: $([math]::Round($size, 2)) MB" -ForegroundColor Gray

    Write-Host ""
    Write-Host "[5/5] Creating distribution package..." -ForegroundColor Yellow

    # Create zip for distribution
    $version = "1.0.0"
    $zipName = "BPM-Windows-$version.zip"

    Compress-Archive -Path "dist\BPM.exe" -DestinationPath "dist\$zipName" -Force

    Write-Host "Distribution package created:" -ForegroundColor White
    Write-Host "  dist\$zipName" -ForegroundColor Cyan

} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "  BUILD FAILED!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Check the error messages above for details." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Done!" -ForegroundColor Green
