#!/bin/bash
timestamp=$(date "+%Y-%m-%d %H:%M:%S")
PROJECT_DIR="$(pwd)"
NEW_ENTRY="$1"
ENTRY_POINT="$2"
OUTPUT_NAME=$(basename "$NEW_ENTRY" .py) 
SPEC_PATH=$(basename "$NEW_ENTRY" .spec) 
FINAL_DIST_PATH="usr/local/bin/$OUTPUT_NAME"
DIST_PATH="$PROJECT_DIR/dist"

BINARY_PATH="$DIST_PATH/$OUTPUT_NAME"
HIDDEN_DIR="$FINAL_DEST_PATH/.$OUTPUT_NAMEsrc"
LIST_FILE="paths.txt" # Update this path if your file is named differently or located elsewhere.


echo ""
echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
echo "CrudePyBuild v0.0.1"
echo "Build started: $timestamp"
echo ""
echo "Build process for $OUTPUT_NAME has started."
echo "Entry Point: $ENTRY_POINT"
echo "Project Dir: $PROJECT_DIR"
echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
#Linux Mint users might have to enable and venv to install packages

# Check if .venv exists, if not, create it
if [ ! -d ".venv" ]; then
    echo ""
    echo ".venv not found. Creating virtual environment..."
    python3 -m venv .venv
fi

echo ""
echo "Activating virtual environment..."
source .venv/bin/activate
. .venv/bin/activate
echo ""
echo "Installing PyInstaller..."
pip install pyinstaller --quiet
echo ""
echo "Freezing Required Modules"
pip freeze requirements.txt --quiet
echo ""
echo "Checking Requirements"
pip install -r requirements.txt 
echo ""
if [ ! -d "$PROJECT_DIR/build" ]; then
    echo "Creating '$PROJECT_DIR/build'"
    mkdir "$PROJECT_DIR/build"
fi

if [ ! -d "$DIST_PATH" ]; then
    echo "Creating '$DIST_PATH'"
    mkdir "$DIST_PATH"
fi

echo ""
echo "Building binary with PyInstaller..."

# pyinstaller $SPEC_PATH --onefile "$PROJECT_DIR/$ENTRY_POINT"

OS_TYPE=$(uname -s)
if [[ "$OS_TYPE" == "Linux" ]]; then
  echo ""
  echo "Building for Linux..."
  pyinstaller --specpath "$PROJECT_DIR/$SPEC_PATH" --hidden-import win32security --hidden-import win32gui --distpath "$DIST_PATH" --onefile "$PROJECT_DIR/$ENTRY_POINT"
elif [[ "$OS_TYPE" == "MINGW"* || "$OS_TYPE" == "CYGWIN"* ]]; then
  echo ""
  echo "Building for Windows..."
  pyinstaller --specpath "$PROJECT_DIR/$SPEC_PATH" --distpath "$DIST_PATH" --onefile "$PROJECT_DIR/$ENTRY_POINT"
else
  echo ""
  echo "Unsupported OS: $OS_TYPE"
  exit 1
fi

echo ""
echo "Select an action for the binary:"
echo "1. Move to $FINAL_DIST_PATH"
echo "2. Copy to $FINAL_DIST_PATH"
echo "3. Skip Both"
read -rp "Enter your choice (1/2/3): " CHOICE

case $CHOICE in
  1)
    echo ""
    echo "Moving $BINARY_PATH to $FINAL_DIST_PATH"
    sudo mv "$BINARY_PATH" "$FINAL_DIST_PATH"

    # Process the list file
    if [ -f "$LIST_FILE" ]; then
        
        # Ensure the hidden directory exists
        if [ ! -d "$HIDDEN_DIR" ]; then
            echo "Creating source directory: $HIDDEN_DIR"
            sudo mkdir -p "$HIDDEN_DIR"
        fi
        
        echo "Processing file paths from $LIST_FILE"
        while IFS= read -r PATH_ITEM || [ -n "$PATH_ITEM" ]; do
        if [ -e "$PATH_ITEM" ]; then
            echo "Moving $PATH_ITEM to $HIDDEN_DIR"
            sudo mv "$PATH_ITEM" "$HIDDEN_DIR"
        else
            echo "Warning: $PATH_ITEM does not exist, skipping."
        fi
        done < "$LIST_FILE"
    else
        echo "Warning: List file $LIST_FILE not found. No additional files or directories will be processed."
    fi

    echo "Move complete."
    echo "Setting executable permissions for $FINAL_DIST_PATH"
    sudo chmod +x "$FINAL_DIST_PATH"
    echo ""
    echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    echo "Done! execute the application anywhere by typing: '$OUTPUT_NAME'."
    echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    ;;
  2)
    echo ""
    echo "Copying $BINARY_PATH to $FINAL_DIST_PATH"
    sudo cp "$BINARY_PATH" "$FINAL_DIST_PATH"
    
    # Process the list file
    if [ -f "$LIST_FILE" ]; then

        # Ensure the hidden directory exists
        if [ ! -d "$HIDDEN_DIR" ]; then
            echo "Creating source directory: $HIDDEN_DIR"
            sudo mkdir -p "$HIDDEN_DIR"
        fi

        echo "Processing file paths from $LIST_FILE"
        while IFS= read -r PATH_ITEM || [ -n "$PATH_ITEM" ]; do
        if [ -e "$PATH_ITEM" ]; then
            echo "Copying $PATH_ITEM to $HIDDEN_DIR"
            sudo cp "$PATH_ITEM" "$HIDDEN_DIR"
        else
            echo "Warning: $PATH_ITEM does not exist, skipping."
        fi
        done < "$LIST_FILE"
    else
        echo "Warning: List file $LIST_FILE not found. No additional files or directories will be processed."
    fi

    echo "Copy complete."
    echo "Setting executable permissions for $FINAL_DIST_PATH"
    sudo chmod +x "$FINAL_DIST_PATH"
    echo ""
    echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    echo "Done! execute the application anywhere by typing: '$OUTPUT_NAME'."
    echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    ;;
  3)
    echo ""
    echo "Move and Copy have been skipped. Binary can be located here: $BINARY_PATH"
    echo "Setting executable permissions for $BINARY_PATH"
    sudo chmod +x "$BINARY_PATH"
    echo ""
    echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    echo "Done! execute the application in its binary directory by typing: '$OUTPUT_NAME'."
    echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    ;;
  *)
    echo ""
    echo "Invalid choice. No action taken. Binary can be located here: $BINARY_PATH"
    echo "Setting executable permissions for $BINARY_PATH"
    sudo chmod +x "$BINARY_PATH"
    echo ""
    echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    echo "Done! execute the application in its binary directory by typing: '$OUTPUT_NAME'."
    echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

    ;;
esac


