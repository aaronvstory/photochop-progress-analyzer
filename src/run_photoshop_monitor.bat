@echo off
title Photochop Progress Analyzer

REM Enable color support for console output
color

REM Check admin privileges
net session >nul 2>&1
if NOT %errorLevel% == 0 (
    echo.
    echo ================================================================================
    echo                                   ERROR                                   
    echo ================================================================================
    echo.
    echo [ERROR] This script requires Administrator privileges.
    echo.
    echo Please right-click this file and select "Run as Administrator"
    echo.
    echo ================================================================================
    pause
    exit /b 1
)

echo.
echo ================================================================================
    echo                     PHOTOCHOP PROGRESS ANALYZER                     
echo               Real-time Photoshop Generative Expand Tracking                
echo ================================================================================
echo.
echo [INFO] Starting monitoring system...

REM Navigate to script directory
cd /d "%~dp0"

REM Get current monitored path from config
python -c "import json, os; config=json.load(open('monitor_config.json')) if os.path.exists('monitor_config.json') else {'base_path': r'C:\Users\%USERNAME%\Downloads'}; print(config['base_path'])" > temp_path.txt 2>nul
if exist temp_path.txt (
    set /p CURRENT_PATH=<temp_path.txt
    del temp_path.txt
) else (
    set CURRENT_PATH=C:\Users\%USERNAME%\Downloads
)

REM Check if Python is available
python --version >nul 2>&1
if NOT %errorLevel% == 0 (
    echo.
    echo ================================================================================
    echo                                   ERROR                                   
    echo ================================================================================
    echo.
    echo [ERROR] Python not found in PATH
    echo.
    echo Please install Python or add it to your PATH environment variable
    echo Download Python from: https://python.org/downloads
    echo.
    echo ================================================================================
    pause
    exit /b 1
)

REM Check if script exists
if NOT exist "photoshop_monitor.py" (
    echo.
    echo ================================================================================
    echo                                   ERROR                                   
    echo ================================================================================
    echo.
    echo [ERROR] Monitor script not found
    echo.
    echo Expected: photoshop_monitor.py
    echo Please ensure all files are in the same directory as this batch file
    echo.
    echo ================================================================================
    pause
    exit /b 1
)

echo ================================================================================
echo                              SYSTEM READY                              
echo ================================================================================
echo.
echo [OK] All checks passed - System ready for monitoring operations

:MAIN_MENU
REM Re-read current monitored path (in case it was changed via option 4)
python -c "import json, os; config=json.load(open('monitor_config.json')) if os.path.exists('monitor_config.json') else {'base_path': r'C:\Users\%USERNAME%\Downloads'}; print(config['base_path'])" > temp_path.txt 2>nul
if exist temp_path.txt (
    set /p CURRENT_PATH=<temp_path.txt
    del temp_path.txt
) else (
    set CURRENT_PATH=C:\Users\%USERNAME%\Downloads
)

echo.
echo ================================================================================
echo                        CURRENT MONITORING CONFIGURATION                        
echo ================================================================================
echo.
echo [*] Monitored Path:
echo    %CURRENT_PATH%
echo.
echo [+] Status: Ready for monitoring operations
echo [i] Last Updated: Auto-detected from configuration
echo.
echo ================================================================================
echo                             MONITORING MENU                              
echo ================================================================================
echo.
echo [*] Choose your monitoring mode:
echo.
echo    [1] [CHECK]    Single Check     - Check progress once and return to menu
echo    [2] [MONITOR]  Continuous Monitor - Real-time monitoring (updates every 30s)
echo    [3] [EXIT]     Exit              - Close monitoring system
echo    [4] [FOLDER]   Change Folder     - Select new folder to monitor
echo.
echo ================================================================================
echo.
set /p choice="Enter choice (1-4): "

if "%choice%"=="1" (
    echo.
    echo [INFO] Running single progress check...
    echo ================================================================================
    python photoshop_monitor.py
    echo ================================================================================
    echo [OK] Check completed - Returning to main menu...
    pause
    goto MAIN_MENU
) else if "%choice%"=="2" (
    echo.
    echo [INFO] Starting continuous monitoring mode...
    echo [INFO] Press Ctrl+C to stop monitoring
    echo ================================================================================
    python photoshop_monitor.py --monitor
    echo ================================================================================
    echo [OK] Monitoring stopped - Returning to main menu...
    pause
    goto MAIN_MENU
) else if "%choice%"=="3" (
    echo.
    echo [INFO] Exiting Photochop Progress Analyzer...
    echo Thank you for using our monitoring system!
    echo ================================================================================
    pause
    exit /b 0
) else if "%choice%"=="4" (
    echo.
    echo [INFO] Opening folder picker to select new monitored path...
    echo ================================================================================
    python photoshop_monitor.py --select-folder
    echo ================================================================================
    echo [OK] Folder selection completed - Returning to main menu...
    pause
    goto MAIN_MENU
) else (
    echo.
    echo [ERROR] Invalid choice. Please select 1, 2, 3, or 4
    pause
    goto MAIN_MENU
)

REM This section should never be reached due to the loop structure above
echo.
echo [INFO] Script completed unexpectedly
pause
