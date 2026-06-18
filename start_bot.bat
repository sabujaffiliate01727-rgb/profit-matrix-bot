@echo off
cd /d "%~dp0"
echo Installing dependencies (first run only)...
py -m pip install -r requirements.txt >nul 2>&1
echo Starting Profit Matrix bot...
py bot.py
pause
