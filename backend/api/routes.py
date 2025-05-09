from api import app
from flask import request, jsonify, send_from_directory
from study_data import StudyData
import os, json
import api.storage_utils as storage_utils
from flashcard_web_extraction import extract_cards_for_web_ui, save_all_web_card_data

from study_core import (
    generate_study_content,
    generate_flashcards,
    run_quiz,
    run_test,
    generate_answers,
    generate_batch_mock_answers
)

study_data = StudyData(config={"storage_location": "file"})

@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>")
def serve_static(path):
    full_path = os.path.join(app.static_folder, path)
    if os.path.isfile(full_path):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, "index.html")

@app.route("/api/health")
def health():
    return {"status": "ok"}

@app.route("/api/add_topic", methods=["POST"])
def add_topic():
    data = request.json
    topic = data.get("topic")
    if not topic:
        return jsonify({"error": "Topic is required"}), 400
    study_data["topics"] = study_data.get("topics", []) + [topic]
    return jsonify({"message": "Topic added", "topic": topic})

@app.route("/api/get_topics", methods=["GET"])
def get_topics():
    return jsonify({"topics": study_data.get("topics", [])})

class MockText:
    def __init__(self):
        self.output = []

    def insert(self, index, text):
        self.output.append(text)

    def delete(self, q, a):
        self.output = []

    def getvalue(self):
        return "".join(self.output)
    
@app.route("/api/study_content", methods=["POST"])
def api_study_content():
    topic = request.json.get("topic", "").strip()
    if not topic:
        return jsonify({"error": "Missing topic"}), 400

    force = request.args.get("force", "false").lower() == "true"
    if not force:
        cached = storage_utils.load_material(topic)
        if cached and "study_content" in cached:
            return cached["study_content"]

    fake_box = MockText()
    generate_study_content(topic, fake_box, study_data)
    content = fake_box.getvalue()
    storage_utils.save_material(topic, "study_content", content)

    return content

@app.route("/api/flashcards", methods=["GET", "POST"])
def api_flashcards():
    topic = request.args.get("topic", "").strip()
    if request.method == "POST":
        topic = request.json.get("topic", "").strip()

    force = request.args.get("force", "false").lower() == "true"
    if not topic:
        return jsonify({"error": "Missing topic"}), 400

    if not force:
        cached = storage_utils.load_material(topic)
        if cached and "flashcards" in cached:
            content = cached["flashcards"]
            return jsonify(extract_cards_for_web_ui(content))

    fake_box = MockText()
    generate_flashcards(topic, fake_box, study_data)
    content = fake_box.getvalue()
    storage_utils.save_material(topic, "flashcards", content)

    cards = extract_cards_for_web_ui(content)
    return jsonify(cards)

@app.route("/api/quiz", methods=["GET", "POST"])
def api_quiz():
    topic = request.args.get("topic", "").strip()
    if request.method == "POST":
        topic = request.json.get("topic", "").strip()

    force = request.args.get("force", "false").lower() == "true"
    if not topic:
        return jsonify({"error": "Missing topic"}), 400

    if not force:
        cached = storage_utils.load_material(topic)
        if cached and "quiz" in cached:
            return cached["quiz"]

    fake_box = MockText()
    run_quiz(topic, fake_box, study_data)
    content = fake_box.getvalue()
    storage_utils.save_material(topic, "quiz", content)
    return content

@app.route("/api/test", methods=["GET", "POST"])
def api_test():
    topic = request.args.get("topic", "").strip()
    if request.method == "POST":
        topic = request.json.get("topic", "").strip()

    force = request.args.get("force", "false").lower() == "true"
    if not topic:
        return jsonify({"error": "Missing topic"}), 400

    if not force:
        cached = storage_utils.load_material(topic)
        if cached and "test" in cached:
            return cached["test"]

    fake_box = MockText()
    run_test(topic, fake_box, study_data)
    content = fake_box.getvalue()
    storage_utils.save_material(topic, "test", content)
    return content

@app.route("/api/generate_all", methods=["POST"])
def generate_all():
    topic = request.json.get("topic")
    if not topic:
        return jsonify({"error": "Missing topic"}), 400

    fake_box = MockText()
    generate_study_content(topic, fake_box, study_data)
    generate_flashcards(topic, fake_box, study_data)
    run_quiz(topic, fake_box, study_data)
    run_test(topic, fake_box, study_data)

    return jsonify({"message": "All content generated for topic", "topic": topic})

@app.route("/api/get_flashcard_layout")
def get_flashcard_layout():
    topic = request.args.get("topic", "").strip()
    path = os.path.join("stored_materials", f"{topic}.json")
    if not os.path.exists(path):
        return jsonify({"error": "No saved content for topic"}), 404

    try:
        with open(path, "r") as f:
            data = json.load(f)
            raw_text = data.get("flashcards", "")
    except:
        return jsonify({"error": "Could not read flashcards"}), 500

    global cards
    cards = extract_cards_for_web_ui(raw_text)
    save_all_web_card_data()

    with open("ui_layout.json", "r") as layout_file:
        layout = json.load(layout_file)

    return jsonify({"layout": layout})
