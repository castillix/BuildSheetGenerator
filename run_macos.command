#!/bin/bash
# Build Sheet Generator - macOS Launch Script (Portable)
# This script runs from a pre-configured virtual environment

echo "========================================"
echo " FreeGeek Build Sheet Generator"
echo "========================================"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if venv exists
if [ ! -f "venv_macos/bin/python" ]; then
    echo "ERROR: Virtual environment not found!"
    echo "Please ensure the entire venv folder is present."
    echo ""
    exit 1
fi

# Run the application using venv's Python
echo "Starting Build Sheet Generator..."
echo ""
echo "========================================"
echo " Server will start at http://localhost:15000"
echo " Press Ctrl+C to stop the server"
echo "========================================"
echo ""

./venv_macos/bin/python app.py
