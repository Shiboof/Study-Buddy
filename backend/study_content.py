# Import necessary libraries and modules
import tkinter as tk  # For GUI components
from tkinter import messagebox  # For displaying error messages
from openai import OpenAI, OpenAIError, RateLimitError, APIConnectionError, AuthenticationError  # OpenAI API integration
from dotenv import load_dotenv  # For loading environment variables
from concurrent.futures import ThreadPoolExecutor  # For running tasks concurrently
from api.storage import get_uploaded_context  # Custom API for retrieving uploaded context
from pathlib import Path  # For file path manipulations
import sys  # System-specific parameters and functions

# Utility functions for managing output and errors
def start_output(topic, label, box):
    """
    Clears the output box and inserts a message indicating the start of a process.

    Args:
        topic: The topic being processed.
        label: The label describing the process (e.g., "Generating study content").
        box: The text box widget to display the output.
    """
    box.delete("1.0", tk.END)
    box.insert(tk.END, f"{label} for {topic}...\n")

def show_error(box, msg):
    """
    Displays an error message in the output box and as a popup.

    Args:
        box: The text box widget to display the error message.
        msg: The error message to display.
    """
    box.insert(tk.END, msg)
    messagebox.showerror("Error", msg)

def make_prompt(role, user_msg):
    """
    Creates a structured prompt for the OpenAI API.

    Args:
        role: The role of the assistant (e.g., "You are a helpful study assistant").
        user_msg: The user's message or request.

    Returns:
        A list of dictionaries representing the prompt structure.
    """
    return [{"role": "system", "content": role}, {"role": "user", "content": user_msg}]

# Load environment variables from a .env file
if getattr(sys, 'frozen', False):  # Check if the script is running as a frozen executable
    base_dir = Path(sys._MEIPASS)
else:
    base_dir = Path(__file__).resolve().parent

env_path = base_dir / ".env"
load_dotenv(dotenv_path=env_path)

# Initialize the OpenAI client
client = OpenAI()

