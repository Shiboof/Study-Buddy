import os
from flask import Flask
from flask_cors import CORS

# Resolve the absolute path to the static (frontend) folder
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
STATIC_FOLDER = os.path.join(BASE_DIR, "public")

# Initialize the Flask app with static file serving
app = Flask(
    __name__,
    static_folder=STATIC_FOLDER,
    static_url_path=""  # serve static files from root "/"
)

# Enable CORS for all /api/* routes (can restrict origins if needed)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Register routes
from api import routes
