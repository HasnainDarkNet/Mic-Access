@echo off
title Application Setup
cd /d "%~dp0"

echo ======================================
echo Checking Python...
echo ======================================

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not added to PATH.
    pause
    exit /b
)

echo.
echo ======================================
echo Updating pip...
echo ======================================
python -m pip install --upgrade pip

echo.
echo ======================================
echo Installing Required Packages...
echo ======================================

python -m pip install --upgrade watchdog sounddevice soundfile numpy

if errorlevel 1 (
    echo.
    echo Normal installation failed.
    echo Trying user installation...
    python -m pip install --upgrade watchdog sounddevice soundfile numpy --user
)

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to install required packages.
    pause
    exit /b
)

echo.
echo ======================================
echo Starting Application...
echo ======================================

start "" pythonw "%~dp0window.py"
start "" pythonw "%~dp0test.py"

exit
