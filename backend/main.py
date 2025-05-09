import customtkinter as ctk
from dotenv import load_dotenv
import sys, os
from ui import setup_ui
from api import app  # ✅ Use the app defined in api/__init__.py
from flask import Flask, send_from_directory
from study_data import StudyData  # Import the StudyData class
import api.routes  # Import routes to register them with the Flask app (ensures routes are registered)

CURRENT_VERSION = "v1.0.5"
GITHUB_API_URL = "https://api.github.com/repos/Shiboof/study_buddy/releases/latest"

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load .env file for API keys, etc.
load_dotenv()
study_data = StudyData(config={"storage_location": "file"})

def run_gui():
    root = ctk.CTk()
    root.title("Study Buddy")
    root.geometry("1000x600")
    setup_ui(root)
    root.mainloop()

if __name__ == "__main__":
    if "RUN_GUI" in os.environ:
        run_gui()
    else:
        app.run(debug=True)
