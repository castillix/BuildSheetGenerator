@echo off
echo ========================================
echo  Build Sheet Generator - Build Script
echo ========================================
echo.

REM Check for venv
if exist "venv_win\Scripts\activate.bat" goto :FoundVenv

echo Virtual environment not found (venv_win).
echo Please create it first or adjust this script.
pause
exit /b 1

:FoundVenv
echo Activating virtual environment...
call venv_win\Scripts\activate.bat

echo.
echo Installing PyInstaller...
pip install pyinstaller

echo.
echo Building Executable...
echo This may take a minute...
echo.

REM Clean previous builds
rmdir /s /q build dist 2>nul
del /f /q *.spec 2>nul

REM Build command
pyinstaller --name "BuildSheetGen" ^
            --onefile ^
            --add-data "templates;templates" ^
            --add-data "static;static" ^
            --add-data "resources;resources" ^
            --icon=NONE ^
            app.py

echo.
if exist "dist\BuildSheetGen.exe" goto :BuildSuccess

echo Build failed. Please check output above.
goto :End

:BuildSuccess
echo ========================================
echo  Build Complete!
echo ========================================
echo  Executable is located in: dist\BuildSheetGen.exe
echo.
echo  Copying prices.txt to dist folder...
copy prices.txt dist\prices.txt >nul
echo.
echo  You can move this file anywhere. It contains everything needed.

:End
pause
