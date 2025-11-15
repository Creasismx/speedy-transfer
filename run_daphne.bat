@echo off
echo Starting Daphne server with HTTP and WebSocket support...
echo.
cd /d %~dp0

REM Activate virtual environment if it exists
if exist "venv311\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv311\Scripts\activate.bat
)

REM Run Daphne using Python module
echo Starting server on port 8001...
python -m daphne -b 0.0.0.0 -p 8001 config.asgi:application

pause

