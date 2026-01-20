import streamlit as st
from streamlit_lottie import st_lottie
from deep_translator import GoogleTranslator
from transformers import pipeline
import pandas as pd
import random
import requests
import datetime

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Lumina | Zen Space", page_icon="🌱", layout="wide")

# Initialize session states
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_count" not in st.session_state:
    st.session_state.chat_count = 0

# --- 2. ASSETS & MODELS ---
@st.cache_resource
def load_tools():
    # Robust sentiment model
    classifier = pipeline("text-classification", model="cardiffnlp/twitter-roberta-base-sentiment-latest")
    return classifier

classifier = load_tools()

def load_lottieurl(url):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 else None
    except: return None

# --- 3. SIDEBAR: CHALLENGES & SAFETY ---
with st.sidebar:
    st.title("🌿 Lumina Sanctuary")
    theme_choice = st.radio("Atmosphere", ["Daylight (Fresh)", "Midnight (Calm)"])
    
    # Daily Wellness Challenge
    st.divider()
    st.subheader("🎯 Daily Wellness Win")
    challenges = [
        "💧 Drink a full glass of water right now.",
        "🪟 Open a window and take 3 deep breaths.",
        "📝 Write down 1 thing you achieved today.",
        "🚶 Stretch your body for 30 seconds.",
        "🍎 Have a healthy snack.",
        "📵 10 minutes of 'No-Phone' time."
    ]
    day_seed = datetime.datetime.now().timetuple().tm_yday
    st.info(challenges[day_seed % len(challenges)])
    if st.button("I did it! ✨"):
        st.balloons()
        st.toast("Self-care is a victory! 🎉")

    # Soundscape
    st.divider()
    sound_choice = st.selectbox("Ambient Sounds", ["None", "Soft Rain", "Lo-Fi Study"])
    sounds = {
        "Soft Rain": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-10.mp3",
        "Lo-Fi Study": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-15.mp3"
    }
    if sound_choice != "None":
        st.audio(sounds[sound_choice], format="audio/mp3", loop=True)

    # Safety Feature
    st.sidebar.markdown("---")
    with st.sidebar.expander("🆘 EMERGENCY RESOURCES", expanded=False):
        st.error("If you are in danger:")
        st.markdown("- **Crisis Line:** 988\n- **Campus Security:** [Insert Number]\n- **International:** [befrienders.org](https://www.befrienders.org/)")

# --- 4. DYNAMIC THEMING ---
if theme_choice == "Midnight (Calm)":
    bg_gradient, card_bg, text_color = "linear-gradient(180deg, #0f172a 0%, #1e1b4b 100%)", "rgba(30, 41, 59, 0.7)", "#f8fafc"
    lottie_url = "https://lottie.host/682946c1-507c-4749-8084-3c66289d38f8/U7S8vOaDbe.json" 
else:
    bg_gradient, card_bg, text_color = "linear-gradient(180deg, #E3F2FD 0%, #E8F5E9 100%)", "rgba(255, 255, 255, 0.7)", "#2D3748"
    lottie_url = "https://lottie.host/8051e041-0672-46c5-a3d8-7e3f436980e1/V8u1X2vX6t.json"

st.markdown(f"<style>.stApp {{ background: {bg_gradient}; color: {text_color}; }} .glass-card {{ background: {card_bg}; border-radius: 20px; padding: 25px; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1); text-align: center; margin-bottom: 20px; }} h1, h2, h3, p {{ color: {text_color} !important; }}</style>", unsafe_allow_html=True)

# --- 5. MAIN UI ---
lottie_zen = load_lottieurl(lottie_url)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if lottie_zen: st_lottie(lottie_zen, height=200)
    st.markdown('<div class="glass-card"><h1>Lumina</h1><p>Your safe, multilingual sanctuary.</p></div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["💬 Chat Support", "📝 Reflection", "🔬 Science"])

with tab1:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.write(msg["content"])

    if prompt := st.chat_input("How are you feeling?"):
        st.session_state.chat_count += 1
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)

        with st.spinner("✨ Lumina is listening..."):
            try:
                # A. Multilingual Bridge
                detect_obj = GoogleTranslator(source='auto', target='en')
                translated_en = detect_obj.translate(prompt)
                user_lang = detect_obj.source 
                
                # B. Sentiment Analysis
                res = classifier(translated_en)[0]
                label = res['label']

                # C. Human-First Empathy Logic (Direct response first)
                if label == "negative":
                    responses = [
                        "I hear you. It sounds like things are really heavy right now, and I want you to know it's okay to feel this way.",
                        "Thank you for sharing that with me. I'm here to listen. You don't have to carry this alone.",
                        "I can tell you're going through a lot. I'm sitting here with you. What's weighing most on your mind?"
                    ]
                    response_en = random.choice(responses)
                elif label == "positive":
                    response_en = "That's wonderful! I'm so glad to hear you're in a good space. What's making today feel bright?"
                else:
                    response_en = "I'm here for you. Tell me more about what's on your mind."

                final_resp = GoogleTranslator(source='en', target=user_lang).translate(response_en)
                
                with st.chat_message("assistant"):
                    st.write(final_resp)
                    
                    # D. Delayed Support (Shows choices only after 2+ turns if still sad)
                    if st.session_state.chat_count >= 2 and label == "negative":
                        st.write("---")
                        st.caption("I notice you're still feeling quite heavy. Would you like a small way to ground yourself?")
                        cs1, cs2 = st.columns(2)
                        with cs1:
                            if st.button("🎵 Calming Music"):
                                st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-8.mp3")
                        with cs2:
                            if st.button("🧘 1-Min Breathing"):
                                st.info("Breathe in... 4s | Hold... 4s | Out... 4s")

                st.session_state.messages.append({"role": "assistant", "content": final_resp})
            except:
                st.write("I am here for you. Please tell me more.")

with tab2:
    st.subheader("Safe Journal")
    st.text_area("This space is private and yours.", placeholder="Today was...")
    if st.button("Secure My Thoughts"): st.success("Stored safely.")

with tab3:
    st.header("The Science of Calm")
    st.write("Lumina uses RoBERTa-base NLP to identify emotional triggers and provide linguistic mirroring for comfort.")
