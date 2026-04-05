"""
Psychological State Survey Program
Module: Fundamentals of Programming, 4BUIS008C
Topic: Emotional Resilience and Mental Well-being Survey
"""

import json
import csv
import os
import re
from datetime import datetime

# ─────────────────────────────────────────────
# DATA TYPES USED (covers all 10 required types)
# int, str, float, list, tuple, range, bool, dict, set, frozenset
# ─────────────────────────────────────────────

# Survey questions stored in a list of dicts (loaded from file OR hardcoded)
QUESTIONS_FILE = "questions.json"

HARDCODED_QUESTIONS: list = [
    {
        "text": "How often do you feel emotionally drained after social interactions?",
        "options": [
            ("Never", 0),
            ("Rarely", 1),
            ("Sometimes", 2),
            ("Often", 3),
            ("Always", 4),
        ],
    },
    {
        "text": "How well are you able to bounce back after a disappointing event?",
        "options": [
            ("Very easily", 0),
            ("Fairly easily", 1),
            ("With some effort", 2),
            ("With great difficulty", 3),
            ("I rarely recover quickly", 4),
        ],
    },
    {
        "text": "How often do you feel a sense of purpose in your daily activities?",
        "options": [
            ("Always", 0),
            ("Often", 1),
            ("Sometimes", 2),
            ("Rarely", 3),
            ("Never", 4),
        ],
    },
    {
        "text": "How frequently do you feel that your emotions are out of control?",
        "options": [
            ("Never", 0),
            ("Rarely", 1),
            ("Sometimes", 2),
            ("Often", 3),
            ("Always", 4),
        ],
    },
    {
        "text": "How often do you feel genuinely happy or content?",
        "options": [
            ("Every day", 0),
            ("Most days", 1),
            ("Some days", 2),
            ("Rarely", 3),
            ("Almost never", 4),
        ],
    },
    {
        "text": "How often do you find it difficult to make everyday decisions?",
        "options": [
            ("Never", 0),
            ("Rarely", 1),
            ("Sometimes", 2),
            ("Often", 3),
            ("Always", 4),
        ],
    },
    {
        "text": "How well do you maintain focus when faced with personal challenges?",
        "options": [
            ("Very well", 0),
            ("Fairly well", 1),
            ("Somewhat", 2),
            ("Poorly", 3),
            ("Very poorly", 4),
        ],
    },
    {
        "text": "How often do you feel isolated or disconnected from others?",
        "options": [
            ("Never", 0),
            ("Rarely", 1),
            ("Sometimes", 2),
            ("Often", 3),
            ("Always", 4),
        ],
    },
    {
        "text": "How frequently do you engage in activities that bring you joy?",
        "options": [
            ("Daily", 0),
            ("Several times a week", 1),
            ("Once a week", 2),
            ("Rarely", 3),
            ("Never", 4),
        ],
    },
    {
        "text": "How often do you feel overwhelmed by your emotions?",
        "options": [
            ("Never", 0),
            ("Rarely", 1),
            ("Sometimes", 2),
            ("Often", 3),
            ("Always", 4),
        ],
    },
    {
        "text": "How confident are you in your ability to handle life's challenges?",
        "options": [
            ("Very confident", 0),
            ("Fairly confident", 1),
            ("Somewhat confident", 2),
            ("Not very confident", 3),
            ("Not confident at all", 4),
        ],
    },
    {
        "text": "How often do you feel a sense of gratitude in your daily life?",
        "options": [
            ("Always", 0),
            ("Often", 1),
            ("Sometimes", 2),
            ("Rarely", 3),
            ("Never", 4),
        ],
    },
    {
        "text": "How often do you experience sudden changes in mood without a clear reason?",
        "options": [
            ("Never", 0),
            ("Rarely", 1),
            ("Sometimes", 2),
            ("Often", 3),
            ("Always", 4),
        ],
    },
    {
        "text": "How well do you cope when your personal plans or routines are disrupted?",
        "options": [
            ("Very well", 0),
            ("Fairly well", 1),
            ("Somewhat", 2),
            ("Poorly", 3),
            ("Very poorly", 4),
        ],
    },
    {
        "text": "How often do you feel that life is meaningful and worth living?",
        "options": [
            ("Always", 0),
            ("Often", 1),
            ("Sometimes", 2),
            ("Rarely", 3),
            ("Never", 4),
        ],
    },
    {
        "text": "How frequently do you feel anxious about future events beyond your control?",
        "options": [
            ("Never", 0),
            ("Rarely", 1),
            ("Sometimes", 2),
            ("Often", 3),
            ("Always", 4),
        ],
    },
    {
        "text": "How well do you maintain healthy relationships with people around you?",
        "options": [
            ("Very well", 0),
            ("Fairly well", 1),
            ("Somewhat", 2),
            ("With difficulty", 3),
            ("Poorly", 4),
        ],
    },
    {
        "text": "How often do you feel that your self-worth depends entirely on your achievements?",
        "options": [
            ("Never", 0),
            ("Rarely", 1),
            ("Sometimes", 2),
            ("Often", 3),
            ("Always", 4),
        ],
    },
    {
        "text": "How often do you practice self-care (e.g., sleep, nutrition, exercise)?",
        "options": [
            ("Every day", 0),
            ("Most days", 1),
            ("Occasionally", 2),
            ("Rarely", 3),
            ("Never", 4),
        ],
    },
    {
        "text": "How often do you feel that negative thoughts dominate your mind?",
        "options": [
            ("Never", 0),
            ("Rarely", 1),
            ("Sometimes", 2),
            ("Often", 3),
            ("Always", 4),
        ],
    },
]

