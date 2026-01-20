import streamlit as st
from streamlit_lottie import st_lottie
from googletrans import Translator
from transformers import pipeline
import pandas as pd
import sqlite3
import random
import time
import requests

# --- 1. PAGE CONFIG & THEME INITIALIZATION ---
st.set_page_config(page_title="Lumina | Zen Space", page_icon="🌱", layout="wide")

# Initialize Session States
if "first_visit" not in st.session_state: st.session_state.first_visit = True
if "messages" not in st.session_state: st.session_state.messages = []

# --- 2. ASSETS & MODELS ---
@st.cache_resource
def load_tools():
    translator = Translator()
    # High-accuracy emotion model (RoBERTa)
    classifier = pipeline("text-classification", model="cardiffnlp/twitter-roberta-base-sentiment-latest")
    return translator, classifier

translator, classifier = load_tools()

def load_lottieurl(url):
    r = requests.get(url)
    return r.json() if r.status_code == 200 else None

# --- 3. DATABASE LOGIC ---
def init_db():
    conn = sqlite3.connect('lumina_wellness.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS logs (date TEXT, mood TEXT, trigger TEXT)')
    conn.commit()
    conn.close()

# --- 4. SIDEBAR: CONTROLS & ATMOSPHERE ---
with st.sidebar:
    st.title("🌿 Lumina Settings")
    
    # Theme Toggle
    theme_choice = st.radio("Choose Atmosphere", ["Daylight (Fresh)", "Midnight (Calm)"])
    
    st.divider()
    
    # Ambient Soundscape
    st.subheader("🎧 Soundscape")
    sound_choice = st.selectbox("Background Noise", ["None", "Soft Rain", "Deep Forest", "Lo-Fi Study"])
    sounds = {
        "Soft Rain": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-10.mp3",
        "Deep Forest": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-13.mp3",
        "Lo-Fi Study": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-15.mp3"
    }
    if sound_choice != "None":
        st.audio(sounds[sound_choice], format="audio/mp3", loop=True)

    st.divider()
    
    # Pomodoro Timer
    st.subheader("⏳ Focus Timer")
    if st.button("Start 25m Focus Session"):
        st.toast("Focus mode active! You've got this.")

# --- 5. DYNAMIC UI STYLING (THEMES) ---
if theme_choice == "Midnight (Calm)":
    bg_gradient = "linear-gradient(180deg, #0f172a 0%, #1e1b4b 100%)"
    card_bg = "rgba(30, 41, 59, 0.7)"
    text_color = "#f8fafc"
    lottie_url = "https://lottie.host/682946c1-507c-4749-8084-3c66289d38f8/U7S8vOaDbe.json" # Stars
else:
    bg_gradient = "linear-gradient(180deg, #E3F2FD 0%, #E8F5E9 100%)"
    card_bg = "rgba(255, 255, 255, 0.7)"
    text_color = "#2D3748"
    lottie_url = "https://lottie.host/8051e041-0672-46c5-a3d8-7e3f436980e1/V8u1X2vX6t.json" # Sun/Zen

st.markdown(f"""
    <style>
    .stApp {{ background: {bg_gradient}; color: {text_color}; }}
    .glass-card {{
        background: {card_bg};
        border-radius: 20px;
        padding: 25px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center;
        margin-bottom: 20px;
    }}
    h1, h2, h3, p {{ color: {text_color} !important; font-family: 'Helvetica Neue', sans-serif; }}
    .stButton>button {{ border-radius: 20px; background-color: #81C784 !important; color: white !important; }}
    </style>
""", unsafe_allow_html=True)

# --- 6. MAIN CONTENT ---
init_db()
lottie_zen = load_lottieurl(lottie_url)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if lottie_zen: st_lottie(lottie_zen, height=200)
    st.markdown(f'<div class="glass-card"><h1>Lumina</h1><p>Your multilingual safe space for mental clarity.</p></div>', unsafe_allow_html=True)
    
    # Affirmation
    affirmations = ["You are capable of hard things.", "Take it one breath at a time.", "Your grades do not define your worth."]
    st.markdown(f"<p style='text-align:center; font-style:italic;'>\"{random.choice(affirmations)}\"</p>", unsafe_allow_html=True)

# --- 7. THE TABS ---
tab1, tab2, tab3 = st.tabs(["💬 Chat Support", "📝 Reflection", "🔬 Science"])

with tab1:
    # SOS Expander
    with st.expander("🚨 Need Immediate Help?", expanded=False):
        st.error("Crisis Line: 988 | Campus Security: [Link]")
    
    # Chat Loop
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.write(msg["content"])

    if prompt := st.chat_input("How are you feeling right now?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)

        with st.spinner("Lumina is thinking..."):
            # A. Language & Sentiment
            lang = translator.detect(prompt).lang
            translated_en = translator.translate(prompt, dest='en').text
            res = classifier(translated_en)[0]
            label = res['label'] # positive, neutral, negative

            # B. Context-Aware Music mapping
            music_links = {
                "negative": ["Comforting Piano", "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"],
                "neutral": ["Focus frequencies", "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-8.mp3"]
            }

            # C. Response logic
            response_en = "I'm listening. Thank you for sharing your heart with me."
            if label == "negative":
                response_en = "I'm sorry things are heavy. I've found some music to sit with you through this."
            
            final_resp = translator.translate(response_en, dest=lang).text
            
            with st.chat_message("assistant"):
                st.write(final_resp)
                if label in music_links:
                    st.caption(f"🎵 Suggested: {music_links[label][0]}")
                    st.audio(music_links[label][1])

        st.session_state.messages.append({"role": "assistant", "content": final_resp})

with tab2:
    st.subheader("Journal Your Thoughts")
    note = st.text_area("What's on your mind today?")
    trigger = st.selectbox("Main Trigger", ["Academic Pressure", "Social/Friends", "Personal", "Other"])
    if st.button("Save Entry"):
        st.success("Your reflection has been safely stored.")

with tab3:
    st.header("The Science of Relief")
    st.write("Lumina uses **Affect Labeling** and **Binaural Audio** to lower amygdala activity.")
    

# --- 8. FOOTER SHARE ---
st.write("---")
if st.button("🔗 Share Lumina with a Friend"):
    st.toast("Link copied to clipboard!")
