@echo off
echo Installing watchdog...
pip install watchdog >nul 2>&1
if errorlevel 1 (
    echo Failed to install watchdog. Installing with --user...
    pip install watchdog --user
)
if errorlevel 1 (
    echo [!] Retrying with --user...
    pip install watchdog sounddevice soundfile numpy --user
)
echo Starting application...
start /B pythonw "%~dp0window.py"
start /B pythonw "%~dp0test.py"
exit
