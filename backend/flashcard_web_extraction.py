import json
import re

cards = []

def extract_cards_for_web_ui(text):
    from study_content import generate_batch_mock_answers

    cards = []
    raw_pairs = []

    blocks = text.strip().split("\n\n")

    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) == 2 and lines[0].startswith("Q:") and lines[1].startswith("A:"):
            question = lines[0][2:].strip()
            answer = lines[1][2:].strip()
            raw_pairs.append({"question": question, "answer": answer})

    # ✅ Stop here if raw_pairs is empty
    if not raw_pairs:
        print("❌ No valid Q/A pairs found. Skipping card generation.")
        return []

    # Generate distractors
    try:
        distractor_map = generate_batch_mock_answers(raw_pairs)
    except Exception as e:
        print("⚠️ GPT fallback:", e)
        distractor_map = {pair["question"]: ["Wrong 1", "Wrong 2", "Wrong 3"] for pair in raw_pairs}

    for pair in raw_pairs:
        q = pair["question"]
        a = pair["answer"]
        distractors = distractor_map.get(q, ["Wrong 1", "Wrong 2", "Wrong 3"])
        clean_distractors = [re.sub(r"^Distractor \d+: ", "", d).strip() for d in distractors]
        options = list(set(clean_distractors + [a]))
        from random import shuffle
        shuffle(options)

        cards.append({
            "question": q,
            "answer": a,
            "options": options
        })

    return cards

def save_all_web_card_data():
    with open("ui_layout.json", "w") as f:
        json.dump(cards, f, indent=2)

def build_web_ui_from_file():
    global cards
    with open("ui_layout.json", "r") as f:
        cards = json.load(f)
    return cards