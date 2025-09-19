
import streamlit as st
import pandas as pd
import random
from PIL import Image

from googletrans import Translator

# Load data
ragas_df = pd.read_csv("Ragas new.csv")
artists_df = pd.read_csv("Artists (1).csv")
quiz_df = pd.read_csv("Classical_Music_Quiz.csv")
trivia_df = pd.read_csv("Dailytrivia new.csv")
compare_df = pd.read_csv("Hindustani_vs_Carnatic_Comparison.csv")

translator = Translator()
st.set_page_config(page_title="Swaranand: Indian Classical Music Chatbot", layout="wide")
st.title("🎶 Indian Classical Music Companion")

right_image = Image.open("Instruments.jpg")  # Replace with your image path

# Create two columns side-by-side
col1, col2 = st.columns([1, 1])  # Adjust ratio as needed

with col1:
    st.image("Swaranand logo.png", use_container_width=True)

with col2:
    st.image(right_image, use_container_width=True)


# Simple user login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.user_scores = {}

if not st.session_state.logged_in:
    st.subheader("Login")
    username = st.text_input("Enter your name to start:")
    if st.button("Login") and username:
        st.session_state.logged_in = True
        st.session_state.username = username
        if username not in st.session_state.user_scores:
            st.session_state.user_scores[username] = {"score": 0, "history": []}
        st.rerun()
    st.stop()

# Language selection
lang_choice = st.selectbox("Choose Language", ["English", "Hindi", "Marathi", "Kannada"])
LANGUAGE_CODE_MAP = {
    "English": "en",
    "Hindi": "hi",
    "Marathi": "mr",
    "Kannada": "kn",
    # Add more if needed
}

#Translate
translate = lambda text: translator.translate(text, dest=LANGUAGE_CODE_MAP.get(lang_choice, "en")).text if lang_choice != "English" else text


# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Raga Info", "Artist Info", "Daily Trivia", "Compare Traditions", "Start Quiz"])

with tab1:
    st.header(translate("Raga Information"))
    selected_raga = st.selectbox("Select a Raga", ragas_df["Name"])
    raga_info = ragas_df[ragas_df["Name"] == selected_raga].iloc[0]
    for col in ragas_df.columns:
        st.markdown(f"**{translate(col)}:** {translate(str(raga_info[col]))}")

with tab2:
    st.header(translate("Artist Information"))
    selected_artist = st.selectbox("Select an Artist", artists_df["Name"])
    artist_info = artists_df[artists_df["Name"] == selected_artist].iloc[0]
    for col in artists_df.columns:
        st.markdown(f"**{translate(col)}:** {translate(str(artist_info[col]))}")

with tab3:
    st.header(translate("Daily Trivia"))
    trivia_fact = random.choice(trivia_df["fact"].tolist())
    st.info(translate(trivia_fact))

with tab4:
    st.header(translate("Comparison: Hindustani vs Carnatic"))
    st.dataframe(compare_df.rename(columns=lambda x: translate(x)))

with tab5:
    st.header(translate("Quiz Time!"))

if "quiz_score" not in st.session_state:
    st.session_state.quiz_score = 0
    st.session_state.quiz_index = 0

if st.session_state.quiz_index < len(quiz_df):
    question = quiz_df.iloc[st.session_state.quiz_index]
    st.subheader(translate(question["Question"]))
    
    # Define options
    options = ["Option 1", "Option 2", "Option 3", "Option 4"]
    option_texts = [translate(question[opt]) for opt in options]
    
    # Display radio buttons for answer
    answer = st.radio("", option_texts)

    if st.button(translate("Submit Answer")):
        correct_answer = question["Answer"].strip()
        option_values = [question["Option 1"], question["Option 2"], question["Option 3"], question["Option 4"]]
        
        # Clean and match
        try:
            correct_index = option_values.index(correct_answer)
            correct_option = translate(option_values[correct_index])
        except ValueError:
            correct_option = "Not Found"

        # Compare selected answer with correct one
        if answer == correct_option:
            st.success(translate("Correct!"))
            st.session_state.quiz_score += 1
        else:
            st.error(translate(f"Wrong! Correct answer was: {correct_option}"))

        st.session_state.quiz_index += 1
        st.rerun()

else:
    st.success(translate(f"Quiz Finished! Your score: {st.session_state.quiz_score}/{len(quiz_df)}"))

    if st.button("Restart Quiz"):
        st.session_state.quiz_index = 0
        st.session_state.quiz_score = 0
        st.rerun()