@echo off
setlocal ENABLEEXTENSIONS

REM Ensure the script runs from the project root even if double-clicked
cd /d "%~dp0"

echo [INFO] Sanal ortam kontrol ediliyor...
if not exist "venv\" (
    echo [INFO] Sanal ortam olusturuluyor...
    py -3 -m venv venv
)

echo [INFO] Sanal ortam aktif ediliyor...
call "venv\Scripts\activate.bat"

echo [INFO] pip guncelleniyor...
python -m pip install --upgrade pip

echo [INFO] Proje bagimliliklari yukleniyor...
pip install -r requirements.txt

echo.
echo [SUCCESS] Kurulum tamamlandi. Uygulamayi baslatmak icin baslat.bat dosyasini calistirin.
echo.
pause

