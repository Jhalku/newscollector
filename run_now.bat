@echo off
setlocal

:: Get the directory where this batch file is located
set "PROJECT_DIR=%~dp0"
:: Remove trailing backslash
set "PROJECT_DIR=%PROJECT_DIR:~0,-1%"

set "PYTHON_EXE=%PROJECT_DIR%\venv\Scripts\python.exe"
set "SCRIPT_FILE=%PROJECT_DIR%\news_tracker.py"

echo Running News Tracker...
echo Fetching latest news for your keywords and delivering to Telegram...
echo.

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

:: Run the script
"%PYTHON_EXE%" "%SCRIPT_FILE%"

echo.
pause
endlocal
