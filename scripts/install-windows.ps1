# BPM - Windows Installation Script
# Run in PowerShell as Administrator

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  BPM - Blood Pressure Analysis Tool" -ForegroundColor Cyan
Write-Host "  Windows Installation Script" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
function Check-Python {
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "Found: $pythonVersion" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "Python not found." -ForegroundColor Yellow
        return $false
    }
}

# Install Python via winget or prompt user
function Install-Python {
    Write-Host "Installing Python..." -ForegroundColor Yellow

    if (Get-Command winget -ErrorAction SilentlyContinue) {
        winget install Python.Python.3.11
    }
    else {
        Write-Host "Please download Python from https://www.python.org/downloads/" -ForegroundColor Red
        Write-Host "Make sure to check 'Add Python to PATH' during installation." -ForegroundColor Red
        Start-Process "https://www.python.org/downloads/"
        Read-Host "Press Enter after installing Python..."
    }
}

# Setup Python environment
function Setup-PythonEnv {
    Write-Host ""
    Write-Host "Setting up Python environment..." -ForegroundColor Yellow

    $scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
    $projectRoot = Split-Path -Parent $scriptPath

    Set-Location $projectRoot

    # Create virtual environment
    if (-not (Test-Path "venv")) {
        Write-Host "Creating virtual environment..."
        python -m venv venv
    }

    # Activate virtual environment
    & ".\venv\Scripts\Activate.ps1"

    # Upgrade pip
    python -m pip install --upgrade pip

    # Install dependencies
    Write-Host "Installing Python packages..."
    pip install -r requirements.txt

    Write-Host "Python environment ready!" -ForegroundColor Green
}

# Create desktop shortcut
function Create-Shortcut {
    Write-Host ""
    Write-Host "Creating desktop shortcut..." -ForegroundColor Yellow

    $scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
    $projectRoot = Split-Path -Parent $scriptPath

    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\BPM.lnk")
    $Shortcut.TargetPath = "powershell.exe"
    $Shortcut.Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$projectRoot\scripts\run-bpm.ps1`""
    $Shortcut.WorkingDirectory = $projectRoot
    $Shortcut.Description = "Blood Pressure Analysis Tool"
    $Shortcut.Save()

    Write-Host "Desktop shortcut created!" -ForegroundColor Green
}

# Create run script
function Create-RunScript {
    Write-Host ""
    Write-Host "Creating run script..." -ForegroundColor Yellow

    $scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
    $projectRoot = Split-Path -Parent $scriptPath

    $runScript = @"
# BPM Run Script
Set-Location "$projectRoot"
& ".\venv\Scripts\Activate.ps1"
python src/main.py
"@

    Set-Content -Path "$projectRoot\scripts\run-bpm.ps1" -Value $runScript

    # Also create a batch file for easy launching
    $batchScript = @"
@echo off
cd /d "$projectRoot"
call venv\Scripts\activate.bat
python src\main.py
"@

    Set-Content -Path "$projectRoot\run-bpm.bat" -Value $batchScript

    Write-Host "Run scripts created!" -ForegroundColor Green
}

# Main installation
function Main {
    Write-Host "Starting installation..." -ForegroundColor Cyan

    if (-not (Check-Python)) {
        Install-Python
    }

    Setup-PythonEnv
    Create-RunScript

    Write-Host ""
    $createShortcut = Read-Host "Create desktop shortcut? [Y/n]"
    if ($createShortcut -eq "" -or $createShortcut -eq "Y" -or $createShortcut -eq "y") {
        Create-Shortcut
    }

    Write-Host ""
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host "Installation Complete!" -ForegroundColor Green
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To run BPM:"
    Write-Host "  Double-click run-bpm.bat"
    Write-Host ""
    Write-Host "Or use the desktop shortcut (if created)"
    Write-Host ""
}

Main
