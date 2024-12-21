#!/bin/bash

echo "OS Platform: $OSTYPE"

# Check OS type and proceed accordingly
if [[ "$OSTYPE" == "linux-gnu"* || "$OSTYPE" == "darwin"* ]]; then
    # For Linux or macOS
    echo "cRUDEIRC - Activating virtual environment for Linux/macOS..."
    source .venv/bin/activate
    . .venv/bin/activate
    
    python3 crudeirc.py "$@"
elif [[ "$OSTYPE" == "msys"* || "$OSTYPE" == "cygwin"* || "$OSTYPE" == "win32"* ]]; then
    # For Windows
    echo "cRUDEIRC - Activating virtual environment for Windows..."
    source .venv/Scripts/activate.bat
    . .venv/Scripts/activate.bat
    python3 crudeirc.py "$@"
else
    echo "Unsupported OS: $OSTYPE"
    exit 1
fi
