# Import necessary libraries and modules
import customtkinter as ctk  # CustomTkinter for modern UI components
from tkinter import filedialog, messagebox  # For file selection dialogs
from study_content import (  # Import content generation functions
    generate_study_content, generate_flashcards, run_quiz, run_test, 
    generate_answers, generate_batch_mock_answers
)
from api.storage import upload_context_file, save_study_data_to_file  # API storage utilities
from PIL import Image  # For handling images
import sys  # System-specific parameters and functions
from pathlib import Path  # For file path manipulations
import requests  # For making HTTP requests
import json  # For JSON serialization and deserialization
import random  # For randomization
from study_data import StudyData  # Import the Study class for managing study data

# Initialize the StudyData object
study_data = StudyData(config={"storage_location": "file"})  # Use file storage for persistence

is_dark_mode = False  # Tracks the current theme (dark or light mode)
cards = []  # Stores flashcard data
layout_index = 0  # Index for navigating UI layouts
ui_layout_data = []  # Stores the UI layout data for flashcards

# Utility function to create a button with consistent styling
def create_button(parent, text, command, side="left", padx=5, pady=5):
    """
    Creates a button with specified text, command, and layout options.

    Args:
        parent: The parent container for the button.
        text: The text displayed on the button.
        command: The function to execute when the button is clicked.
        side: The side of the parent container to pack the button (default: "left").
        padx: Horizontal padding around the button (default: 5).
        pady: Vertical padding around the button (default: 5).

    Returns:
        The created button object.
    """
    btn = ctk.CTkButton(parent, text=text, command=command)
    btn.pack(side=side, padx=padx, pady=pady)
    return btn

# Toggles between dark and light mode for the UI
def toggle_dark_mode():
    """
    Toggles the application's appearance mode between dark and light themes.
    """
    global is_dark_mode
    is_dark_mode = not is_dark_mode
    ctk.set_appearance_mode("dark" if is_dark_mode else "light")

# Displays a specific flashcard UI based on the provided index
def show_ui_card(container, index):
    """
    Displays a flashcard UI layout in the specified container.

    Args:
        container: The parent container for the flashcard UI.
        index: The index of the flashcard layout to display.
    """
    global ui_layout_data
    selected = ctk.StringVar()  # Tracks the selected dropdown option

    # Clear existing widgets in the container
    for widget in container.winfo_children():
        widget.destroy()

    # Handle invalid index cases
    if index < 0 or index >= len(ui_layout_data):
        ctk.CTkLabel(container, text="No more cards.", font=("Helvetica", 12)).pack()
        return

    layout = ui_layout_data[index]
    answer_label = None
    correct_answer = ""
    feedback_label = None
    
    # Main layout frame to hold everything above navigation
    layout_frame = ctk.CTkFrame(container)
    layout_frame.pack(pady=10)

    submit_frame = None
    dropdown = None  # we'll need to access this inside lambda

    for element in layout:
        if element["type"] == "label":
            ctk.CTkLabel(layout_frame, text=element["text"], font=("Helvetica", 14, "bold")).pack(pady=10)

        elif element["type"] == "dropdown":
            selected.set("Choose an option")
            dropdown = ctk.CTkComboBox(layout_frame, values=element["options"], variable=selected)
            dropdown.pack(pady=5)
            correct_answer = element.get("correct", "")
            feedback_label = ctk.CTkLabel(layout_frame, text="", font=("Helvetica", 12))
            feedback_label.pack(pady=5)

            # Create the submit frame after dropdown
            submit_frame = ctk.CTkFrame(container)
            submit_frame.pack(pady=5)

        elif element["type"] == "button":
            if element["text"].lower() == "show answer":
                answer_label = ctk.CTkLabel(layout_frame, text="?", font=("Helvetica", 12))
                answer_label.pack(pady=10)
                create_button(layout_frame, "Show Answer", lambda: reveal_answer(answer_label, index), pady=5)

            elif element["text"].lower() == "submit":
                if submit_frame:
                    create_button(submit_frame, "Submit", lambda: [
                        check_answer(selected.get(), correct_answer, feedback_label),
                        dropdown.configure(state="disabled")
                    ], pady=5)

    # Navigation buttons — bottom section
    nav_frame = ctk.CTkFrame(container)
    nav_frame.pack(pady=10)

    if index > 0:
        create_button(nav_frame, "Previous", lambda: show_ui_card(container, index - 1))
    create_button(nav_frame, "Shuffle", lambda: shuffle_cards(container))
    if index < len(ui_layout_data) - 1:
        create_button(nav_frame, "Next", lambda: show_ui_card(container, index + 1))