# Psychological state outcomes: tuple of (min_score, max_score, label, description)
OUTCOMES: tuple = (
    (0, 15, "Excellent Well-being",
     "Your emotional resilience is outstanding. You demonstrate strong psychological health with no indicators of distress."),
    (16, 30, "Good Well-being",
     "You have a generally positive emotional state. Minor stressors may occur but you handle them well."),
    (31, 45, "Moderate Well-being",
     "You show some signs of emotional strain. Consider incorporating more self-care and relaxation into your routine."),
    (46, 55, "Mild Psychological Strain",
     "There are noticeable signs of emotional difficulty. Speaking with a trusted friend or counsellor may be beneficial."),
    (56, 65, "Moderate Psychological Strain",
     "Your results suggest meaningful emotional distress. It is advisable to seek psychological support or guidance."),
    (66, 75, "High Psychological Distress",
     "You are experiencing significant emotional difficulties. Professional psychological support is strongly recommended."),
    (76, 80, "Severe Psychological Distress",
     "Your results indicate a serious level of distress. Please seek immediate support from a mental health professional."),
)

# Valid file formats: frozenset (immutable)
VALID_FILE_FORMATS: frozenset = frozenset({"txt", "csv", "json"})

# ─────────────────────────────────────────────
# UTILITY FUNCTIONS
# ─────────────────────────────────────────────

def load_questions_from_file(filepath: str) -> list:
    """Load questions from an external JSON file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"[INFO] Questions loaded from '{filepath}'.\n")
        return data
    except FileNotFoundError:
        print(f"[INFO] '{filepath}' not found. Using hardcoded questions.\n")
        return HARDCODED_QUESTIONS
    except json.JSONDecodeError:
        print(f"[WARNING] Could not parse '{filepath}'. Using hardcoded questions.\n")
        return HARDCODED_QUESTIONS


def save_questions_to_file(questions: list, filepath: str) -> None:
    """Save questions list to a JSON file for external loading."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)


def validate_name(name: str) -> bool:
    """
    Validate that the name contains only letters, hyphens, apostrophes, and spaces.
    Covers names like O'Connor, Smith-Jones, Mary Ann.
    """
    pattern = r"^[a-zA-Z][a-zA-Z '\-]*[a-zA-Z]$|^[a-zA-Z]$"
    return bool(re.match(pattern, name))


def validate_dob(dob_str: str) -> bool:
    """Validate date of birth in DD/MM/YYYY format."""
    try:
        dob = datetime.strptime(dob_str, "%d/%m/%Y")
        today = datetime.today()
        age: int = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return 5 <= age <= 120  # plausible age range
    except ValueError:
        return False


def validate_student_id(sid: str) -> bool:
    """Validate that student ID contains only digits."""
    return sid.isdigit() and len(sid) >= 4


def get_psychological_state(total_score: int) -> dict:
    """Return the psychological state label and description for a given score."""
    for (low, high, label, description) in OUTCOMES:
        if low <= total_score <= high:
            return {"label": label, "description": description}
    return {"label": "Unknown", "description": "Score out of expected range."}


# ─────────────────────────────────────────────
# INPUT COLLECTION FUNCTIONS
# ─────────────────────────────────────────────

def get_validated_input(prompt: str, validator, error_msg: str) -> str:
    """
    Generic validated input using a while loop.
    Keeps asking until the validator returns True.
    """
    while True:  # while loop for input validation
        value: str = input(prompt).strip()
        if validator(value):
            return value
        print(f"  [ERROR] {error_msg}\n")


