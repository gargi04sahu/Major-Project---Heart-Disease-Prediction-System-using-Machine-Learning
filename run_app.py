#!/usr/bin/env python
"""
CardioPredict Launcher Script
This script helps to launch the CardioPredict application properly.
It will check for available ports and launch the application accordingly.
"""

import os
import sys
import socket
import webbrowser
import subprocess
import time
import platform
from pathlib import Path

# Default port to try first
DEFAULT_PORT = 5000
# Alternate ports to try if default is unavailable
ALTERNATE_PORTS = [8501, 8502, 8503, 8504, 8505]

def is_port_in_use(port):
    """Check if a port is already in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def find_available_port():
    """Find an available port to use"""
    if not is_port_in_use(DEFAULT_PORT):
        return DEFAULT_PORT
    
    for port in ALTERNATE_PORTS:
        if not is_port_in_use(port):
            return port
    
    return None

def create_streamlit_config():
    """Create the .streamlit configuration folder and config.toml if they don't exist"""
    # Create the .streamlit directory if it doesn't exist
    config_dir = Path('.streamlit')
    config_dir.mkdir(exist_ok=True)
    
    # Create config.toml if it doesn't exist
    config_file = config_dir / 'config.toml'
    if not config_file.exists():
        with open(config_file, 'w') as f:
            f.write("""[server]
headless = false
address = "0.0.0.0"
runOnSave = true

[browser]
gatherUsageStats = false
serverAddress = "localhost"
serverPort = 5000
""")

def check_environment():
    """Check if the environment is properly set up"""
    try:
        import streamlit
        import pandas
        import numpy
        import sklearn
        import plotly
        import matplotlib
        print("✅ All required packages are installed.")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install all required dependencies with:")
        print("pip install streamlit pandas numpy scikit-learn plotly matplotlib streamlit-extras")
        return False

def launch_app(port):
    """Launch the Streamlit application on the specified port"""
    print(f"🚀 Starting CardioPredict on port {port}...")
    
    # Open the browser after a slight delay to allow the server to start
    def open_browser():
        time.sleep(2)  # Wait for the server to start
        url = f"http://localhost:{port}"
        print(f"📱 Opening {url} in your browser...")
        webbrowser.open(url)
    
    # Start the browser in a separate thread
    import threading
    threading.Thread(target=open_browser).start()
    
    # Start the Streamlit app
    cmd = [sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", str(port)]
    subprocess.run(cmd)

def main():
    """Main function to run the app"""
    print("=" * 50)
    print("CardioPredict Launcher")
    print("=" * 50)
    
    # Check if environment is set up correctly
    if not check_environment():
        print("Please fix the dependencies and try again.")
        return
    
    # Create Streamlit config if needed
    create_streamlit_config()
    
    # Find an available port
    port = find_available_port()
    if port is None:
        print("❌ Could not find an available port. Please free up one of these ports:")
        print(f"   {DEFAULT_PORT}, {', '.join(map(str, ALTERNATE_PORTS))}")
        return
    
    # Launch the app
    launch_app(port)

if __name__ == "__main__":
    main()