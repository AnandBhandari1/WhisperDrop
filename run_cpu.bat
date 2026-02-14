@echo off

echo Starting WhisperDrop (CPU mode)...
echo Press F8 anywhere to start/stop recording
echo.

where uv >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: uv is not installed or not in PATH.
    echo Install it: https://astral.sh/uv
    exit /b 1
)

uv run python app_windows.py --cpu