def collect_user_details() -> dict:
    """Collect and validate user personal details."""
    print("\n" + "=" * 60)
    print("  PERSONAL DETAILS")
    print("=" * 60)

    # Use for loop for surname + given name validation (2 fields)
    fields: list = [
        ("Surname", "Enter your surname: "),
        ("Given name", "Enter your given name: "),
    ]
    name_data: dict = {}

    for field_name, field_prompt in fields:  # for loop for input validation
        name_data[field_name] = get_validated_input(
            field_prompt,
            validate_name,
            f"{field_name} may only contain letters, hyphens (-), apostrophes ('), and spaces."
            " No digits or other punctuation allowed. (e.g. O'Connor, Smith-Jones, Mary Ann)"
        )

    dob: str = get_validated_input(
        "Date of birth (DD/MM/YYYY): ",
        validate_dob,
        "Please enter a valid date in DD/MM/YYYY format (e.g. 15/03/2000)."
    )

    student_id: str = get_validated_input(
        "Student ID (digits only): ",
        validate_student_id,
        "Student ID must contain only digits and be at least 4 characters long."
    )

    return {
        "surname": name_data["Surname"],
        "given_name": name_data["Given name"],
        "dob": dob,
        "student_id": student_id,
    }


# ─────────────────────────────────────────────
# SURVEY CONDUCT FUNCTION
# ─────────────────────────────────────────────

def conduct_survey(questions: list) -> tuple:
    """
    Run the survey questionnaire.
    Returns (total_score: int, answers: list of dicts).
    """
    print("\n" + "=" * 60)
    print("  EMOTIONAL RESILIENCE & MENTAL WELL-BEING SURVEY")
    print("=" * 60)
    print("Please answer each question honestly.")
    print("Enter the number corresponding to your answer.\n")

    total_score: int = 0
    answers: list = []
    valid_choices: set = set()  # used to track valid options per question

    for i, question in enumerate(questions, start=1):  # for loop iterating questions
        print(f"Q{i}. {question['text']}")
        options = question["options"]

        # Build valid choices set for this question
        valid_choices = set(range(1, len(options) + 1))

        for j, (option_text, _score) in enumerate(options, start=1):
            print(f"   {j}. {option_text}")

        # Validate answer input with while loop
        while True:
            raw: str = input("   Your answer (enter number): ").strip()
            if raw.isdigit() and int(raw) in valid_choices:
                choice: int = int(raw)
                break
            print(f"   [ERROR] Please enter a number between 1 and {len(options)}.")

        chosen_text, chosen_score = options[choice - 1]
        total_score += chosen_score
        answers.append({
            "question": question["text"],
            "answer": chosen_text,
            "score": chosen_score,
        })
        print(f"   ✔ Recorded: {chosen_text} (score: {chosen_score})\n")

    return total_score, answers


# ─────────────────────────────────────────────
# RESULT DISPLAY
# ─────────────────────────────────────────────

def display_result(user_details: dict, total_score: int) -> dict:
    """Display the survey result and return the result dictionary."""
    state: dict = get_psychological_state(total_score)
    max_possible: int = len(HARDCODED_QUESTIONS) * 4  # float used in percentage
    percentage: float = round((total_score / max_possible) * 100, 1)

    print("\n" + "=" * 60)
    print("  SURVEY RESULT")
    print("=" * 60)
    print(f"  Name       : {user_details['given_name']} {user_details['surname']}")
    print(f"  Student ID : {user_details['student_id']}")
    print(f"  Date       : {datetime.today().strftime('%d/%m/%Y')}")
    print(f"  Total Score: {total_score} / {max_possible} ({percentage}%)")
    print(f"\n  Psychological State: {state['label']}")
    print(f"\n  {state['description']}")
    print("=" * 60)

    return {
        "name": f"{user_details['given_name']} {user_details['surname']}",
        "student_id": user_details["student_id"],
        "dob": user_details["dob"],
        "date_taken": datetime.today().strftime("%d/%m/%Y %H:%M"),
        "total_score": total_score,
        "max_score": max_possible,
        "percentage": percentage,
        "psychological_state": state["label"],
        "description": state["description"],
    }


# ─────────────────────────────────────────────
# SAVE FUNCTIONS
# ─────────────────────────────────────────────

