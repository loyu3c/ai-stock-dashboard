@echo off
cd /d "%~dp0"
call .venv\Scripts\activate.bat 2>nul
if errorlevel 1 (
    echo Virtual environment not found or activation failed. Trying global python...
)

echo Starting AI Stock Assistant...
python main.py
pause
