"""
Quiet Study Zone Preference and Concentration Depth Survey
Module  : Fundamentals of Programming, 4BUIS008C (Level 4)
Tool    : Streamlit Web Application
Topic   : Quiet Study Zone Preference and Concentration Depth

Run locally : streamlit run survey_app.py
Deploy      : Upload to Hugging Face Spaces (SDK = Streamlit)
              or Streamlit Community Cloud (share.streamlit.io)
"""

import json
import csv
import re
import io
import os
from datetime import datetime

import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
# ALL REQUIRED PYTHON DATA TYPES ARE USED THROUGHOUT THIS FILE:
#   int, str, float, list, tuple, range, bool, dict, set, frozenset
# ─────────────────────────────────────────────────────────────────────────────

# ── QUESTIONS ─────────────────────────────────────────────────────────────────
# Each question: dict with "text" (str) and "options" (list of [label, score])
# Loaded from questions.json if present, otherwise uses HARDCODED_QUESTIONS.

QUESTIONS_FILE: str = "questions.json"

HARDCODED_QUESTIONS: list = [
    {
        "text": "How important is a completely quiet environment for you to study effectively?",
        "options": [
            ["Absolutely essential — I cannot study without silence", 0],
            ["Very important — I strongly prefer it", 1],
            ["Somewhat important — I can manage with low noise", 2],
            ["Not very important — background noise rarely bothers me", 3],
            ["Not important at all — noise has no effect on me", 4],
        ],
    },
    {
        "text": "How deeply can you concentrate when studying in a completely silent room?",
        "options": [
            ["Extremely deeply — I lose track of time entirely", 0],
            ["Very deeply — I stay focused for long periods", 1],
            ["Moderately — I focus well but take regular breaks", 2],
            ["Lightly — my mind still wanders despite the silence", 3],
            ["I struggle to concentrate even in total silence", 4],
        ],
    },
    {
        "text": "How quickly does background noise (e.g. conversations, music) break your concentration?",
        "options": [
            ["I never notice it once I am focused", 0],
            ["It takes a significant disturbance to break my focus", 1],
            ["Moderate noise gradually pulls my attention away", 2],
            ["Even low noise interrupts me within minutes", 3],
            ["Any noise immediately destroys my concentration", 4],
        ],
    },
    {
        "text": "How long can you maintain deep focus before losing concentration?",
        "options": [
            ["More than 90 minutes without any break", 0],
            ["60 to 90 minutes before needing a short pause", 1],
            ["30 to 60 minutes before my attention drifts", 2],
            ["15 to 30 minutes before I lose focus", 3],
            ["Less than 15 minutes before I become distracted", 4],
        ],
    },
    {
        "text": "How often do you actively seek out a quiet zone (library, empty room) to study seriously?",
        "options": [
            ["Always — it is part of my standard study routine", 0],
            ["Often — I do so for most important study sessions", 1],
            ["Sometimes — only when the task is particularly demanding", 2],
            ["Rarely — I usually study wherever I happen to be", 3],
            ["Never — I do not seek quiet zones at all", 4],
        ],
    },
    {
        "text": "How does studying in a noisy environment affect the quality of your work?",
        "options": [
            ["It has no effect — my output is the same regardless", 0],
            ["Slight effect — minor drop in quality under noise", 1],
            ["Noticeable effect — I make more errors and work slower", 2],
            ["Significant effect — the quality of my work drops sharply", 3],
            ["Severe effect — I am practically unable to produce good work", 4],
        ],
    },
    {
        "text": "How comfortable are you studying in shared spaces such as open libraries or common rooms?",
        "options": [
            ["Very comfortable — shared spaces work perfectly for me", 0],
            ["Fairly comfortable — minor distractions are manageable", 1],
            ["Somewhat uncomfortable — I tolerate it but prefer otherwise", 2],
            ["Quite uncomfortable — shared spaces drain my concentration", 3],
            ["Very uncomfortable — I avoid them entirely for study", 4],
        ],
    },
    {
        "text": "How often do you use tools such as noise-cancelling headphones or earplugs while studying?",
        "options": [
            ["Never — my environment is naturally quiet enough", 0],
            ["Occasionally — only in unusually noisy situations", 1],
            ["Sometimes — for medium-difficulty tasks", 2],
            ["Often — I rely on them for most study sessions", 3],
            ["Always — I cannot study at all without them", 4],
        ],
    },
    {
        "text": "How well do you retain information studied in a quiet environment compared to a noisy one?",
        "options": [
            ["Equally well — the environment makes no difference", 0],
            ["Slightly better in quiet — a small but noticeable difference", 1],
            ["Moderately better — quiet clearly improves my retention", 2],
            ["Much better — retention is significantly higher in silence", 3],
            ["Dramatically better — I barely retain anything in noisy settings", 4],
        ],
    },
    {
        "text": "How often do unexpected sounds (a door slamming, a phone ringing) cause you to lose your train of thought?",
        "options": [
            ["Never — I remain focused regardless of sudden sounds", 0],
            ["Rarely — only very loud or startling sounds affect me", 1],
            ["Sometimes — moderate unexpected sounds break my focus", 2],
            ["Often — even small sounds regularly disrupt my thinking", 3],
            ["Always — any unexpected sound resets my concentration entirely", 4],
        ],
    },
    {
        "text": "How would you describe your ability to enter a state of deep focus (flow) in your usual study setting?",
        "options": [
            ["Very easy — I enter a flow state quickly and regularly", 0],
            ["Fairly easy — I usually get there within a few minutes", 1],
            ["Moderate — it takes effort and the right conditions", 2],
            ["Difficult — I rarely reach a genuine state of deep focus", 3],
            ["Very difficult — I have almost never experienced deep focus", 4],
        ],
    },
    {
        "text": "How much does low-level ambient sound (e.g. air conditioning, distant traffic) affect your study?",
        "options": [
            ["Not at all — I find it neutral or even helpful", 0],
            ["Very slightly — I notice it but it does not bother me", 1],
            ["Somewhat — it is mildly distracting over time", 2],
            ["Considerably — it noticeably reduces my concentration", 3],
            ["Greatly — even soft ambient sound makes studying very hard", 4],
        ],
    },
    {
        "text": "How often do you feel mentally exhausted after studying in a noisy environment?",
        "options": [
            ["Never — environmental noise does not tire me", 0],
            ["Rarely — only after very long sessions in noisy places", 1],
            ["Sometimes — moderate fatigue after a few hours", 2],
            ["Often — I regularly feel drained after studying in noise", 3],
            ["Always — even short noisy sessions leave me mentally depleted", 4],
        ],
    },
    {
        "text": "How satisfied are you with the quiet study options currently available to you?",
        "options": [
            ["Very satisfied — I always have access to an ideal quiet space", 0],
            ["Fairly satisfied — adequate quiet spaces are usually available", 1],
            ["Neutral — access is inconsistent but I manage", 2],
            ["Fairly dissatisfied — quiet spaces are difficult to find", 3],
            ["Very dissatisfied — I almost never have access to a quiet space", 4],
        ],
    },
    {
        "text": "How effectively can you switch between topics while remaining in deep concentration?",
        "options": [
            ["Very effectively — I transition smoothly without losing focus", 0],
            ["Fairly effectively — brief adjustment time but focus is maintained", 1],
            ["Moderately — switching topics disrupts my concentration noticeably", 2],
            ["With difficulty — task-switching significantly breaks my focus", 3],
            ["Very poorly — any switch essentially ends my concentration session", 4],
        ],
    },
    {
        "text": "How often do you plan your study sessions around the availability of a quiet environment?",
        "options": [
            ["Never — I study whenever and wherever it is convenient", 0],
            ["Rarely — only for major deadlines or exams", 1],
            ["Sometimes — I consider it for important tasks", 2],
            ["Often — quiet availability is a key factor in my planning", 3],
            ["Always — I will not begin a study session without securing a quiet space", 4],
        ],
    },
    {
        "text": "How does studying with background music (without lyrics) affect your concentration?",
        "options": [
            ["It helps me focus — I concentrate better with instrumental music", 0],
            ["It is neutral — no noticeable positive or negative effect", 1],
            ["It mildly distracts me — I prefer silence over music", 2],
            ["It noticeably distracts me — music reduces my concentration", 3],
            ["It severely distracts me — any music makes studying very hard", 4],
        ],
    },
    {
        "text": "How well do you perform on complex tasks (problem-solving, essay writing) in your usual study environment?",
        "options": [
            ["Excellently — I consistently produce high-quality work", 0],
            ["Well — my performance is generally strong with minor lapses", 1],
            ["Adequately — I complete tasks but not always to my best ability", 2],
            ["Poorly — I frequently struggle to think clearly during tasks", 3],
            ["Very poorly — my cognitive performance is consistently low", 4],
        ],
    },
    {
        "text": "How aware are you of other people's movements or activities around you while studying?",
        "options": [
            ["Not aware at all — I am fully absorbed in my work", 0],
            ["Slightly aware — I notice them but am not distracted", 1],
            ["Moderately aware — they occasionally pull my attention", 2],
            ["Very aware — I frequently lose focus due to others nearby", 3],
            ["Extremely aware — I cannot ignore what others around me are doing", 4],
        ],
    },
    {
        "text": "How confident are you that your current study environment supports your best academic performance?",
        "options": [
            ["Very confident — my environment is ideal for my needs", 0],
            ["Fairly confident — it meets most of my requirements", 1],
            ["Uncertain — it is acceptable but far from ideal", 2],
            ["Not very confident — my environment often works against me", 3],
            ["Not confident at all — my environment significantly hinders my performance", 4],
        ],
    },
]

