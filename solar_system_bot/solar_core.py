"""
main.py - Solar system / general chatbot

Features:
- Uses AIML (*.xml) patterns for core conversational replies
- Uses a questions.csv file for FAQ-style question/answer matching via TF-IDF
- Uses a kb.csv file and NLTK's logic ResolutionProver for simple logical checks
  about planets and moons (e.g. "Is Europa a moon?").
- Exposes `get_bot_reply(message: str) -> str` for use in UIs such as Streamlit.
- Also supports a simple CLI chat loop when run directly: `python main.py`.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import List, Optional

# -------------------------------------------------------------------
# Compatibility patch for old python-aiml on modern Python versions
# -------------------------------------------------------------------
# Older versions of python-aiml call time.clock(), which was removed in Python 3.8+.
# We patch it to use time.perf_counter so the library works on Python 3.12.
if not hasattr(time, "clock"):
    time.clock = time.perf_counter  # type: ignore[attr-defined]

# -------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------
try:
    import aiml
except ImportError:
    aiml = None  # type: ignore[assignment]

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.sem import Expression
from nltk.inference import ResolutionProver

# -------------------------------------------------------------------
# Paths and global state
# -------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent


# AIML kernel
kern = aiml.Kernel()

# Knowledge base for logical reasoning
read_expr = Expression.fromstring
kb_expressions: List = []

# Data for FAQ matching
faq_df: Optional[pd.DataFrame] = None
tfidf_vectorizer: Optional[TfidfVectorizer] = None
tfidf_matrix = None


# -------------------------------------------------------------------
# Initialisation helpers
# -------------------------------------------------------------------

def _init_aiml() -> None:
    """Load AIML startup and chat files if present."""
    startup = BASE_DIR / "std-startup.xml"
    chat = BASE_DIR / "chat.xml"

    if startup.exists():
        kern.learn(str(startup))
    if chat.exists():
        kern.learn(str(chat))

    # Many AIML sets require a "load aiml b" bootstrap, but it's safe to ignore errors.
    try:
        kern.respond("load aiml b")
    except Exception:
        pass


def _init_faq() -> None:
    """Load questions.csv into a DataFrame and prepare TF-IDF matrix."""
    global faq_df, tfidf_vectorizer, tfidf_matrix

    questions_path = BASE_DIR / "questions.csv"
    if not questions_path.exists():
        return

    # Handle possible UTF-8 BOM and weird column names
    df = pd.read_csv(questions_path, encoding="utf-8")
    # Strip BOM and whitespace from column names
    df.columns = [str(c).strip().lstrip("\ufeff") for c in df.columns]

    # Expect columns: question, answer
    if not {"question", "answer"}.issubset(df.columns):
        # Try fallback for older naming
        if 0 in df.columns and 1 in df.columns:
            df.columns = ["question", "answer"]
        else:
            return

    df["question_clean"] = df["question"].astype(str).str.strip().str.lower()

    vectorizer = TfidfVectorizer()
    matrix = vectorizer.fit_transform(df["question_clean"])

    faq_df = df
    tfidf_vectorizer = vectorizer
    tfidf_matrix = matrix


def _init_kb() -> None:
    """Load logical knowledge base from kb.csv if present."""
    global kb_expressions

    kb_path = BASE_DIR / "kb.csv"
    if not kb_path.exists():
        return

    kb_expressions = []
    data = pd.read_csv(kb_path, header=None)

    for row in data[0]:
        text = str(row).strip()
        if not text:
            continue
        # Strip potential BOM
        text = text.lstrip("\ufeff")
        try:
            kb_expressions.append(read_expr(text))
        except Exception as e:
            # Skip malformed rows but continue
            print(f"[WARN] Could not parse KB row '{text}': {e}")


# Initialise on import so get_bot_reply() is ready immediately
_init_aiml()
_init_faq()
_init_kb()


# -------------------------------------------------------------------
# Logic helpers
# -------------------------------------------------------------------

def _try_logic_query(message: str) -> Optional[str]:
    """
    Try to interpret the message as a logical query about planets/moons.

    Currently supports patterns like:
      - "is europa a moon"
      - "is mars a planet?"
    """
    if not kb_expressions:
        return None

    text = message.strip().lower()

    if not text.startswith("is "):
        return None

    # crude pattern: "is X a Y" or "is X an Y"
    parts = text[3:]  # drop "is "
    # remove trailing punctuation
    for ch in "?.!":
        if parts.endswith(ch):
            parts = parts[:-1]

    # look for " a " or " an "
    if " a " in parts:
        obj, pred = parts.split(" a ", 1)
    elif " an " in parts:
        obj, pred = parts.split(" an ", 1)
    else:
        return None

    obj = obj.strip()
    pred = pred.strip()

    if not obj or not pred:
        return None

    # normalise to lowercase for our kb
    expr_str = f"{pred}({obj})"
    try:
        expr = read_expr(expr_str)
    except Exception:
        return None

    try:
        result = ResolutionProver().prove(expr, kb_expressions, verbose=False)
    except Exception:
        return None

    if result:
        return f"Yes, based on my knowledge base, it is true that {obj} is a {pred}."
    else:
        return f"I cannot prove from my knowledge base that {obj} is a {pred}."


def _faq_fallback(message: str, threshold: float = 0.35) -> Optional[str]:
    """
    Use TF-IDF cosine similarity to match the user's message
    to the closest FAQ question in questions.csv.
    """
    if faq_df is None or tfidf_vectorizer is None or tfidf_matrix is None:
        return None

    query = message.strip().lower()
    if not query:
        return None

    query_vec = tfidf_vectorizer.transform([query])
    scores = cosine_similarity(query_vec, tfidf_matrix)[0]
    best_idx = scores.argmax()
    best_score = scores[best_idx]

    if best_score < threshold:
        return None

    answer = str(faq_df.iloc[best_idx]["answer"])
    return answer


# -------------------------------------------------------------------
# Public chatbot API
# -------------------------------------------------------------------

def get_bot_reply(user_message: str) -> str:
    """
    Main function to get a reply from the bot.

    Order of attempts:
      1. Logic query on kb.csv (e.g. "Is Europa a moon?")
      2. AIML kernel response (chat.xml / std-startup.xml)
      3. FAQ matching via questions.csv + TF-IDF
      4. Generic fallback message
    """
    user_message = user_message.strip()
    if not user_message:
        return "Please type something so I can help you."

    # 1) Logic-based query (planets/moons)
    logic_answer = _try_logic_query(user_message)
    if logic_answer:
        return logic_answer

    # 2) AIML-based reply
    try:
        aiml_reply = kern.respond(user_message)
    except Exception:
        aiml_reply = ""

    if aiml_reply and aiml_reply.strip():
        return aiml_reply.strip()

    # 3) FAQ / TF-IDF fallback
    faq_answer = _faq_fallback(user_message)
    if faq_answer:
        return faq_answer

    # 4) Generic fallback
    return "I'm not sure how to answer that yet. Try asking me about the solar system or space objects."


# -------------------------------------------------------------------
# CLI entry point
# -------------------------------------------------------------------

def main() -> None:
    print("Welcome to this chatbot. Type 'quit' or 'exit' to leave.\n")
    while True:
        try:
            user_input = input("You > ")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if user_input.strip().lower() in {"quit", "exit"}:
            print("Goodbye!")
            break

        reply = get_bot_reply(user_input)
        print(f"Bot > {reply}")


if __name__ == "__main__":
    main()
