#!/bin/bash

echo "======================================"
echo "CardioPredict Application Launcher"
echo "======================================"
echo
echo "Starting application..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in your PATH."
    echo "Please install Python 3.7 or higher and try again."
    read -p "Press Enter to exit..."
    exit 1
fi

# Make sure the script is executable
chmod +x run_app.py

# Launch the application using the launcher script
python3 run_app.py

# If the application exits, wait before closing
echo
echo "Application has closed. Press Enter to exit..."
read