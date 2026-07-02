@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0"

echo Building GFA Admin Panel Windows executable...
echo.

if not exist "venv\Scripts\python.exe" (
    echo Creating virtual environment...
    py -3 -m venv venv
)

call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r req.txt pyinstaller

echo.
echo IMPORTANT: Set SKIP_LOGIN = False in main.py before distributing the exe.
echo.

pyinstaller main.spec --distpath dist/android --noconfirm

if exist "dist\android\GFA-Admin-Panel.exe" (
    echo.
    echo Success: dist\android\GFA-Admin-Panel.exe
    echo The database file will be created beside the exe on first run.
) else (
    echo.
    echo Build failed. Check the output above for errors.
    exit /b 1
)

endlocal
