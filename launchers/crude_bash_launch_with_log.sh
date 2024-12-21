#!/bin/bash

# Create a logs directory if it doesn't exist
LOG_DIR="logs"
mkdir -p "$LOG_DIR"

# Define log file with timestamp
LOG_FILE="$LOG_DIR/$(date +"%Y-%m-%d_%H-%M-%S")_app.log"

# Function to log messages
log_message() {
    echo "$(date +"%Y-%m-%d %H:%M:%S") - $1" >> "$LOG_FILE"
}

# Check for Python installation
if ! command -v python &> /dev/null
then
    log_message "Python is not installed. Exiting..."
    echo "Python is not installed. Exiting..."
    exit 1
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    # List possible activation scripts
    log_message "Virtual environment is not activated. Choosing activation script..."
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
            log_message "Activating virtual environment using $script..."
            source "$script"
            break
        else
            log_message "Invalid choice: $script"
            echo "Invalid choice."
        fi
    done
fi

# Run the Python application
log_message "Running application..."
echo "Running application..."
python main.py >> "$LOG_FILE" 2>&1

# Wait for user input before closing
log_message "Application finished. Waiting for user input before exiting..."
read -p "Press [Enter] key to exit..."
log_message "User pressed Enter. Exiting..."
