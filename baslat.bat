@echo off
setlocal ENABLEEXTENSIONS

REM Ensure the script runs from the project root even if double-clicked
cd /d "%~dp0"

if not exist "venv\" (
    echo [ERROR] Sanal ortam bulunamadi. Lutfen once kurulum.bat dosyasini calistirin.
    pause
    exit /b 1
)

echo [INFO] Sanal ortam aktif ediliyor...
call "venv\Scripts\activate.bat"

echo [INFO] Uygulama baslatiliyor...
python -m uvicorn app.main:app --reload