# Reveals the correct answer for the current flashcard
def reveal_answer(label, index):
    """
    Reveals the correct answer for the current flashcard.

    Args:
        label: The label widget to update with the answer.
        index: The index of the current flashcard.
    """
    try:
        label.configure(text=cards[index]["answer"])
    except:
        label.configure(text="Answer unavailable")

# Shuffles the flashcards and rebuilds the UI layout
def shuffle_cards(container):
    """
    Shuffles the flashcards and updates the UI layout.

    Args:
        container: The parent container for the flashcard UI.
    """
    global cards, ui_layout_data

    random.shuffle(cards)  # Shuffle the flashcards

    layout_all = []
    for card in cards:
        # Skip cards with missing essential fields
        if "question" not in card or "answer" not in card:
            print(f"⚠️ Skipping malformed card: {card}")
            continue

        layout = [{"type": "label", "text": card["question"]}]
        options = card.get("options", [])

        if options and isinstance(options, list) and len(options) > 1:
            cleaned = [opt.split(". ", 1)[-1].strip() for opt in options]
            random.shuffle(cleaned)
            enumerated = [f"{i+1}. {opt}" for i, opt in enumerate(cleaned)]

            # Update card with fresh dropdown options
            card["options"] = enumerated
            answer = card.get("answer", "Unknown")
            layout.append({
                "type": "dropdown",
                "options": enumerated,
                "correct": answer
            })
            layout.append({"type": "button", "text": "Submit"})
        else:
            layout.append({"type": "button", "text": "Show Answer"})

        layout_all.append(layout)

    ui_layout_data = layout_all

    # Save the updated cards and layout to files
    with open("generated_cards.json", "w") as f:
        json.dump(cards, f, indent=2)
    with open("ui_layout.json", "w") as f:
        json.dump(ui_layout_data, f, indent=2)

    print("🔁 Cards shuffled and layout rebuilt")
    show_ui_card(container, 0)

# Checks the user's answer and provides feedback
def check_answer(selected, correct, feedback_label):
    """
    Compares the user's selected answer with the correct one and updates the feedback label.

    Args:
        selected: The user's selected answer.
        correct: The correct answer.
        feedback_label: The label widget to display feedback.
    """
    stripped = selected.split(". ", 1)[-1].strip()  # Remove enumeration prefix
    if stripped == correct.strip():
        feedback_label.configure(text="✅ Correct!", text_color="green")
    else:
        feedback_label.configure(text=f"❌ Incorrect. Correct: {correct}", text_color="red")

