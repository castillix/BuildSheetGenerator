#!/bin/bash

echo "========================================"
echo " Build Sheet Generator - Build Script (macOS)"
echo "========================================"
echo

# Function to activate venv
activate_venv() {
    if [ -f "venv/bin/activate" ]; then
        echo "Activating virtual environment (venv)..."
        source venv/bin/activate
        return 0
    elif [ -f "venv_mac/bin/activate" ]; then
        echo "Activating virtual environment (venv_mac)..."
        source venv_mac/bin/activate
        return 0
    elif [ -f ".venv/bin/activate" ]; then
        echo "Activating virtual environment (.venv)..."
        source .venv/bin/activate
        return 0
    else
        return 1
    fi
}

# Check for venv
if ! activate_venv; then
    echo "Virtual environment not found (checked venv, venv_mac, .venv)."
    echo "Please create it first or adjust this script."
    exit 1
fi

echo
echo "Installing PyInstaller..."
pip install pyinstaller

echo
echo "Building Executable..."
echo "This may take a minute..."
echo

# Clean previous builds
rm -rf build dist
rm -f *.spec

# Build command
# Note: Separator for --add-data on macOS is ':'
pyinstaller --name "BuildSheetGen" \
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
