import os
import subprocess
import sys
import webbrowser
import time

print("🚀 Launching Study Helper AI... Please wait.\n")

# Define app path
project_path = os.path.dirname(os.path.abspath(__file__))
app_path = os.path.join(project_path, "app.py")

# Open browser manually after Streamlit starts
def open_browser():
    time.sleep(3)  # wait a few seconds for Streamlit server
    webbrowser.open("http://localhost:8501")

# Launch Streamlit server
subprocess.Popen([sys.executable, "-m", "streamlit", "run", app_path])

# Open browser tab
open_browser()

# Keep window open
input("\n✅ App launched! Press Enter to close this window when done...")
