@echo off
chcp 65001 >nul
echo Installing requirements...
pip install -r requirements.txt pyinstaller
echo Building...
pyinstaller --noconfirm --windowed --name AdhanApp --collect-all customtkinter --collect-data tzdata adhan_app.py
echo.
echo Done. Output folder: dist\AdhanApp
pause