# ── OUTCOMES ──────────────────────────────────────────────────────────────────
# tuple of (min_score: int, max_score: int, label: str, description: str, emoji: str, color: str)

OUTCOMES: tuple = (
    (0, 15,
     "Ideal Match — Deep Concentration",
     "You have an exceptionally strong preference for quiet and achieve deep, sustained concentration. "
     "Your study habits and environment are well-aligned for peak academic performance.",
     "🟢", "#1a7a4a"),
    (16, 30,
     "Strong Preference — High Focus Ability",
     "Quiet zones significantly boost your performance. You focus deeply when conditions are right. "
     "Seek out silent spaces and protect your study time to maintain this strong output.",
     "🟩", "#2d9e5f"),
    (31, 45,
     "Moderate Preference — Good Concentration",
     "You benefit noticeably from quiet environments but can manage moderate noise levels. "
     "Consider using noise-cancelling headphones and scheduling study in quieter periods.",
     "🟡", "#b8860b"),
    (46, 55,
     "Low Sensitivity — Partial Quiet Preference",
     "Noise affects you but you adapt reasonably well. Structured quiet time will improve "
     "your retention and reduce mental fatigue during demanding study sessions.",
     "🟠", "#cc6600"),
    (56, 68,
     "Adaptive Studier — Flexible Concentration",
     "You are largely adaptable to different environments. While quiet is not critical for you, "
     "experimenting with silent study sessions may reveal untapped concentration potential.",
     "🔵", "#1a5a99"),
    (69, 80,
     "Environment-Independent — Highly Flexible",
     "Your concentration is largely unaffected by noise levels. You perform consistently "
     "across environments. Focus on task structure and time management to further optimise performance.",
     "⚪", "#555555"),
)

