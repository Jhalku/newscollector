@echo off
setlocal

:: Get the directory where this batch file is located
set "PROJECT_DIR=%~dp0"
:: Remove trailing backslash
set "PROJECT_DIR=%PROJECT_DIR:~0,-1%"

set "PYTHON_EXE=%PROJECT_DIR%\venv\Scripts\python.exe"
set "SCRIPT_FILE=%PROJECT_DIR%\news_tracker.py"

echo Checking paths:
echo Project Directory: %PROJECT_DIR%
echo Python Path: %PYTHON_EXE%
echo Script Path: %SCRIPT_FILE%

if not exist "%PYTHON_EXE%" (
    echo Error: Could not find Python executable at %PYTHON_EXE%
    echo Make sure you have created the virtual environment in 'venv' folder.
    pause
    exit /b 1
)

if not exist "%SCRIPT_FILE%" (
    echo Error: Could not find script at %SCRIPT_FILE%
    pause
    exit /b 1
)

:: Create the scheduled task
echo Creating scheduled task 'NewsAutoCollector_Daily'...
schtasks /create /tn "NewsAutoCollector_Daily" /tr "\"%PYTHON_EXE%\" \"%SCRIPT_FILE%\"" /sc daily /st 09:00 /f

if %errorlevel% equ 0 (
    echo.
    echo Successfully scheduled task 'NewsAutoCollector_Daily' to run every day at 09:00 AM!
    echo To modify or check it, open the Windows "Task Scheduler" application.
) else (
    echo.
    echo Failed to create scheduled task. 
    echo Please try running this script as an Administrator!
)

pause
endlocal
