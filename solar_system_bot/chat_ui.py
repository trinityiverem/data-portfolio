import streamlit as st
from pathlib import Path
import pandas as pd

from main import get_bot_reply

BASE_DIR = Path(__file__).resolve().parent

st.set_page_config(page_title="Solar System Learning Hub", page_icon="🪐")

# -------------------------------------------------------------------
# Sidebar: mode selector + about sections
# -------------------------------------------------------------------
with st.sidebar:
    st.title("🪐 Solar System Hub")

    mode = st.radio(
        "Choose a mode:",
        ["Chat", "Planet explorer", "Quiz"],
    )

    st.divider()
    st.subheader("About this project")
    st.write(
        """
This app is a small learning tool about the Solar System.

It combines:
- A rule-based chatbot built in Python
- AIML + CSV knowledge base
- A Streamlit interface for chat, exploration and quizzes
        """
    )

    st.subheader("About the developer")
    st.write(
        """
Created by Trinity, a tech-focused graduate exploring data, AI
and interactive learning tools.
        """
    )


# -------------------------------------------------------------------
# Chat mode
# -------------------------------------------------------------------
if mode == "Chat":
    st.title("💬 Chat with the bot")
    st.write("Ask me about the Solar System, planets, or space objects!")

    # Store conversation in session_state
    if "messages" not in st.session_state:
        st.session_state["messages"] = []  # list of {"role": "user"/"assistant", "content": "..."}

    # Display previous messages
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input box
    user_input = st.chat_input("Type your message here...")

    if user_input:
        # Add user message
        st.session_state["messages"].append({"role": "user", "content": user_input})

        # Get bot reply
        reply = get_bot_reply(user_input)

        # Add bot message
        st.session_state["messages"].append({"role": "assistant", "content": reply})

        # Rerun so the new messages show up in the loop at the top
        st.rerun()


# -------------------------------------------------------------------
# Planet explorer mode
# -------------------------------------------------------------------
elif mode == "Planet explorer":
    st.title("🌍 Planet explorer")

    # Simple planet dataset (you can extend this)
    planets = {
        "Mercury": {
            "description": "The smallest planet and closest to the Sun. It has no moons.",
            "facts": {
                "Orbital period (days)": "88",
                "Moons": "0",
                "Position from Sun": "1st",
            },
            "image": BASE_DIR / "images" / "mercury.gif",
        },
        "Venus": {
            "description": "A hot world with a thick, toxic atmosphere and runaway greenhouse effect.",
            "facts": {
                "Orbital period (days)": "225",
                "Moons": "0",
                "Position from Sun": "2nd",
            },
            "image": BASE_DIR / "images" / "venus.gif",
        },
        "Earth": {
            "description": "Our home planet, the only known world to support life.",
            "facts": {
                "Orbital period (days)": "365",
                "Moons": "1",
                "Position from Sun": "3rd",
            },
            "image": BASE_DIR / "images" / "earth.gif",
        },
        "Mars": {
            "description": "The Red Planet, with polar ice caps and the largest volcano in the Solar System.",
            "facts": {
                "Orbital period (days)": "687",
                "Moons": "2",
                "Position from Sun": "4th",
            },
            "image": BASE_DIR / "images" / "mars.gif",
        },
        "Jupiter": {
            "description": "The largest planet, a gas giant with dozens of moons and a Great Red Spot storm.",
            "facts": {
                "Orbital period (days)": "4,333",
                "Moons": "95+",
                "Position from Sun": "5th",
            },
            "image": BASE_DIR / "images" / "jupiter.gif",
        },
        "Saturn": {
            "description": "Famous for its stunning ring system and many icy moons.",
            "facts": {
                "Orbital period (days)": "10,759",
                "Moons": "80+",
                "Position from Sun": "6th",
            },
            "image": BASE_DIR / "images" / "saturn.gif",
        },
        "Uranus": {
            "description": "An ice giant that rotates on its side with faint rings.",
            "facts": {
                "Orbital period (days)": "30,687",
                "Moons": "25+",
                "Position from Sun": "7th",
            },
            "image": BASE_DIR / "images" / "uranus.gif",
        },
        "Neptune": {
            "description": "A distant ice giant with strong winds and a deep blue colour.",
            "facts": {
                "Orbital period (days)": "60,190",
                "Moons": "14",
                "Position from Sun": "8th",
            },
            "image": BASE_DIR / "images" / "neptune.gif",
        },
    }

    planet_name = st.selectbox("Choose a planet:", list(planets.keys()))

    info = planets[planet_name]

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader(planet_name)
        st.write(info["description"])

        st.markdown("**Key facts:**")
        for label, value in info["facts"].items():
            st.write(f"- **{label}:** {value}")

    with col2:
        img_path = info["image"]
        if img_path.exists():
            st.image(img_path, caption=planet_name)
        else:
            st.info("Add an image file for this planet to the images/ folder to see it here.")

    st.caption("You can ask the chatbot about these planets in Chat mode as well!")


# -------------------------------------------------------------------
# Quiz mode
# -------------------------------------------------------------------
elif mode == "Quiz":
    st.title("🧠 Solar System Quiz")

    quiz_path = BASE_DIR / "quiz.csv"

    if not quiz_path.exists():
        st.error("quiz.csv not found. Please create it in the same folder as this app.")
    else:
        quiz_df = pd.read_csv(quiz_path)

        required_cols = {"question", "option_a", "option_b", "option_c", "correct_option"}
        if not required_cols.issubset(set(quiz_df.columns)):
            st.error(
                "quiz.csv must have columns: question, option_a, option_b, option_c, correct_option"
            )
        else:
            # Initialise quiz state
            if "quiz_index" not in st.session_state:
                st.session_state.quiz_index = 0
                st.session_state.quiz_score = 0

            total_questions = len(quiz_df)

            # If finished
            if st.session_state.quiz_index >= total_questions:
                st.success(
                    f"Quiz complete! Your score: {st.session_state.quiz_score} / {total_questions}"
                )
                if st.button("Restart quiz"):
                    st.session_state.quiz_index = 0
                    st.session_state.quiz_score = 0
                    st.rerun()
            else:
                q = quiz_df.iloc[st.session_state.quiz_index]

                st.markdown(f"**Question {st.session_state.quiz_index + 1} of {total_questions}**")
                st.write(q["question"])

                options = [
                    f"A: {q['option_a']}",
                    f"B: {q['option_b']}",
                    f"C: {q['option_c']}",
                ]

                selected = st.radio(
                    "Choose an answer:",
                    options,
                    key=f"quiz_q_{st.session_state.quiz_index}",
                )

                if st.button("Submit answer", key=f"submit_{st.session_state.quiz_index}"):
                    chosen_letter = selected[0]  # "A", "B", or "C"
                    correct_letter = str(q["correct_option"]).strip().upper()

                    if chosen_letter == correct_letter:
                        st.success("Correct! 🎉")
                        st.session_state.quiz_score += 1
                    else:
                        st.error(f"Not quite. The correct answer was {correct_letter}.")

                    st.session_state.quiz_index += 1
                    st.rerun()

                st.write(f"Current score: {st.session_state.quiz_score} / {total_questions}")