# Valid save formats: frozenset (immutable set)
VALID_FORMATS: frozenset = frozenset({"txt", "csv", "json"})

# ── VALIDATION FUNCTIONS ───────────────────────────────────────────────────────

def validate_name(name: str) -> bool:
    """Allow letters, hyphens, apostrophes, spaces. Covers O'Connor, Smith-Jones, Mary Ann."""
    pattern: str = r"^[a-zA-Z][a-zA-Z '\-]*[a-zA-Z]$|^[a-zA-Z]$"
    return bool(re.match(pattern, name.strip()))


def validate_dob(dob_str: str) -> bool:
    """Validate DD/MM/YYYY format and plausible age (5–120 years)."""
    try:
        dob = datetime.strptime(dob_str.strip(), "%d/%m/%Y")
        today = datetime.today()
        age: int = today.year - dob.year - (
            (today.month, today.day) < (dob.month, dob.day)
        )
        return 5 <= age <= 120
    except ValueError:
        return False


def validate_student_id(sid: str) -> bool:
    """Student ID must be digits only, minimum 4 characters."""
    return sid.strip().isdigit() and len(sid.strip()) >= 4


# ── SCORING FUNCTION ───────────────────────────────────────────────────────────

def get_outcome(total_score: int) -> dict:
    """Return outcome dict for the given total score."""
    for (low, high, label, desc, emoji, color) in OUTCOMES:
        if low <= total_score <= high:
            return {"label": label, "description": desc, "emoji": emoji, "color": color}
    return {"label": "Unknown", "description": "Score out of range.", "emoji": "❓", "color": "#888"}


# ── FILE GENERATION FUNCTIONS ──────────────────────────────────────────────────

def build_json_bytes(result: dict, answers: list) -> bytes:
    """Return JSON file as bytes for download."""
    full: dict = {**result, "answers": answers}
    return json.dumps(full, indent=2, ensure_ascii=False).encode("utf-8")


