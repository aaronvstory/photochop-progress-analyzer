@echo off
title Photochop Progress Analyzer - Windows Installation

echo ==================================================
echo Photochop Progress Analyzer - Installation Script
echo ==================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if NOT %errorLevel% == 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python 3.7+ from https://python.org/downloads
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo [OK] Python found
python --version

REM Check if pip is available
pip --version >nul 2>&1
if NOT %errorLevel% == 0 (
    echo [ERROR] pip is not available
    echo.
    echo Please ensure pip is installed with Python
    pause
    exit /b 1
)

echo [OK] pip found

REM Install dependencies
echo.
echo [INFO] Installing dependencies...
pip install psutil

if NOT %errorLevel% == 0 (
    echo [ERROR] Failed to install dependencies
    echo.
    echo Try running this command manually:
    echo pip install psutil
    echo.
    pause
    exit /b 1
)

echo [OK] Dependencies installed successfully

REM Test installation
echo.
echo [INFO] Testing installation...
cd ..\src\
python photoshop_monitor.py --help >nul 2>&1

if NOT %errorLevel% == 0 (
    echo [ERROR] Installation test failed
    echo.
    echo Please check the setup manually
    pause
    exit /b 1
)

echo [OK] Installation test passed

echo.
echo ==================================================
echo [SUCCESS] Installation completed successfully!
echo ==================================================
echo.
echo Quick start:
echo   1. Navigate to the src\ folder
echo   2. Right-click "run_photoshop_monitor.bat"
echo   3. Select "Run as Administrator"
echo   4. Choose option 4 to select your monitoring folder
echo.
echo For detailed usage instructions, see:
echo   docs\SETUP.md
echo   README.md
echo.
pause
