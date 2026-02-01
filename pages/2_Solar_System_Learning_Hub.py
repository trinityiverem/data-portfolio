from solar_system_bot.solar_core import get_bot_reply
import streamlit as st

from pathlib import Path

import streamlit as st
import pandas as pd

# Import the chatbot logic from your package
from solar_system_bot.solar_core import get_bot_reply

# -------------------------------------------------------------------
# Paths
# -------------------------------------------------------------------
PAGE_DIR = Path(__file__).resolve().parent        # .../pages
PROJECT_DIR = PAGE_DIR.parent                     # repo root
SOLAR_DIR = PROJECT_DIR / "solar_system_bot"      # solar_system_bot folder
IMAGES_DIR = SOLAR_DIR / "images"                 # gifs folder
QUIZ_PATH = SOLAR_DIR / "quiz.csv"                # quiz file


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
An interactive learning tool about the Solar System.

It combines:
- A rule-based Python chatbot (AIML + CSV knowledge)
- A Streamlit UI with chat, a planet explorer and a quiz
- Simple data structures and session state to manage interaction
        """
    )

    st.subheader("About the developer")
    st.write(
        """
Created by Trinity, a Computing graduate exploring data, AI
and interactive learning tools.
        """
    )


# -------------------------------------------------------------------
# Chat mode
# -------------------------------------------------------------------
if mode == "Chat":
    st.title("💬 Chat with the bot")
    st.write("Ask me about the Solar System, planets, or space objects!")

    # Separate key so it doesn’t clash with other pages
    if "solar_messages" not in st.session_state:
        st.session_state["solar_messages"] = []

    # Show previous messages
    for msg in st.session_state["solar_messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    user_input = st.chat_input("Type your message here...")

    if user_input:
        # Add user message
        st.session_state["solar_messages"].append(
            {"role": "user", "content": user_input}
        )

        # Get bot reply from your core logic
        reply = get_bot_reply(user_input)

        # Add bot message
        st.session_state["solar_messages"].append(
            {"role": "assistant", "content": reply}
        )

        st.rerun()


# -------------------------------------------------------------------
# Planet explorer mode
# -------------------------------------------------------------------
elif mode == "Planet explorer":
    st.title("🌍 Planet explorer")

    # Optional solar system gif at the top
    solar_system_gif = IMAGES_DIR / "solar_system.gif"
    if solar_system_gif.exists():
        st.image(solar_system_gif, caption="Solar system overview")
        st.divider()

    # Planet data with gifs and facts
    planets = {
        "Mercury": {
            "description": "The smallest planet and closest to the Sun. It has no moons.",
            "facts": {
                "Orbital period (days)": "88",
                "Moons": "0",
                "Position from Sun": "1st",
            },
            "gif": IMAGES_DIR / "mercury.gif",
        },
        "Venus": {
            "description": "A hot world with a thick, toxic atmosphere and runaway greenhouse effect.",
            "facts": {
                "Orbital period (days)": "225",
                "Moons": "0",
                "Position from Sun": "2nd",
            },
            "gif": IMAGES_DIR / "venus.gif",
        },
        "Earth": {
            "description": "Our home planet, the only known world to support life.",
            "facts": {
                "Orbital period (days)": "365",
                "Moons": "1",
                "Position from Sun": "3rd",
            },
            "gif": IMAGES_DIR / "earth.gif",
        },
        "Mars": {
            "description": "The Red Planet, with polar ice caps and the largest volcano in the Solar System.",
            "facts": {
                "Orbital period (days)": "687",
                "Moons": "2",
                "Position from Sun": "4th",
            },
            "gif": IMAGES_DIR / "mars.gif",
        },
        "Jupiter": {
            "description": "The largest planet, a gas giant with dozens of moons and a Great Red Spot storm.",
            "facts": {
                "Orbital period (days)": "4,333",
                "Moons": "95+",
                "Position from Sun": "5th",
            },
            "gif": IMAGES_DIR / "jupiter.gif",
        },
        "Saturn": {
            "description": "Famous for its stunning ring system and many icy moons.",
            "facts": {
                "Orbital period (days)": "10,759",
                "Moons": "80+",
                "Position from Sun": "6th",
            },
            "gif": IMAGES_DIR / "saturn.gif",
        },
        "Uranus": {
            "description": "An ice giant that rotates on its side with faint rings.",
            "facts": {
                "Orbital period (days)": "30,687",
                "Moons": "25+",
                "Position from Sun": "7th",
            },
            "gif": IMAGES_DIR / "uranus.gif",
        },
        "Neptune": {
            "description": "A distant ice giant with strong winds and a deep blue colour.",
            "facts": {
                "Orbital period (days)": "60,190",
                "Moons": "14",
                "Position from Sun": "8th",
            },
            "gif": IMAGES_DIR / "neptune.gif",
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
        gif_path = info["gif"]
        if gif_path.exists():
            st.image(gif_path, caption=f"{planet_name} (animation)")
        else:
            st.info(
                f"Add a GIF file for this planet called {gif_path.name} "
                "to the images/ folder inside solar_system_bot to see it here."
            )

    st.caption("You can also ask the chatbot about these planets in Chat mode.")


# -------------------------------------------------------------------
# Quiz mode
# -------------------------------------------------------------------
elif mode == "Quiz":
    st.title("🧠 Solar System Quiz")

    if not QUIZ_PATH.exists():
        st.error("quiz.csv not found. Please add it to solar_system_bot/quiz.csv.")
    else:
        quiz_df = pd.read_csv(QUIZ_PATH)

        required_cols = {"question", "option_a", "option_b", "option_c", "correct_option"}
        if not required_cols.issubset(set(quiz_df.columns)):
            st.error(
                "quiz.csv must have columns: question, option_a, option_b, option_c, correct_option"
            )
        else:
            # Separate keys so they don't clash with other pages
            if "solar_quiz_index" not in st.session_state:
                st.session_state.solar_quiz_index = 0
                st.session_state.solar_quiz_score = 0

            total_questions = len(quiz_df)

            if st.session_state.solar_quiz_index >= total_questions:
                st.success(
                    f"Quiz complete! Your score: "
                    f"{st.session_state.solar_quiz_score} / {total_questions}"
                )
                if st.button("Restart quiz"):
                    st.session_state.solar_quiz_index = 0
                    st.session_state.solar_quiz_score = 0
                    st.rerun()
            else:
                q = quiz_df.iloc[st.session_state.solar_quiz_index]

                st.markdown(
                    f"**Question {st.session_state.solar_quiz_index + 1} "
                    f"of {total_questions}**"
                )
                st.write(q["question"])

                options = [
                    f"A: {q['option_a']}",
                    f"B: {q['option_b']}",
                    f"C: {q['option_c']}",
                ]

                selected = st.radio(
                    "Choose an answer:",
                    options,
                    key=f"solar_quiz_q_{st.session_state.solar_quiz_index}",
                )

                if st.button(
                    "Submit answer",
                    key=f"solar_submit_{st.session_state.solar_quiz_index}",
                ):
                    chosen_letter = selected[0]  # "A", "B", or "C"
                    correct_letter = str(q["correct_option"]).strip().upper()

                    if chosen_letter == correct_letter:
                        st.success("Correct! 🎉")
                        st.session_state.solar_quiz_score += 1
                    else:
                        st.error(f"Not quite. The correct answer was {correct_letter}.")

                    st.session_state.solar_quiz_index += 1
                    st.rerun()

                st.write(
                    f"Current score: "
                    f"{st.session_state.solar_quiz_score} / {total_questions}"
                )

