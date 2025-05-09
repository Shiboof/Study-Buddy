from waitress import serve
from api import app

if __name__ == "__main__":
    print("🚀 Starting Flask app with Waitress on http://0.0.0.0:8000")
    serve(app, host="0.0.0.0", port=8000)
