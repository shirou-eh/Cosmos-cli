@echo off
REM VoidCorp Terminal - Windows Launcher
if not exist venv\Scripts\activate.bat (
    echo Installing dependencies...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)
python -m cosmos.main
pause
