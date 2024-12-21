#!/bin/bash

# Check for Python installation
if ! command -v python &> /dev/null
then
    echo "Python is not installed. Exiting..."
    exit 1
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    # List possible activation scripts
    echo "Virtual environment is not activated. Choose an activation script:"
    scripts=(
        ".venv/bin/activate"
        ".venv/bin/activate_this.py"
        ".venv/bin/deactivate"
        ".venv/bin/activate.fish"
        ".venv/bin/activate.nu"
        ".venv/bin/activate.ps1"
    )
    select script in "${scripts[@]}"; do
        if [[ -f "$script" ]]; then
            source "$script"
            break
        else
            echo "Invalid choice."
        fi
    done
fi

# Run the Python application
echo "Running application..."
python main.py

# Wait for user input before closing
# shellcheck disable=SC2162
read -p "Press [Enter] key to exit..."
