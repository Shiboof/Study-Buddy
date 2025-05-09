from openai import OpenAI, OpenAIError, RateLimitError, APIConnectionError, AuthenticationError
from dotenv import load_dotenv
from api.storage import get_uploaded_context
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import os
import re

load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("❌ Missing OPENAI_API_KEY in environment. Check your .env file.")
else:
    print("✅ Loaded OpenAI API key.")

client = OpenAI(api_key=api_key)

def make_prompt(role, user_msg):
    return [{"role": "system", "content": role}, {"role": "user", "content": user_msg}]

def call_openai_api(model, messages, max_tokens=500, temperature=0.7):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content
    except (AuthenticationError, RateLimitError, APIConnectionError, OpenAIError) as e:
        raise RuntimeError(f"OpenAI API error: {e}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error: {e}")
    
def generate_study_content(topic, output_box, study_data):
    print(f"Generating study content for {topic}...")
    try:
        context = get_uploaded_context()
        user_msg = (
            f"Using the following context:\n\n{context}\n\n"
            f"Generate a detailed and beginner-friendly study summary for the topic '{topic}'. "
            f"Structure the summary into sections with headers."
        )
        messages = make_prompt("You are a helpful educational assistant.", user_msg)
        summary = call_openai_api("gpt-3.5-turbo-0125", messages)

        output_box.insert("end", summary)
        study_data["content"] = summary
    except Exception as e:
        output_box.insert("end", f"Error generating study content: {e}")

def generate_flashcards(topic, output_box, study_data):
    try:
        context = get_uploaded_context()
        existing = study_data.get("flashcards", "")
        user_msg = (
            f"Using this context:\n{context}\n\n"
            f"Existing flashcards:\n{existing}\n\n"
            f"Generate 15 new, unique flashcards for '{topic}' in the format:\nQ: ...\nA: ..."
        )
        messages = make_prompt("You are an assistant that creates educational flashcards.", user_msg)
        flashcards = call_openai_api("gpt-3.5-turbo", messages)

        output_box.insert("end", "Flashcards:\n" + flashcards)
        study_data["flashcards"] = study_data.get("flashcards", "") + "\n\n" + flashcards
    except Exception as e:
        output_box.insert("end", f"Error generating flashcards: {e}")

def run_quiz(topic, output_box, study_data):
    try:
        context = get_uploaded_context()
        existing = study_data.get("quiz", "")
        user_msg = (
            f"Using this context:\n{context}\n\n"
            f"Previously generated quiz:\n{existing}\n\n"
            f"Create 20 new, unique multiple-choice quiz questions for '{topic}'. Format:\nQ: ...\nA. ...\nB. ..."
        )
        messages = make_prompt("You are an assistant that writes structured multiple-choice quizzes.", user_msg)
        quiz = call_openai_api("gpt-3.5-turbo", messages, max_tokens=1500)

        output_box.insert("end", "Quiz:\n" + quiz)
        study_data["quiz"] = study_data.get("quiz", "") + "\n\n" + quiz
    except Exception as e:
        output_box.insert("end", f"Error generating quiz: {e}")

def run_test(topic, output_box, study_data):
    def prompt_mc():
        context = get_uploaded_context()
        existing = study_data.get("test", "")
        user_msg = (
            f"Using this context:\n{context}\n\n"
            f"Previously generated test:\n{existing}\n\n"
            f"Create 30 new multiple-choice test questions about '{topic}' with 4 options each."
        )
        return call_openai_api("gpt-3.5-turbo", make_prompt("You are a structured test generator.", user_msg), max_tokens=1500)

    def prompt_fill():
        context = get_uploaded_context()
        existing = study_data.get("test", "")
        user_msg = (
            f"Using this context:\n{context}\n\n"
            f"Previously generated test:\n{existing}\n\n"
            f"Create 30 new fill-in-the-blank questions about '{topic}'."
        )
        return call_openai_api("gpt-3.5-turbo", make_prompt("You are a structured test generator.", user_msg), max_tokens=1000)

    try:
        with ThreadPoolExecutor() as executor:
            mc_future = executor.submit(prompt_mc)
            fill_future = executor.submit(prompt_fill)
            mc_questions = mc_future.result()
            fill_questions = fill_future.result()

            output_box.insert("end", f"\nMultiple-Choice Questions:\n{mc_questions}\n")
            output_box.insert("end", f"\nFill-in-the-Blank Questions:\n{fill_questions}\n")
            study_data["test"] = study_data.get("test", "") + "\n\n" + mc_questions + "\n" + fill_questions
    except Exception as e:
        output_box.insert("end", f"Error generating test: {e}")

def generate_answers(output_box, study_data):
    output_box.delete("1.0", "end")
    output_box.insert("end", "Generating answers for quizzes and tests...\n")

    try:
        quiz_data = study_data.get("quiz", "")
        test_data = study_data.get("test", "")

        if not quiz_data and not test_data:
            raise Exception("No quiz or test data found to generate answers.")

        answers = ""

        def answer_prompt(question):
            user_msg = f"Provide a clear and correct answer to the following question:\n{question}"
            messages = make_prompt("You provide direct answers to educational questions.", user_msg)
            return call_openai_api("gpt-3.5-turbo", messages).strip()

        if quiz_data:
            output_box.insert("end", "Generating answers for the quiz.\n")
            quiz_questions = [line.strip() for line in quiz_data.split("\n") if line.strip().startswith("Q")]
            quiz_answers = []
            for q in quiz_questions:
                try:
                    a = answer_prompt(q)
                    quiz_answers.append(f"{q}\nAnswer: {a}\n")
                except Exception as e:
                    quiz_answers.append(f"{q}\nAnswer: Error - {e}\n")
            answers += "Quiz Answers:\n" + "\n".join(quiz_answers) + "\n\n"

        if test_data:
            output_box.insert("end", "Generating answers for the test.\n")
            test_questions = [line.strip() for line in test_data.split("\n") if line.strip().startswith("Q")]
            test_answers = []
            for q in test_questions:
                try:
                    a = answer_prompt(q)
                    test_answers.append(f"{q}\nAnswer: {a}\n")
                except Exception as e:
                    test_answers.append(f"{q}\nAnswer: Error - {e}\n")
            answers += "Test Answers:\n" + "\n".join(test_answers) + "\n\n"

        study_data["answers"] = answers
        output_box.insert("end", f"\nAnswers:\n{answers}")
    except Exception as e:
        output_box.insert("end", f"Error generating answers: {e}")


def generate_batch_mock_answers(cards):
    """
    Generates three multiple-choice distractors for each flashcard using the OpenAI API.

    Args:
        cards (list): List of flashcard dictionaries, each containing 'question' and 'answer'.

    Returns:
        dict: Mapping of each question to a list containing the correct answer and three distractors.
    """
    try:
        import re

        joined_questions = "\n".join(
            f"Q: {card['question']}\nA: {card['answer']}"
            for card in cards if card.get("answer")
        )

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

        # Retry missing
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
