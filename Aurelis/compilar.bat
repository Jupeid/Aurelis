@echo off
echo ===================================
echo   Gerando executavel com PyInstaller...
echo ===================================

pyinstaller --noconfirm --onefile --windowed --icon=aurelis.ico --add-data "*.txt;." Aurelis.py

echo.
echo ===================================
echo   Processo concluido com sucesso!
echo ===================================
pause