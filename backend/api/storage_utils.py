import os, json

STORAGE_DIR = os.path.join(os.getcwd(), "stored_materials")
os.makedirs(STORAGE_DIR, exist_ok=True)

def save_material(topic, material_type, content):
    filename = os.path.join(STORAGE_DIR, f"{topic.lower()}.json")
    data = load_material(topic) or {}
    data[material_type] = content
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

def load_material(topic):
    filename = os.path.join(STORAGE_DIR, f"{topic.lower()}.json")
    if os.path.exists(filename):
        with open(filename) as f:
            return json.load(f)
    return None