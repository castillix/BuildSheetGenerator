@echo off
REM Build Sheet Generator - Windows Launch Script (Portable)
REM This script runs from a pre-configured virtual environment

echo ========================================
echo  FreeGeek Build Sheet Generator
echo ========================================
echo.

REM Check if venv exists
if not exist "venv_win\Scripts\python.exe" (
    echo ERROR: Virtual environment not found!
    echo Please ensure the entire venv folder is present.
    echo.
    pause
    exit /b 1
)

REM Run the application using venv's Python
echo Starting Build Sheet Generator...
echo.
echo ========================================
echo  Server will start at http://localhost:15001
echo  Press Ctrl+C to stop the server
echo ========================================
echo.

venv_win\Scripts\python.exe app.py

pause