def setup_ui(root):
    """
    Sets up the main user interface for the application.

    Args:
        root: The root window of the application.
    """
    global card_frame
    ctk.set_appearance_mode("light")  # Set the default appearance mode to light
    base_dir = Path(sys._MEIPASS) if getattr(sys, 'frozen', False) else Path(__file__).resolve().parent
    assets_path = base_dir / "assets"
    moon_image_path = assets_path / "moon.png"

    # Load the moon image for the dark mode toggle button
    try:
        moon_image = Image.open(moon_image_path)
        moon_photo = ctk.CTkImage(light_image=moon_image, dark_image=moon_image, size=(30, 30))
    except:
        moon_photo = None

    # Add a dark mode toggle button if the image is available
    if moon_photo:
        ctk.CTkButton(
            root, image=moon_photo, text="", command=lambda: toggle_dark_mode(),
            fg_color="transparent", hover_color="lightblue", width=30, height=30, corner_radius=15
        ).place(x=10, y=10)

    # Add the main application title and description
    ctk.CTkLabel(root, text="Study Buddy", font=("Helvetica", 20, "bold"), text_color="blue").pack(pady=10)
    ctk.CTkLabel(
        root, text="Enter a topic and use the buttons below to generate study materials.", font=("Helvetica", 12)
    ).pack(pady=5)

    # Create the input frame for entering topics
    input_frame = ctk.CTkFrame(root)
    input_frame.pack(pady=10, padx=20, fill="x")
    ctk.CTkLabel(input_frame, text="Enter Topic:", font=("Helvetica", 12)).grid(row=0, column=0, padx=5, pady=5, sticky="w")
    entry = ctk.CTkEntry(input_frame, width=300, font=("Helvetica", 12))
    entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

    # Create the frame for displaying downloadable study data
    study_data_frame = ctk.CTkFrame(root)
    study_data_frame.pack(side="right", padx=10, pady=10, fill="y")
    ctk.CTkLabel(study_data_frame, text="Downloadable Content:", font=("Helvetica", 14, "bold")).pack(pady=5)
    study_data_box = ctk.CTkTextbox(study_data_frame, width=300, height=400, font=("Helvetica", 10))
    study_data_box.pack(fill="both", expand=True)

    # Function to update the study data display
    def update_study_data_display():
        """
        Updates the study data display box with the current study data.
        """
        study_data_box.delete("1.0", "end")
        for key, value in study_data.get_all_data().items():
            study_data_box.insert("end", f"{key.capitalize()}:\n{value if value else 'No data'}\n\n")

    # Create the button frame for generating study materials
    button_frame = ctk.CTkFrame(root)
    button_frame.pack(pady=10)

    # Create the frame for displaying flashcards
    global card_frame
    card_frame = ctk.CTkFrame(root)
    card_frame.pack(padx=20, pady=10, fill="both", expand=True)

    # Define the buttons and their respective commands
    buttons = [
        ctk.CTkButton(
            button_frame, text="Generate Study Content",
            command=lambda: (
                messagebox.showerror("Missing Topic", "Please enter a topic before generating content.")
                if not entry.get().strip()
                else [generate_study_content(entry.get(), study_data_box, study_data), update_study_data_display()]
            ),
            fg_color="blue"
        ),
        ctk.CTkButton(
            button_frame, text="Generate Flashcards",
            command=lambda: (
                messagebox.showerror("Missing Topic", "Please enter a topic before generating flashcards.")
                if not entry.get().strip()
                else generate_flashcards_with_mock_answers(entry.get(), study_data_box)
            ),
            fg_color="green"
        ),
        ctk.CTkButton(
            button_frame, text="Generate Quiz",
            command=lambda: (
                messagebox.showerror("Missing Topic", "Please enter a topic before generating a quiz.")
                if not entry.get().strip()
                else [run_quiz(entry.get(), study_data_box, study_data), update_study_data_display()]
            ),
            fg_color="orange"
        ),
        ctk.CTkButton(
            button_frame, text="Generate Test",
            command=lambda: (
                messagebox.showerror("Missing Topic", "Please enter a topic before generating a test.")
                if not entry.get().strip()
                else [run_test(entry.get(), study_data_box, study_data), update_study_data_display()]
            ),
            fg_color="orange"
        ),
        ctk.CTkButton(
            button_frame, text="Upload Context File",
            command=lambda: upload_file(study_data_box),
            fg_color="red"
        ),
        ctk.CTkButton(
            button_frame, text="Download Content",
            command=lambda: save_study_data_to_file(study_data),
            fg_color="coral"
        ),
        ctk.CTkButton(
            button_frame, text="Study Data Answers",
            command=lambda: [generate_answers(study_data_box, study_data), update_study_data_display()],
            fg_color="purple"
        ),
        ctk.CTkButton(
            button_frame, text="Send Topic to API",
            command=lambda: (
                messagebox.showerror("Missing Topic", "Please enter a topic to send to the API.")
                if not entry.get().strip()
                else send_topic_to_api(entry.get())
            ),
            fg_color="gray"
        ),
        ctk.CTkButton(
            button_frame, text="Show Topics from API",
            command=lambda: study_data_box.insert("end", "\n".join(get_topics_from_api()) + "\n"),
            fg_color="teal"
        ),
        ctk.CTkButton(
            button_frame, text="Load from Server",    
            command=lambda: prompt_server_load(entry, study_data_box),
            fg_color="orange"
        ),

    ]

    # Arrange the buttons in a grid layout
    for i, button in enumerate(buttons):
        button.grid(row=i // 2, column=i % 2, padx=10, pady=10)

def upload_file(study_data_box):
    """
    Opens a file dialog to upload a context file and displays the result in the study data box.

    Args:
        study_data_box: The text box widget to display the upload result.
    """
    file_path = filedialog.askopenfilename(title="Select a File", filetypes=(("Text Files", "*.txt"), ("All Files", "*.*")))
    if file_path:
        result = upload_context_file(file_path)
        study_data_box.insert("end", f"{result}\n")
        study_data_box.insert("end", f"File uploaded: {file_path}\n")

def send_topic_to_api(topic):
    """
    Sends the entered topic to the API for processing.

    Args:
        topic: The topic string to send to the API.
    """
    try:
        res = requests.post("http://127.0.0.1:5000/api/add_topic", json={"topic": topic}, timeout=5)
        if res.status_code == 200:
            print("✅ Sent to API:", topic)
        else:
            print("❌ API Error:", res.json())
    except Exception as e:
        show_server_connection_error("add_topic", e)

def get_topics_from_api():
    """
    Fetches the list of topics from the API.

    Returns:
        A list of topics or an error message if the API call fails.
    """
    try:
        res = requests.get("http://127.0.0.1:5000/api/get_topics", timeout=5)
        if res.status_code == 200:
            return res.json().get("topics", [])
        else:
            return ["Error fetching topics"]
    except Exception as e:
        show_server_connection_error("get_topics", e)
    
def prompt_server_load(entry, output_box):
    topic = entry.get().strip()
    if not topic:
        messagebox.showerror("Missing Topic", "Please enter a topic first.")
        return

    option_popup = ctk.CTkToplevel()
    option_popup.title("Select Content Type")
    option_popup.geometry("300x150")

    ctk.CTkLabel(option_popup, text="Choose content to load from server:", font=("Helvetica", 12)).pack(pady=10)

    selection = ctk.StringVar(value="all")
    dropdown = ctk.CTkComboBox(option_popup, values=["all", "flashcards", "quiz", "test"], variable=selection)
    dropdown.pack(pady=5)

    def confirm_choice():
        choice = selection.get()
        option_popup.destroy()
        if choice == "all":
            for route in ["flashcards", "quiz", "test"]:
                try:
                    res = requests.get(f"http://127.0.0.1:5000/api/{route}?topic={topic}")
                    output_box.insert("end", f"\n{route.title()}:\n{res.text}\n")
                except Exception as e:
                    show_server_connection_error(route, e)
        else:
            try:
                res = requests.get(f"http://127.0.0.1:5000/api/{choice}?topic={topic}")
                output_box.delete("1.0", "end")
                output_box.insert("end", f"{choice.title()}:\n{res.text}")
            except Exception as e:
                show_server_connection_error(choice, e)

    ctk.CTkButton(option_popup, text="Load", command=confirm_choice).pack(pady=10)

# Updated extractor that handles both multiple-choice and single-answer flashcards
def extract_cards_from_text(text):
    global cards
    cards = []
    blocks = text.strip().split("\n\n")

    for block in blocks:
        lines = block.strip().split("\n")

        question = None
        choices = []
        correct = None

        for line in lines:
            if line.startswith("Q:"):
                question = line[2:].strip()
            elif line.startswith("A:"):
                # Handle Q+A format with one correct answer
                correct = line[2:].strip()
                choices = [correct, "Incorrect 1", "Incorrect 2", "Incorrect 3"]
                break
            elif line.startswith("A.") or line.startswith("A:"):
                # Handle multiple choice
                ans_text = line[2:].strip()
                if "✔" in ans_text:
                    correct = ans_text.replace("✔", "").strip()
                choices.append(ans_text.replace("✔", "").strip())

        if question and correct and choices:
            cards.append([
                {"type": "label", "text": question},
                {"type": "dropdown", "options": choices, "correct": correct},
                {"type": "button", "text": "Submit"}
            ])

    return cards

def save_all_card_data():
    with open("generated_cards.json", "w") as f:
        json.dump(cards, f, indent=2)

    with open("ui_layout.json", "w") as f:
        json.dump(cards, f, indent=2)

def build_ui_from_file():
    global cards
    with open("ui_layout.json", "r") as f:
        cards = json.load(f)
    return cards


def rebuild_enumerated_options(card):
    """
    Clean and re-enumerate card['options'] to avoid dropdown disappearing after shuffle.
    """
    raw_options = [opt.split(". ", 1)[[-1]].strip() for opt in card.get("options", []) if opt.strip()]
    
    # Ensure correct answer is included (even if it was dropped/malformed)
    if card.get("answer") and card["answer"] not in raw_options:
        raw_options.append(card["answer"])

    # Deduplicate, shuffle, and re-enumerate
    unique = list(dict.fromkeys(raw_options))  # preserves order
    random.shuffle(unique)
    return [f"{i+1}. {opt}" for i, opt in enumerate(unique)]

def show_server_connection_error(route, exception):
    """
    Display a popup and print error if server connection fails.

    Args:
        route (str): The attempted API route (e.g., 'quiz').
        exception (Exception): The exception raised.
    """
    error_msg = f"❌ Could not connect to server route '/api/{route}':\n{exception}"
    print(error_msg)
    messagebox.showerror("Server Connection Error", error_msg)

def generate_flashcards_with_mock_answers(topic, output_box):
    global cards, ui_layout_data

    # Step 1: Generate flashcards normally
    generate_flashcards(topic, output_box, study_data)

    # Step 2: Parse flashcards into a list of {question, answer}
    raw_text = study_data["flashcards"]
    if not raw_text:
        messagebox.showerror("Error", "No flashcards were generated.")
        return

    parsed_cards = []
    blocks = raw_text.strip().split("\n\n")
    for block in blocks:
        lines = block.strip().splitlines()
        q, a = None, None
        for line in lines:
            if line.startswith("Q:"):
                q = line[2:].strip()
            elif line.startswith("A:"):
                a = line[2:].strip()
        if q and a:
            parsed_cards.append({"question": q, "answer": a})

    cards = parsed_cards

    # Step 3: Generate distractors
    answers_dict = generate_batch_mock_answers(cards)

    # Step 4: Build UI layouts
    layout_all = []
    for card in cards:
        q = card["question"]
        options = answers_dict.get(q, [card["answer"], "Wrong 1", "Wrong 2", "Wrong 3"])
        random.shuffle(options)
        card["options"] = options  # Save options for shuffling

        layout = [
            {"type": "label", "text": q},
            {"type": "dropdown", "options": [f"{i+1}. {opt}" for i, opt in enumerate(options)], "correct": card["answer"]},
            {"type": "button", "text": "Submit"}
        ]
        layout_all.append(layout)

    ui_layout_data = layout_all

    # Step 5: Save to files
    with open("generated_cards.json", "w") as f:
        json.dump(cards, f, indent=2)
    with open("ui_layout.json", "w") as f:
        json.dump(ui_layout_data, f, indent=2)

    # Step 6: Display the first card
    show_ui_card(card_frame, 0)



def run_gui():
    """
    Initializes and runs the main GUI application.
    """
    root = ctk.CTk()
    root.geometry("1000x700")  # Set the window size
    root.title("Study Buddy")  # Set the window title
    setup_ui(root)  # Set up the UI components
    root.mainloop()  # Start the main event loop

if __name__ == "__main__":
    run_gui()  # Entry point for the application