# Function to call the OpenAI API
def call_openai_api(model, messages, max_tokens=500, temperature=0.7):
    """
    Sends a request to the OpenAI API and returns the response.

    Args:
        model: The OpenAI model to use (e.g., "gpt-3.5-turbo").
        messages: The prompt messages to send to the API.
        max_tokens: The maximum number of tokens in the response (default: 500).
        temperature: The randomness of the response (default: 0.7).

    Returns:
        The content of the API response.

    Raises:
        RuntimeError: If an error occurs during the API call.
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content
    except AuthenticationError:
        raise RuntimeError("Authentication failed. Please check your OpenAI API key.")
    except RateLimitError:
        raise RuntimeError("Rate limit exceeded. Please wait and try again later.")
    except APIConnectionError:
        raise RuntimeError("Failed to connect to OpenAI API. Please check your internet connection.")
    except OpenAIError as e:
        raise RuntimeError(f"An OpenAI API error occurred: {e}")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {e}")

# Function to generate study content
def generate_study_content(topic, output_box, study_data):
    """
    Generates a structured study summary for a given topic using the OpenAI API.

    Args:
        topic (str): The study topic.
        output_box (tk.Text): The text widget for displaying output.
        study_data (StudyData): An instance of the StudyData class to store the result.
    """
    start_output(topic, "Generating study content", output_box)

    try:
        context = get_uploaded_context()
        user_msg = (
            f"Using the following context:\n\n{context}\n\n"
            f"Generate a detailed and beginner-friendly study summary for the topic '{topic}'. "
            f"Structure the summary into sections with headers."
        )
        messages = make_prompt("You are a helpful educational assistant.", user_msg)
        summary = call_openai_api("gpt-3.5-turbo-0125", messages)

        output_box.insert(tk.END, summary)
        study_data["content"] = summary

    except RuntimeError as e:
        show_error(output_box, f"Error generating study content: {e}")
    except Exception as e:
        show_error(output_box, f"Unexpected error: {e}")

# Function to generate flashcards
def generate_flashcards(topic, output_box, study_data):
    """
    Generates beginner-friendly flashcards for a given topic using the OpenAI API.

    Args:
        topic (str): The study topic.
        output_box (tk.Text): The text widget to display the generated flashcards.
        study_data (StudyData): Instance to store the flashcard content.
    """
    start_output(topic, "Generating flashcards", output_box)

    try:
        context = get_uploaded_context()
        user_msg = (
            f"Using the following context:\n\n{context}\n\n"
            f"Generate 15 flashcards for someone learning about '{topic}'. "
            f"Each flashcard should be formatted like:\nQ: What is ...?\nA: ...\n"
        )
        messages = make_prompt("You are an assistant that creates educational flashcards.", user_msg)
        flashcards = call_openai_api("gpt-3.5-turbo", messages)

        output_box.insert(tk.END, "Flashcards:\n" + flashcards)
        study_data["flashcards"] = flashcards

    except RuntimeError as e:
        show_error(output_box, f"Error generating flashcards: {e}")
    except Exception as e:
        show_error(output_box, f"Unexpected error: {e}")


# Function to generate a quiz
def run_quiz(topic, output_box, study_data):
    """
    Generates a structured multiple-choice quiz for a given topic using the OpenAI API.

    Args:
        topic (str): The quiz topic.
        output_box (tk.Text): The text widget for displaying the generated quiz.
        study_data (StudyData): Instance to store the quiz content.
    """
    start_output(topic, "Generating quiz", output_box)

    try:
        context = get_uploaded_context()
        user_msg = (
            f"Using the following context:\n\n{context}\n\n"
            f"Create a 20-question multiple-choice quiz on the topic '{topic}'. "
            f"Each question must have 4 options labeled A, B, C, and D.\n"
            f"Format each question like this:\n"
            f"Q1: What is ...?\nA. Option 1\nB. Option 2\nC. Option 3\nD. Option 4"
        )
        messages = make_prompt("You are an assistant that writes structured multiple-choice quizzes.", user_msg)
        quiz = call_openai_api("gpt-3.5-turbo", messages, max_tokens=1500)

        output_box.insert(tk.END, "Quiz:\n" + quiz)
        study_data["quiz"] = quiz

    except RuntimeError as e:
        show_error(output_box, f"Error generating quiz: {e}")
    except Exception as e:
        show_error(output_box, f"Unexpected error: {e}")

# Function to generate a test
def run_test(topic, output_box, study_data):
    """
    Generates a mixed-format test for a given topic using the OpenAI API, including 
    multiple-choice and fill-in-the-blank questions.

    Args:
        topic (str): The test topic.
        output_box (tk.Text): The text widget to display the generated test.
        study_data (StudyData): Instance to store the full test content.
    """
    start_output(topic, "Generating test", output_box)

    def prompt_mc():
        context = get_uploaded_context()
        user_msg = (
            f"Using the following context:\n\n{context}\n\n"
            f"Create 30 multiple-choice questions about '{topic}'. "
            f"Each question must have 4 options labeled A, B, C, and D.\n"
            f"Format like:\nQ1: What is ...?\nA. Option 1\nB. Option 2\nC. Option 3\nD. Option 4"
        )
        return call_openai_api("gpt-3.5-turbo", make_prompt(
            "You are a structured test generator.", user_msg), max_tokens=1500)

    def prompt_fill():
        context = get_uploaded_context()
        user_msg = (
            f"Using the following context:\n\n{context}\n\n"
            f"Create 30 fill-in-the-blank questions about '{topic}'. "
            f"Format like:\nQ31: _____ is the capital of France."
        )
        return call_openai_api("gpt-3.5-turbo", make_prompt(
            "You are a structured test generator.", user_msg), max_tokens=1000)

    try:
        with ThreadPoolExecutor() as executor:
            mc_future = executor.submit(prompt_mc)
            fill_future = executor.submit(prompt_fill)

            mc_questions = mc_future.result()
            fill_questions = fill_future.result()

            output_box.insert(tk.END, f"\nMultiple-Choice Questions:\n{mc_questions}\n")
            output_box.insert(tk.END, f"\nFill-in-the-Blank Questions:\n{fill_questions}\n")

            study_data["test"] = f"{mc_questions}\n{fill_questions}"

    except RuntimeError as e:
        show_error(output_box, f"Error generating test: {e}")
    except Exception as e:
        show_error(output_box, f"Unexpected error: {e}")

# Function to generate answers for quizzes and tests
def generate_answers(output_box, study_data):
    """
    Generates answers for quizzes and tests stored in the study_data.

    Args:
        output_box (tk.Text): The text widget to display generated answers.
        study_data (StudyData): Contains stored quiz and test content.
    """
    output_box.delete("1.0", tk.END)
    output_box.insert(tk.END, "Generating answers for quizzes and tests...\n")

    try:
        quiz_data = study_data["quiz"]
        test_data = study_data["test"]

        if not quiz_data and not test_data:
            raise Exception("No quiz or test data found to generate answers.")

        answers = ""

        def answer_prompt(question):
            user_msg = f"Provide a clear and correct answer to the following question:\n{question}"
            messages = make_prompt("You provide direct answers to educational questions.", user_msg)
            return call_openai_api("gpt-3.5-turbo", messages).strip()

        if quiz_data:
            output_box.insert(tk.END, "Generating answers for the quiz...\n")
            quiz_answers = [
                f"{q}\nAnswer: {answer_prompt(q)}\n"
                for q in quiz_data.split("\n") if q.strip().startswith("Q")
            ]
            answers += "Quiz Answers:\n" + "\n".join(quiz_answers) + "\n\n"

        if test_data:
            output_box.insert(tk.END, "Generating answers for the test...\n")
            test_answers = [
                f"{q}\nAnswer: {answer_prompt(q)}\n"
                for q in test_data.split("\n") if q.strip().startswith("Q")
            ]
            answers += "Test Answers:\n" + "\n".join(test_answers) + "\n\n"

        study_data["answers"] = answers
        output_box.insert(tk.END, f"\nAnswers:\n{answers}")

    except RuntimeError as e:
        show_error(output_box, f"Error generating answers: {e}")
    except Exception as e:
        show_error(output_box, f"Unexpected error: {e}")

# Function to generate batch mock answers for flashcards
def generate_batch_mock_answers(cards):
    """
    Generates three multiple-choice distractors for each flashcard using the OpenAI API.
    """
    try:
        if not cards:
            print("⚠️ No flashcards provided to generate_batch_mock_answers.")
            return {}

        import re

        joined_questions = "\n".join(
            f"Q: {card['question']}\nA: {card['answer']}"
            for card in cards if card.get("answer")
        )

        if not joined_questions.strip():
            print("⚠️ No valid Q&A content to send to OpenAI.")
            return {}

        user_msg = (
            f"For each Q&A below, generate 3 plausible but incorrect multiple choice answers.\n"
            f"Format like:\n\n"
            f"Question: ...\nCorrect: ...\nChoices:\n- Distractor 1\n- Distractor 2\n- Distractor 3\n\n"
            f"Content:\n{joined_questions}"
        )

        messages = make_prompt("You are an assistant that creates distractors for educational multiple-choice questions.", user_msg)
        raw = call_openai_api("gpt-3.5-turbo", messages, max_tokens=2000)

        output = {}
        current_q, current_a, choices = "", "", []

        for line in raw.strip().splitlines():
            if line.lower().startswith("question:"):
                if current_q and current_a and choices:
                    output[current_q.strip()] = [current_a.strip()] + choices[:3]
                current_q = line.split(":", 1)[1].strip()
                current_a, choices = "", []
            elif line.lower().startswith("correct:"):
                current_a = line.split(":", 1)[1].strip()
            elif line.strip().startswith("-"):
                try:
                    cleaned = re.sub(r"(?i)^incorrect option\s*\d*[:\-\.]?\s*", "", line.strip("- ").strip())
                except Exception as e:
                    print(f"⚠️ Regex cleanup failed: {e}")
                    cleaned = line.strip("- ").strip()
                choices.append(cleaned)

        if current_q and current_a and choices:
            output[current_q.strip()] = [current_a.strip()] + choices[:3]

        # Retry missing questions
        all_questions = {card['question']: card['answer'] for card in cards if card.get('answer')}
        for q, a in all_questions.items():
            if q.strip() not in output:
                print(f"🔁 Retrying distractors for: {q}")
                try:
                    retry_msg = (
                        f"The correct answer is: {a}\n"
                        f"Question: {q}\n\n"
                        f"Generate 3 plausible but incorrect answers.\n"
                        f"Format:\n- Incorrect Option 1\n- Incorrect Option 2\n- Incorrect Option 3"
                    )
                    retry_response = call_openai_api("gpt-3.5-turbo", make_prompt(
                        "You generate plausible but incorrect answers for quizzes.", retry_msg), max_tokens=300)

                    distractors_raw = re.findall(r"^- (.+)", retry_response, re.MULTILINE)
                    distractors = [re.sub(r"(?i)^incorrect option\s*\d*[:\-\.]?\s*", "", d.strip()) for d in distractors_raw]

                    if distractors:
                        output[q.strip()] = [a] + distractors[:3]
                        print(f"✅ Retry succeeded for: {q}")
                    else:
                        raise ValueError("No valid distractors parsed.")

                except Exception as e:
                    print(f"❌ Retry failed for '{q}': {e}")
                    output[q.strip()] = [a, "Incorrect guess", "Misconception", "Wrong assumption"]

        return output

    except Exception as e:
        print(f"❌ Error in batch distractor generation: {e}")
        return {}


