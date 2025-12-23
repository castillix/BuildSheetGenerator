#!/bin/bash

echo "========================================"
echo " Build Sheet Generator - Build Script (Linux)"
echo "========================================"
echo

# Determine VENV location
VENV_PATH=""
if [ -d "venv" ]; then
    VENV_PATH="./venv"
elif [ -d "venv_linux" ]; then
    VENV_PATH="./venv_linux"
elif [ -d ".venv" ]; then
    VENV_PATH="./.venv"
fi

if [ -z "$VENV_PATH" ]; then
    echo "Error: Virtual environment not found (checked venv, venv_linux, .venv)."
    echo "Please create it first using 'python3 -m venv venv' and try again."
    exit 1
fi

echo "Using virtual environment at: $VENV_PATH"

# Define executable paths
PYTHON="$VENV_PATH/bin/python"
PIP="$VENV_PATH/bin/pip"
PYINSTALLER="$VENV_PATH/bin/pyinstaller"

# Verify Python exists (sanity check for venv)
if [ ! -f "$PYTHON" ]; then
    echo "Error: Python interpreter not found at $PYTHON"
    exit 1
fi

echo "Installing PyInstaller..."
"$PIP" install pyinstaller

# Verify PyInstaller exists after install
if [ ! -f "$PYINSTALLER" ]; then
    echo "Error: PyInstaller not found at $PYINSTALLER after installation."
    echo "Installation might have failed or installed to a different location."
    exit 1
fi

echo
echo "Building Executable..."
echo "This may take a minute..."
echo

# Clean previous builds
rm -rf build dist
rm -f *.spec

# Build command using specific pyinstaller path
# Note: Separator for --add-data on Linux is ':'
"$PYINSTALLER" --name "BuildSheetGen" \
            --onefile \
            --add-data "templates:templates" \
            --add-data "static:static" \
            --add-data "resources:resources" \
            --icon=NONE \
            app.py

echo
if [ -f "dist/BuildSheetGen" ]; then
    echo "========================================"
    echo " Build Complete!"
    echo "========================================"
    echo " Executable is located in: dist/BuildSheetGen"
    echo
    echo " Copying prices.txt to dist folder..."
    cp prices.txt dist/prices.txt
    echo
    echo " You can move this file anywhere. It contains everything needed."
else
    echo "Build failed. Please check output above."
    exit 1
fi
