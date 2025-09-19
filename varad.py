import streamlit as st
import pandas as pd
import random
from googletrans import Translator

# Load data
ragas_df = pd.read_csv("Ragas new.csv")
artists_df = pd.read_csv("Artists (1).csv")
quiz_df = pd.read_csv("Classical_Music_Quiz.csv")
trivia_df = pd.read_csv("Dailytrivia new.csv")
compare_df = pd.read_csv("Hindustani_vs_Carnatic_Comparison.csv")

# Translator setup
translator = Translator()
LANGUAGE_CODE_MAP = {"English": "en", "Hindi": "hi", "Marathi": "mr", "Kannada": "kn"}
translate = lambda text, lang: translator.translate(text, dest=LANGUAGE_CODE_MAP.get(lang, "en")).text if lang != "English" else text

# App setup
st.set_page_config(page_title="RaagBot", layout="wide")
st.title("\U0001F3B6 RaagBot - Indian Classical Music Chatbot")

# CSS for chat bubbles
st.markdown("""
<style>
.chat-bubble { padding: 10px 15px; border-radius: 15px; margin: 10px 0; max-width: 80%; font-size: 16px; }
.user-bubble { background-color: #9c27b0; margin-left: auto; }
.bot-bubble { background-color: #f2f2f2; margin-right: auto; }
</style>
""", unsafe_allow_html=True)

# Session state
for key in ["chat_history", "language", "quiz_mode", "score", "question_index", "shuffled_quiz", "quiz_done"]:
    if key not in st.session_state:
        st.session_state[key] = [] if key == "chat_history" else False if key == "quiz_mode" or key == "quiz_done" else 0 if key == "score" or key == "question_index" else quiz_df.sample(frac=1).to_dict(orient="records") if key == "shuffled_quiz" else "English"

# Language selection
if not st.session_state["language"]:
    st.session_state.language = st.selectbox("Choose Language", list(LANGUAGE_CODE_MAP.keys()))

# Input
user_input = st.text_input("You:")
response = ""
lang = st.session_state.language

# Raga info
for name in ragas_df["Name"]:
    if name.lower() in user_input.lower():
        r = ragas_df[ragas_df["Name"] == name].iloc[0]
        response = f"""
**Raga**: {r['Name']}  
**Thaat**: {r['Thaat']}  
**Aroha**: {r['Aroha']}  
**Avaroha**: {r['Avaroha']}  
**Vadi**: {r['Vadi']}  
**Samvadi**: {r['Samvadi']}  
**Time**: {r['Time']}  
**Rasa**: {r['Rasa']}  
**Origin**: {r['Origin']}"""
        break

# Artist info
if not response:
    for name in artists_df["Name"]:
        if name.lower() in user_input.lower():
            a = artists_df[artists_df["Name"] == name].iloc[0]
            response = f"Artist: {name}\n" + "\n".join([f"{col}: {a[col]}" for col in artists_df.columns if col != "Name"])
            break

# Trivia
if "trivia" in user_input.lower() and not st.session_state.quiz_mode:
    response = random.choice(trivia_df["fact"].tolist())

# Comparison
if "hindustani" in user_input.lower() and "carnatic" in user_input.lower():
    st.markdown("### Hindustani vs Carnatic Classical Music")
    st.markdown(compare_df.to_html(index=False), unsafe_allow_html=True)

# Start quiz
if "quiz" in user_input.lower():
    st.session_state.quiz_mode = True
    st.session_state.shuffled_quiz = quiz_df.sample(frac=1).to_dict(orient="records")
    st.session_state.question_index = 0
    st.session_state.score = 0
    st.session_state.quiz_done = False
    st.rerun()

# Save chat
if response:
    user_text = translate(user_input, lang)
    bot_text = translate(response, lang)
    st.session_state.chat_history.append((user_text, bot_text))

# Show chat
if not st.session_state.quiz_mode:
    for user, bot in st.session_state.chat_history:
        st.markdown(f"<div class='chat-bubble user-bubble'>You: {user}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='chat-bubble bot-bubble'>\U0001F3B5 {bot}</div>", unsafe_allow_html=True)

# Quiz logic
if st.session_state.quiz_mode:
    if not st.session_state.quiz_done:
        q = st.session_state.shuffled_quiz[st.session_state.question_index]
        st.subheader(f"Q{st.session_state.question_index + 1}: {q['Question']}")
        options = [q[f"Option {i}"] for i in range(1, 5)]
        selected = st.radio("Choose an answer:", options, key=st.session_state.question_index)

        if st.button("Next"):
            if selected == q["Answer"]:
                st.session_state.score += 1
            st.session_state.question_index += 1
            if st.session_state.question_index >= len(st.session_state.shuffled_quiz):
                st.session_state.quiz_done = True
            st.rerun()
    else:
        st.success("\U0001F389 Quiz Complete!")
        st.markdown(f"**Score**: {st.session_state.score} / {len(st.session_state.shuffled_quiz)}")
        if st.button("Restart Quiz"):
            st.session_state.quiz_mode = False
            st.session_state.score = 0
            st.session_state.question_index = 0
            st.session_state.quiz_done = False
            st.rerun()

# Restart chat
if st.button("Restart Chat"):
    st.session_state.chat_history = []
    st.session_state.quiz_mode = False
    st.rerun()