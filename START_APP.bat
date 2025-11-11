@echo off
echo ========================================
echo  DNA Forensic Analysis System
echo  Starting with ALL Features
echo ========================================
echo.
echo Stopping any running Flask apps...
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul
echo.
echo Starting the complete application...
echo.
python full_app.py
pause