def save_result(result: dict, answers: list, fmt: str) -> None:
    """Save survey results to file in the chosen format."""
    filename_base: str = f"result_{result['student_id']}_{datetime.today().strftime('%Y%m%d_%H%M%S')}"

    if fmt == "json":
        filename: str = filename_base + ".json"
        full_data: dict = {**result, "answers": answers}
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(full_data, f, indent=2, ensure_ascii=False)

    elif fmt == "csv":
        filename = filename_base + ".csv"
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Field", "Value"])
            for key, value in result.items():
                writer.writerow([key, value])
            writer.writerow([])
            writer.writerow(["#", "Question", "Answer", "Score"])
            for idx, ans in enumerate(answers, start=1):
                writer.writerow([idx, ans["question"], ans["answer"], ans["score"]])

    else:  # txt
        filename = filename_base + ".txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write("EMOTIONAL RESILIENCE SURVEY — RESULTS\n")
            f.write("=" * 50 + "\n")
            for key, value in result.items():
                f.write(f"{key.replace('_', ' ').title()}: {value}\n")
            f.write("\n--- ANSWERS ---\n")
            for idx, ans in enumerate(answers, start=1):
                f.write(f"{idx}. {ans['question']}\n")
                f.write(f"   Answer : {ans['answer']} (score: {ans['score']})\n")

    print(f"\n  [INFO] Results saved to '{filename}'.")


def save_menu(result: dict, answers: list) -> None:
    """Ask user if they want to save, and in which format."""
    print("\nWould you like to save your results?")
    choice: str = input("  Enter 'yes' or 'no': ").strip().lower()

    if choice not in {"yes", "y"}:
        print("  Results not saved.")
        return

    print(f"\nChoose file format to save ({', '.join(sorted(VALID_FILE_FORMATS))}):")
    while True:
        fmt: str = input("  Format: ").strip().lower()
        if fmt in VALID_FILE_FORMATS:
            break
        print(f"  [ERROR] Please choose one of: {', '.join(sorted(VALID_FILE_FORMATS))}")

    save_result(result, answers, fmt)


# ─────────────────────────────────────────────
# LOAD & DISPLAY EXISTING RESULT
# ─────────────────────────────────────────────

def load_existing_result() -> None:
    """Load and display results from a previously saved file."""
    print("\n" + "=" * 60)
    print("  LOAD EXISTING RESULTS")
    print("=" * 60)
    filepath: str = input("Enter the full filename (e.g. result_123456_20250101_1200.json): ").strip()

    if not os.path.exists(filepath):
        print(f"  [ERROR] File '{filepath}' not found.")
        return

    extension: str = filepath.rsplit(".", 1)[-1].lower()

    if extension == "json":
        with open(filepath, "r", encoding="utf-8") as f:
            data: dict = json.load(f)
        print("\n  --- Loaded Results ---")
        for key, value in data.items():
            if key != "answers":
                print(f"  {key.replace('_', ' ').title()}: {value}")
        if "answers" in data:
            print(f"\n  Total questions answered: {len(data['answers'])}")

    elif extension == "csv":
        with open(filepath, "r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            print("\n  --- Loaded Results ---")
            is_bool_header: bool = False
            for row in reader:
                if len(row) == 2:
                    print(f"  {row[0]}: {row[1]}")
                elif len(row) == 4 and row[0] == "#":
                    is_bool_header = True
                elif is_bool_header and len(row) == 4:
                    print(f"  Q{row[0]}: {row[1]} → {row[2]} (score: {row[3]})")

    elif extension == "txt":
        with open(filepath, "r", encoding="utf-8") as f:
            print("\n" + f.read())

    else:
        print("  [ERROR] Unsupported file format. Supported: json, csv, txt")


# ─────────────────────────────────────────────
# MAIN PROGRAM
# ─────────────────────────────────────────────

def main() -> None:
    """Main program entry point."""
    print("\n" + "=" * 60)
    print("  EMOTIONAL RESILIENCE & MENTAL WELL-BEING SURVEY")
    print("  Westminster International University in Tashkent")
    print("=" * 60)

    # Save questions to external file on first run (both methods available)
    if not os.path.exists(QUESTIONS_FILE):
        save_questions_to_file(HARDCODED_QUESTIONS, QUESTIONS_FILE)
        print(f"[INFO] Questions file created: '{QUESTIONS_FILE}'")

    # Startup menu
    print("\nWhat would you like to do?")
    print("  1. Start a new questionnaire")
    print("  2. Load and view existing results from a file")

    while True:  # while loop for menu validation
        choice: str = input("\nEnter 1 or 2: ").strip()
        if choice in {"1", "2"}:
            break
        print("  [ERROR] Please enter 1 or 2.")

    if choice == "2":
        load_existing_result()
        return

    # ── NEW QUESTIONNAIRE FLOW ──────────────────────
    # Load questions (from file if available, otherwise hardcoded)
    questions: list = load_questions_from_file(QUESTIONS_FILE)

    # Collect and validate user details
    user_details: dict = collect_user_details()

    # Conduct survey
    total_score: int
    answers: list
    total_score, answers = conduct_survey(questions)

    # Display result
    result: dict = display_result(user_details, total_score)

    # Offer save
    save_menu(result, answers)

    print("\nThank you for completing the survey. Goodbye!\n")


if __name__ == "__main__":
    main()
