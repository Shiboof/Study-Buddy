import json
import os
import requests

uploaded_context = ""
TOPIC_FILE = os.path.join(os.path.dirname(__file__), "topics.json")


def upload_context_file(file_path):
    """Read and store context from a file (used programmatically)."""
    global uploaded_context
    try:
        with open(file_path, "r") as file:
            uploaded_context = file.read()
        print("✅ File uploaded successfully and context stored.")
    except Exception as e:
        print(f"❌ Error reading file: {str(e)}")


def get_uploaded_context():
    """Return the currently uploaded context string."""
    return uploaded_context


def save_study_data_to_file(study_data, file_path="study_output.txt"):
    """
    Save study content to a specified file path.
    In cloud deployments, file_path should be predefined or passed in via API.
    """
    try:
        with open(file_path, "w") as file:
            for section in ["content", "flashcards", "quiz", "test", "answers"]:
                file.write(f"{section.capitalize()}:\n")
                value = study_data.get(section) or ""
                file.write(value + "\n\n")
        print(f"✅ Study material saved to {file_path}")
    except Exception as e:
        print(f"❌ Failed to save study material: {str(e)}")


def add_topic_to_file(topic):
    """Append a new topic to the local topics.json file."""
    topics = get_all_topics_from_file()
    topics.append(topic)
    with open(TOPIC_FILE, "w") as f:
        json.dump(topics, f)


def get_all_topics_from_file():
    """Return list of stored topics, or empty list if not found."""
    if not os.path.exists(TOPIC_FILE):
        return []
    with open(TOPIC_FILE, "r") as f:
        return json.load(f)


def load_from_server(route, topic):
    """
    Fetch content from the backend server via HTTP for a given route/topic.
    `box` argument is removed — use return value instead.
    """
    if not topic:
        raise ValueError("Missing topic.")

    try:
        res = requests.get(f"http://127.0.0.1:8000/api/{route}?topic={topic}")
        res.raise_for_status()
        return res.text
    except Exception as e:
        print(f"❌ Failed to load from {route}: {e}")
        return f"Error loading {route}: {e}"
