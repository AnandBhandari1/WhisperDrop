@echo off

REM WhisperDrop - Speak. Drop. Done.

echo Starting WhisperDrop...
echo Press F8 anywhere to start/stop recording
echo.

REM Check if uv is installed
where uv >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: uv is not installed.
    echo Install it: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    pause
    exit /b 1
)

uv run python app.py
pause
