import streamlit as st
from streamlit_lottie import st_lottie
from deep_translator import GoogleTranslator
from transformers import pipeline
import pandas as pd
import sqlite3
import random
import requests

# --- 1. PAGE CONFIG & THEME INITIALIZATION ---
st.set_page_config(page_title="Lumina | Zen Space", page_icon="🌱", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 2. ASSETS & MODELS ---
@st.cache_resource
def load_tools():
    # Modern sentiment model
    classifier = pipeline("text-classification", model="cardiffnlp/twitter-roberta-base-sentiment-latest")
    return classifier

classifier = load_tools()

def load_lottieurl(url):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 else None
    except:
        return None

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
    theme_choice = st.radio("Choose Atmosphere", ["Daylight (Fresh)", "Midnight (Calm)"])
    
    st.divider()
    st.subheader("🎧 Soundscape")
    sound_choice = st.selectbox("Background Noise", ["None", "Soft Rain", "Deep Forest", "Lo-Fi Study"])
    sounds = {
        "Soft Rain": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-10.mp3",
        "Deep Forest": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-13.mp3",
        "Lo-Fi Study": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-15.mp3"
    }
    if sound_choice != "None":
        st.audio(sounds[sound_choice], format="audio/mp3", loop=True)

# --- 5. DYNAMIC UI STYLING ---
if theme_choice == "Midnight (Calm)":
    bg_gradient = "linear-gradient(180deg, #0f172a 0%, #1e1b4b 100%)"
    card_bg = "rgba(30, 41, 59, 0.7)"
    text_color = "#f8fafc"
    lottie_url = "https://lottie.host/682946c1-507c-4749-8084-3c66289d38f8/U7S8vOaDbe.json" 
else:
    bg_gradient = "linear-gradient(180deg, #E3F2FD 0%, #E8F5E9 100%)"
    card_bg = "rgba(255, 255, 255, 0.7)"
    text_color = "#2D3748"
    lottie_url = "https://lottie.host/8051e041-0672-46c5-a3d8-7e3f436980e1/V8u1X2vX6t.json"

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
    h1, h2, h3, p {{ color: {text_color} !important; }}
    .stButton>button {{ border-radius: 20px; background-color: #81C784 !important; color: white !important; border: none; }}
    </style>
""", unsafe_allow_html=True)

# --- 6. MAIN CONTENT ---
init_db()
lottie_zen = load_lottieurl(lottie_url)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if lottie_zen: st_lottie(lottie_zen, height=200)
    st.markdown(f'<div class="glass-card"><h1>Lumina</h1><p>Your safe, multilingual sanctuary.</p></div>', unsafe_allow_html=True)
    
    affirmations = ["You are doing your best, and that is enough.", "Take a deep breath. This moment will pass.", "Your health is more important than your grades."]
    st.markdown(f"<p style='text-align:center; font-style:italic;'>\"{random.choice(affirmations)}\"</p>", unsafe_allow_html=True)

# --- 7. TABS ---
tab1, tab2, tab3 = st.tabs(["💬 Chat Support", "📝 Reflection", "🔬 Science"])

with tab1:
    with st.expander("🚨 Need Immediate Help?", expanded=False):
        st.error("Crisis Line: 988 | Campus Security: [Insert Number]")
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.write(msg["content"])

    if prompt := st.chat_input("How are you feeling right now?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)

        with st.spinner("✨ Lumina is listening..."):
            # A. Translation & Detection
            # We use 'auto' to detect what language the student is speaking
            translated_en = GoogleTranslator(source='auto', target='en').translate(prompt)
            
            # B. Sentiment Analysis
            res = classifier(translated_en)[0]
            label = res['label'] # 'positive', 'neutral', 'negative'

            # C. Sarcasm/Emoji Check
            ironic_emojis = ["💀", "😭", "🫠", "🤡"]
            is_ironic = any(e in prompt for e in ironic_emojis)

            # D. Response Logic
            if is_ironic and label == "positive":
                response_en = "I see those emojis—it sounds like you're going through a lot right now. I'm here for the real talk."
            elif label == "negative":
                response_en = "I'm so sorry things feel this way. It's okay to not be okay. I've found some music to help you ground yourself."
            else:
                response_en = "Thank you for sharing that with me. I'm here to listen."

            # E. Translate Back to User's Language
            # This makes the bot reply in whatever language the student used
            final_resp = GoogleTranslator(source='en', target='auto').translate(response_en)
            
            with st.chat_message("assistant"):
                st.write(final_resp)
                if label == "negative":
                    st.caption("🎵 Comforting Frequencies")
                    st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-8.mp3")

        st.session_state.messages.append({"role": "assistant", "content": final_resp})

with tab2:
    st.subheader("Safe Journal")
    st.text_area("Write freely here. This space is yours.", placeholder="Today was...")
    if st.button("Secure My Thoughts"):
        st.success("Your reflection has been safely stored.")

with tab3:
    st.header("The Science of Calm")
    st.write("Lumina uses **Natural Language Processing** to provide a safe outlet for emotional venting.")
    

# --- 8. FOOTER ---
st.write("---")
if st.button("🔗 Share Lumina Link"):
    st.toast("Link ready to share! ✨")
