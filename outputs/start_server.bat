@echo off
title Game Server Launcher
echo Checking for Python...
where python >nul 2>nul
if %ERRORLEVEL% equ 0 (
    set PY_CMD=python
    goto :start_server
)
where python3 >nul 2>nul
if %ERRORLEVEL% equ 0 (
    set PY_CMD=python3
    goto :start_server
)

echo.
echo ERROR: Python was not found on your system!
echo Please download and install Python from https://www.python.org/downloads/
echo Make sure to check the option "Add Python to PATH" during installation.
echo.
pause
exit /b 1

:start_server
echo Starting server using %PY_CMD%...
%PY_CMD% server.py
pause
