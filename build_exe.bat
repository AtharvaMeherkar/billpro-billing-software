@echo off
echo ============================================
echo   BillPro - Building Windows Executable
echo ============================================
echo.

REM Check if Python is available
python --version > nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.10+
    pause
    exit /b 1
)

REM Install PyInstaller if not present
echo [1/4] Checking PyInstaller...
pip show pyinstaller > nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

REM Install dependencies
echo [2/4] Installing dependencies...
pip install -r requirements.txt

REM Clean previous builds
echo [3/4] Cleaning previous builds...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build

REM Build the executable
echo [4/4] Building executable...
echo This may take a few minutes...
echo.
pyinstaller billpro.spec --clean

echo.
echo ============================================
if exist "dist\BillPro.exe" (
    echo SUCCESS! Executable created at:
    echo    dist\BillPro.exe
    echo.
    echo You can now share this file!
    echo Double-click BillPro.exe to run.
) else (
    echo BUILD FAILED! Check errors above.
)
echo ============================================
pause