def build_csv_bytes(result: dict, answers: list) -> bytes:
    """Return CSV file as bytes for download."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Field", "Value"])
    for key, value in result.items():
        writer.writerow([key, value])
    writer.writerow([])
    writer.writerow(["#", "Question", "Answer", "Score"])
    for idx, ans in enumerate(answers, start=1):
        writer.writerow([idx, ans["question"], ans["answer"], ans["score"]])
    return output.getvalue().encode("utf-8")


def build_txt_bytes(result: dict, answers: list) -> bytes:
    """Return TXT file as bytes for download."""
    lines: list = [
        "QUIET STUDY ZONE PREFERENCE & CONCENTRATION DEPTH SURVEY",
        "Westminster International University in Tashkent",
        "=" * 60,
    ]
    for key, value in result.items():
        lines.append(f"{key.replace('_', ' ').title()}: {value}")
    lines.append("")
    lines.append("─" * 60)
    lines.append("DETAILED ANSWERS")
    lines.append("─" * 60)
    for idx, ans in enumerate(answers, start=1):
        lines.append(f"{idx}. {ans['question']}")
        lines.append(f"   → {ans['answer']}  (score: {ans['score']})")
        lines.append("")
    return "\n".join(lines).encode("utf-8")


def load_questions() -> list:
    """Load questions from external JSON file if it exists, else use hardcoded list."""
    if os.path.exists(QUESTIONS_FILE):
        try:
            with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
                data: list = json.load(f)
            return data
        except (json.JSONDecodeError, KeyError):
            pass
    return HARDCODED_QUESTIONS


# ── PAGE CONFIG ────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Quiet Study Zone Survey",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── CUSTOM CSS ─────────────────────────────────────────────────────────────────

st.markdown("""
<style>
/* ── Global ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── Header banner ── */
.header-banner {
    background: linear-gradient(135deg, #0d2137 0%, #1a4a7a 60%, #0d6efd 100%);
    border-radius: 16px;
    padding: 2.2rem 2rem 1.8rem;
    margin-bottom: 1.8rem;
    text-align: center;
    box-shadow: 0 8px 32px rgba(13,33,55,0.25);
}
.header-banner h1 {
    color: #ffffff;
    font-size: 1.75rem;
    font-weight: 700;
    margin: 0 0 0.4rem 0;
    letter-spacing: -0.02em;
}
.header-banner p {
    color: #a8c8f0;
    font-size: 0.95rem;
    margin: 0;
}

/* ── Step badges ── */
.step-badge {
    display: inline-block;
    background: #e8f0fe;
    color: #1a4a7a;
    font-size: 0.78rem;
    font-weight: 600;
    padding: 3px 12px;
    border-radius: 20px;
    margin-bottom: 0.8rem;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

/* ── Section cards ── */
.section-card {
    background: #f8faff;
    border: 1px solid #dde8f8;
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1.2rem;
}

/* ── Question card ── */
.q-card {
    background: #ffffff;
    border: 1px solid #e2eaf8;
    border-left: 4px solid #0d6efd;
    border-radius: 10px;
    padding: 1.2rem 1.4rem 0.6rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 2px 8px rgba(13,110,253,0.06);
}
.q-number {
    font-size: 0.75rem;
    font-weight: 600;
    color: #0d6efd;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 0.3rem;
}
.q-text {
    font-size: 1.0rem;
    font-weight: 500;
    color: #1a2a3a;
    line-height: 1.5;
    margin-bottom: 0.8rem;
}

/* ── Progress bar override ── */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #0d6efd, #4ea8ff);
    border-radius: 10px;
}

/* ── Result card ── */
.result-card {
    border-radius: 14px;
    padding: 1.8rem 2rem;
    margin: 1.2rem 0;
    text-align: center;
}
.result-score {
    font-size: 3.5rem;
    font-weight: 800;
    line-height: 1;
}
.result-label {
    font-size: 1.2rem;
    font-weight: 700;
    margin-top: 0.5rem;
}
.result-desc {
    font-size: 0.95rem;
    margin-top: 0.8rem;
    line-height: 1.6;
    opacity: 0.9;
}

/* ── Metric boxes ── */
.metric-row {
    display: flex;
    gap: 12px;
    margin: 1rem 0;
}
.metric-box {
    flex: 1;
    background: #f0f5ff;
    border: 1px solid #c8d8f8;
    border-radius: 10px;
    padding: 0.9rem;
    text-align: center;
}
.metric-box .m-label {
    font-size: 0.72rem;
    color: #556;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.metric-box .m-value {
    font-size: 1.4rem;
    font-weight: 700;
    color: #0d2137;
}

/* ── Buttons ── */
div.stButton > button {
    background: linear-gradient(135deg, #0d6efd, #0056d2);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    padding: 0.55rem 1.4rem;
    transition: opacity 0.15s;
}
div.stButton > button:hover { opacity: 0.88; }

/* ── Sidebar nav ── */
.nav-item {
    padding: 6px 0;
    font-size: 0.9rem;
    color: #334;
}
.nav-item.active { color: #0d6efd; font-weight: 600; }

/* ── Error / info boxes ── */
.err-box {
    background: #fff0f0;
    border: 1px solid #ffcccc;
    border-radius: 8px;
    padding: 0.6rem 1rem;
    color: #cc2222;
    font-size: 0.9rem;
    margin-top: 0.3rem;
}
.info-box {
    background: #f0f7ff;
    border: 1px solid #b8d4f8;
    border-radius: 8px;
    padding: 0.7rem 1rem;
    color: #1a4a7a;
    font-size: 0.9rem;
}

/* ── Outcomes scale ── */
.scale-row {
    display: flex;
    gap: 4px;
    margin: 0.5rem 0 1rem;
}
.scale-seg {
    flex: 1;
    height: 8px;
    border-radius: 4px;
}

/* Hide Streamlit branding ── */
#MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE INITIALISATION ───────────────────────────────────────────────

def _init_state() -> None:
    """Initialise all session state variables."""
    defaults: dict = {
        "page": "home",          # home | details | survey | result | load
        "surname": "",
        "given_name": "",
        "dob": "",
        "student_id": "",
        "answers": [],           # list of dicts: {question, answer, score}
        "current_q": 0,          # int index into questions list
        "total_score": 0,        # int
        "result": {},            # dict with summary fields
        "questions": [],         # list loaded once
        "errors": {},            # dict field -> error message
        "saved_format": "",      # str last saved format
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

_init_state()

# Load questions once into session state
if not st.session_state["questions"]:
    st.session_state["questions"] = load_questions()

QUESTIONS: list = st.session_state["questions"]
MAX_SCORE: int = len(QUESTIONS) * 4

# ── HEADER ─────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="header-banner">
  <h1>📚 Quiet Study Zone Survey</h1>
  <p>Preference &amp; Concentration Depth Assessment &nbsp;·&nbsp;
     Westminster International University in Tashkent</p>
</div>
""", unsafe_allow_html=True)

# ── PAGE: HOME ──────────────────────────────────────────────────────────────────

if st.session_state["page"] == "home":

    st.markdown("""
    <div class="info-box">
    This survey assesses how strongly you prefer quiet study environments and how deeply you
    concentrate in them. Answer all <b>20 questions</b> honestly — there are no right or wrong answers.
    Each question has <b>5 options</b> scored 0–4. Your total score (0–80) maps to one of
    <b>6 psychological states</b> describing your study environment profile.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### What would you like to do?")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🆕  Start New Survey", use_container_width=True):
            # Reset survey state
            st.session_state["answers"] = []
            st.session_state["current_q"] = 0
            st.session_state["total_score"] = 0
            st.session_state["result"] = {}
            st.session_state["errors"] = {}
            st.session_state["page"] = "details"
            st.rerun()

    with col2:
        if st.button("📂  Load Existing Results", use_container_width=True):
            st.session_state["page"] = "load"
            st.rerun()

    # Outcome scale preview
    st.markdown("---")
    st.markdown("#### Score Outcomes")
    scale_colors: list = ["#1a7a4a", "#2d9e5f", "#b8860b", "#cc6600", "#1a5a99", "#888888"]
    segs: str = "".join(
        f'<div class="scale-seg" style="background:{c};"></div>'
        for c in scale_colors
    )
    st.markdown(f'<div class="scale-row">{segs}</div>', unsafe_allow_html=True)

    outcome_labels: list = [o[2] for o in OUTCOMES]
    outcome_ranges: list = [f"{o[0]}–{o[1]}" for o in OUTCOMES]
    for label, rng, color in zip(outcome_labels, outcome_ranges, scale_colors):
        st.markdown(
            f'<div style="font-size:0.88rem; margin:3px 0;">'
            f'<span style="color:{color}; font-weight:700;">●</span> '
            f'<b>{rng}</b> — {label}</div>',
            unsafe_allow_html=True
        )

# ── PAGE: DETAILS ───────────────────────────────────────────────────────────────

elif st.session_state["page"] == "details":

    st.markdown('<div class="step-badge">Step 1 of 3 — Personal Details</div>', unsafe_allow_html=True)
    st.markdown("### Enter Your Details")
    st.markdown(
        '<div class="info-box">All fields are required and validated before you can proceed.</div>',
        unsafe_allow_html=True
    )
    st.markdown("")

    errors: dict = st.session_state.get("errors", {})

    # ── Input fields ──────────────────────────────────────────────────────────

    # for loop used for surname + given name field validation (coursework requirement)
    name_fields: list = [
        ("surname",    "Surname",    "e.g. Smith, O'Connor, Smith-Jones"),
        ("given_name", "Given Name", "e.g. John, Mary Ann"),
    ]

    for field_key, field_label, placeholder in name_fields:
        val: str = st.text_input(
            field_label,
            value=st.session_state[field_key],
            placeholder=placeholder,
            key=f"input_{field_key}"
        )
        st.session_state[field_key] = val
        if field_key in errors:
            st.markdown(f'<div class="err-box">⚠ {errors[field_key]}</div>', unsafe_allow_html=True)

    dob_val: str = st.text_input(
        "Date of Birth",
        value=st.session_state["dob"],
        placeholder="DD/MM/YYYY",
        key="input_dob"
    )
    st.session_state["dob"] = dob_val
    if "dob" in errors:
        st.markdown(f'<div class="err-box">⚠ {errors["dob"]}</div>', unsafe_allow_html=True)

    sid_val: str = st.text_input(
        "Student ID",
        value=st.session_state["student_id"],
        placeholder="Digits only, e.g. 210012",
        key="input_sid"
    )
    st.session_state["student_id"] = sid_val
    if "student_id" in errors:
        st.markdown(f'<div class="err-box">⚠ {errors["student_id"]}</div>', unsafe_allow_html=True)

    st.markdown("")
    col_back, col_next = st.columns([1, 2])

    with col_back:
        if st.button("← Back", use_container_width=True):
            st.session_state["page"] = "home"
            st.rerun()

    with col_next:
        if st.button("Continue to Survey →", use_container_width=True):

            # ── Validation logic (for loop + while-style via dict comprehension) ──
            new_errors: dict = {}

            # for loop for name field validation
            for fk, fl, _ in name_fields:
                value: str = st.session_state[fk].strip()
                if not value:
                    new_errors[fk] = f"{fl} is required."
                elif not validate_name(value):
                    new_errors[fk] = (
                        f"{fl} may only contain letters, hyphens (-), apostrophes ('), "
                        "and spaces. No digits or other punctuation."
                    )

            dob_input: str = st.session_state["dob"].strip()
            if not dob_input:
                new_errors["dob"] = "Date of birth is required."
            elif not validate_dob(dob_input):
                new_errors["dob"] = "Enter a valid date in DD/MM/YYYY format (age must be 5–120)."

            sid_input: str = st.session_state["student_id"].strip()
            if not sid_input:
                new_errors["student_id"] = "Student ID is required."
            elif not validate_student_id(sid_input):
                new_errors["student_id"] = "Student ID must contain digits only (minimum 4 digits)."

            st.session_state["errors"] = new_errors

            if not new_errors:
                # All valid — move to survey
                st.session_state["answers"] = []
                st.session_state["current_q"] = 0
                st.session_state["total_score"] = 0
                st.session_state["page"] = "survey"
                st.rerun()
            else:
                st.rerun()

# ── PAGE: SURVEY ────────────────────────────────────────────────────────────────

elif st.session_state["page"] == "survey":

    q_idx: int = st.session_state["current_q"]
    total_q: int = len(QUESTIONS)

    # Progress bar
    progress: float = q_idx / total_q
    st.markdown(f'<div class="step-badge">Step 2 of 3 — Survey  ·  Question {q_idx + 1} of {total_q}</div>',
                unsafe_allow_html=True)
    st.progress(progress)

    question: dict = QUESTIONS[q_idx]
    options_raw: list = question["options"]
    option_labels: list = [opt[0] for opt in options_raw]
    option_scores: list = [opt[1] for opt in options_raw]

    # Question card
    st.markdown(
        f'<div class="q-card">'
        f'<div class="q-number">Question {q_idx + 1}</div>'
        f'<div class="q-text">{question["text"]}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    # Radio — uses index as key so it resets for each question
    chosen_label: str = st.radio(
        "Select your answer:",
        options=option_labels,
        key=f"q_{q_idx}",
        label_visibility="collapsed"
    )

    chosen_idx: int = option_labels.index(chosen_label)
    chosen_score: int = option_scores[chosen_idx]  # int

    st.markdown("")
    col_prev, col_next = st.columns([1, 2])

    with col_prev:
        if q_idx > 0:
            if st.button("← Previous", use_container_width=True):
                # Remove last answer, go back
                if st.session_state["answers"]:
                    removed: dict = st.session_state["answers"].pop()
                    st.session_state["total_score"] -= removed["score"]
                st.session_state["current_q"] -= 1
                st.rerun()

    with col_next:
        btn_label: str = "Next Question →" if q_idx < total_q - 1 else "Submit Survey ✓"
        if st.button(btn_label, use_container_width=True):

            # Record this answer
            answer_record: dict = {
                "question": question["text"],
                "answer":   chosen_label,
                "score":    chosen_score,
            }

            answers_list: list = st.session_state["answers"]

            # Use range() to determine if we're updating or appending (range is required type)
            existing_indices: list = list(range(len(answers_list)))
            if q_idx in existing_indices:
                # Update: adjust score delta
                old_score: int = answers_list[q_idx]["score"]
                st.session_state["total_score"] += (chosen_score - old_score)
                answers_list[q_idx] = answer_record
            else:
                # New answer
                st.session_state["total_score"] += chosen_score
                answers_list.append(answer_record)

            if q_idx < total_q - 1:
                st.session_state["current_q"] += 1
                st.rerun()
            else:
                # Build result summary dict
                score: int = st.session_state["total_score"]
                pct: float = round((score / MAX_SCORE) * 100, 1)
                outcome: dict = get_outcome(score)
                is_complete: bool = len(answers_list) == total_q  # bool type used

                st.session_state["result"] = {
                    "name":               f"{st.session_state['given_name']} {st.session_state['surname']}",
                    "student_id":         st.session_state["student_id"],
                    "dob":                st.session_state["dob"],
                    "date_taken":         datetime.today().strftime("%d/%m/%Y %H:%M"),
                    "total_score":        score,
                    "max_score":          MAX_SCORE,
                    "percentage":         pct,
                    "survey_complete":    is_complete,
                    "psychological_state": outcome["label"],
                    "description":        outcome["description"],
                }
                st.session_state["page"] = "result"
                st.rerun()

# ── PAGE: RESULT ────────────────────────────────────────────────────────────────

elif st.session_state["page"] == "result":

    result: dict     = st.session_state["result"]
    answers: list    = st.session_state["answers"]
    score: int       = result["total_score"]
    pct: float       = result["percentage"]
    outcome: dict    = get_outcome(score)
    color: str       = outcome["color"]

    st.markdown('<div class="step-badge">Step 3 of 3 — Your Results</div>', unsafe_allow_html=True)

    # ── Result card ────────────────────────────────────────────────────────────
    st.markdown(
        f'<div class="result-card" style="background:{color}18; border: 2px solid {color}44;">'
        f'<div class="result-score" style="color:{color};">'
        f'{outcome["emoji"]} {score}<span style="font-size:1.5rem;color:#778;"> / {MAX_SCORE}</span>'
        f'</div>'
        f'<div class="result-label" style="color:{color};">{outcome["label"]}</div>'
        f'<div class="result-desc" style="color:#334;">{outcome["description"]}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    # ── Metrics ────────────────────────────────────────────────────────────────
    st.markdown(
        f'<div class="metric-row">'
        f'<div class="metric-box"><div class="m-label">Score</div>'
        f'<div class="m-value">{score} / {MAX_SCORE}</div></div>'
        f'<div class="metric-box"><div class="m-label">Percentage</div>'
        f'<div class="m-value">{pct}%</div></div>'
        f'<div class="metric-box"><div class="m-label">Questions</div>'
        f'<div class="m-value">{len(answers)} / {len(QUESTIONS)}</div></div>'
        f'</div>',
        unsafe_allow_html=True
    )

    # ── Personal summary ───────────────────────────────────────────────────────
    with st.expander("📋 Personal Details", expanded=False):
        st.markdown(f"**Name:** {result['name']}")
        st.markdown(f"**Student ID:** {result['student_id']}")
        st.markdown(f"**Date of Birth:** {result['dob']}")
        st.markdown(f"**Date Taken:** {result['date_taken']}")

    # ── Answer breakdown ───────────────────────────────────────────────────────
    with st.expander("📝 Full Answer Breakdown", expanded=False):
        for idx, ans in enumerate(answers, start=1):  # for loop over answers
            bar_pct: int = int((ans["score"] / 4) * 100)
            bar_color: str = ["#1a7a4a","#5aaa6a","#b8860b","#cc6600","#cc2222"][ans["score"]]
            st.markdown(
                f"**Q{idx}.** {ans['question']}  \n"
                f"→ *{ans['answer']}*"
            )
            st.markdown(
                f'<div style="background:#eee;border-radius:4px;height:6px;margin:2px 0 10px;">'
                f'<div style="width:{bar_pct}%;background:{bar_color};height:6px;border-radius:4px;"></div>'
                f'</div>',
                unsafe_allow_html=True
            )

    # ── Save / Download ────────────────────────────────────────────────────────
    st.markdown("### 💾 Save Your Results")
    st.markdown(
        '<div class="info-box">Choose a format and click Download. '
        'The file saves to your device automatically.</div>',
        unsafe_allow_html=True
    )
    st.markdown("")

    filename_base: str = (
        f"result_{result['student_id']}_{datetime.today().strftime('%Y%m%d_%H%M%S')}"
    )

    col_json, col_csv, col_txt = st.columns(3)

    with col_json:
        st.download_button(
            label="⬇ Download JSON",
            data=build_json_bytes(result, answers),
            file_name=filename_base + ".json",
            mime="application/json",
            use_container_width=True,
        )
        st.caption("Full nested data — best format")

    with col_csv:
        st.download_button(
            label="⬇ Download CSV",
            data=build_csv_bytes(result, answers),
            file_name=filename_base + ".csv",
            mime="text/csv",
            use_container_width=True,
        )
        st.caption("Spreadsheet compatible")

    with col_txt:
        st.download_button(
            label="⬇ Download TXT",
            data=build_txt_bytes(result, answers),
            file_name=filename_base + ".txt",
            mime="text/plain",
            use_container_width=True,
        )
        st.caption("Plain text report")

    st.markdown("")

    # ── Outcomes scale reference ────────────────────────────────────────────────
    with st.expander("📊 All Possible Outcomes", expanded=False):
        for (low, high, label, desc, emoji, c) in OUTCOMES:
            marker: str = "◀ YOUR RESULT" if low <= score <= high else ""
            st.markdown(
                f'<div style="background:{c}11;border-left:4px solid {c};'
                f'border-radius:6px;padding:8px 12px;margin:6px 0;">'
                f'<b style="color:{c};">{emoji} {low}–{high}: {label}</b> '
                f'<span style="color:#cc4400;font-size:0.8rem;font-weight:700;">{marker}</span><br>'
                f'<span style="font-size:0.85rem;color:#334;">{desc}</span>'
                f'</div>',
                unsafe_allow_html=True
            )

    # ── Navigation ─────────────────────────────────────────────────────────────
    st.markdown("")
    if st.button("🔄  Take the Survey Again", use_container_width=True):
        for key in ["answers", "current_q", "total_score", "result",
                    "surname", "given_name", "dob", "student_id", "errors"]:
            if key in ("answers",):
                st.session_state[key] = []
            elif key in ("current_q", "total_score"):
                st.session_state[key] = 0
            elif key in ("result", "errors"):
                st.session_state[key] = {}
            else:
                st.session_state[key] = ""
        st.session_state["page"] = "home"
        st.rerun()

# ── PAGE: LOAD ───────────────────────────────────────────────────────────────────

elif st.session_state["page"] == "load":

    st.markdown('<div class="step-badge">Load Existing Results</div>', unsafe_allow_html=True)
    st.markdown("### Upload a Previously Saved Results File")
    st.markdown(
        '<div class="info-box">Upload a <b>.json</b>, <b>.csv</b>, or <b>.txt</b> file '
        'that was saved from a previous survey session.</div>',
        unsafe_allow_html=True
    )
    st.markdown("")

    uploaded = st.file_uploader(
        "Choose a result file",
        type=["json", "csv", "txt"],
        label_visibility="collapsed"
    )

    if uploaded is not None:
        ext: str = uploaded.name.rsplit(".", 1)[-1].lower()
        raw_bytes: bytes = uploaded.read()

        # Validate extension is in allowed set
        allowed_ext: set = {"json", "csv", "txt"}
        is_valid_ext: bool = ext in allowed_ext

        if not is_valid_ext:
            st.error("Unsupported file type. Please upload a .json, .csv, or .txt file.")

        elif ext == "json":
            try:
                data: dict = json.loads(raw_bytes.decode("utf-8"))
                st.success("✅ JSON file loaded successfully.")

                # Summary fields
                summary_keys: set = {"name", "student_id", "dob", "date_taken",
                                     "total_score", "max_score", "percentage",
                                     "psychological_state", "description"}
                st.markdown("#### Summary")
                for key in summary_keys:
                    if key in data:
                        label_str: str = key.replace("_", " ").title()
                        st.markdown(f"**{label_str}:** {data[key]}")

                if "answers" in data:
                    st.markdown(f"**Questions Answered:** {len(data['answers'])}")
                    with st.expander("View All Answers"):
                        for i, ans in enumerate(data["answers"], 1):
                            st.markdown(f"**Q{i}.** {ans.get('question','')}")
                            st.markdown(f"→ *{ans.get('answer','')}* (score: {ans.get('score','')})")
            except (json.JSONDecodeError, KeyError) as e:
                st.error(f"Could not parse JSON file: {e}")

        elif ext == "csv":
            text: str = raw_bytes.decode("utf-8")
            reader = csv.reader(io.StringIO(text))
            rows: list = list(reader)
            st.success("✅ CSV file loaded successfully.")
            st.markdown("#### Content")
            for row in rows:
                if len(row) == 2:
                    st.markdown(f"**{row[0]}:** {row[1]}")
                elif len(row) == 4 and row[0].isdigit():
                    st.markdown(f"Q{row[0]}: {row[1]} → *{row[2]}* (score: {row[3]})")

        else:  # txt
            content: str = raw_bytes.decode("utf-8")
            st.success("✅ TXT file loaded successfully.")
            st.text(content)

    st.markdown("")
    if st.button("← Back to Home", use_container_width=True):
        st.session_state["page"] = "home"
        st.rerun()

# ── FOOTER ─────────────────────────────────────────────────────────────────────

st.markdown("---")
st.markdown(
    '<div style="text-align:center;font-size:0.8rem;color:#888;">'
    'Quiet Study Zone Preference Survey &nbsp;·&nbsp; '
    'Fundamentals of Programming 4BUIS008C &nbsp;·&nbsp; '
    'Westminster International University in Tashkent'
    '</div>',
    unsafe_allow_html=True
)
