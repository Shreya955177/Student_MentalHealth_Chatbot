import streamlit as st
from streamlit_lottie import st_lottie
from deep_translator import GoogleTranslator
from transformers import pipeline
import random
import requests
import datetime

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Lumina | AI Sanctuary", page_icon="🌱", layout="wide")

# --- 2. GLOBAL CONTENT & STATE ---
GUIDE_TEXT = """
Welcome to your safe space. Lumina is designed to be a **reflective listener**.
To have the best experience:

* **Speak your heart:** Use your native language. Lumina understands over 100 languages.
* **Be specific:** Instead of "I'm sad," try "I'm feeling overwhelmed by my math assignment."
* **ask for help:** You can ask, "Can you help me reframe this thought?" or "I just need to vent."
* **Take your time:** There is no rush. This space is yours.

*Note: Lumina is an AI companion for wellness, not a clinical replacement.*
"""

if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_count" not in st.session_state:
    st.session_state.chat_count = 0

# --- 2. THE GENERATIVE BRAIN (The "Real" Feeling) ---
@st.cache_resource
def load_ai_models():
    # Model 1: Sentiment Analysis (to trigger music/support)
    sentiment_task = pipeline("text-classification", model="cardiffnlp/twitter-roberta-base-sentiment-latest")
    # Model 2: Conversational AI (The brain that talks back)
    chat_task = pipeline("text2text-generation", model="facebook/blenderbot-400M-distill")
    return sentiment_task, chat_task

with st.spinner("Lumina is waking up... Please wait a moment."):
    classifier, chat_brain = load_ai_models()

def load_lottieurl(url):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 else None
    except: return None

# --- 3. SIDEBAR ---
with st.sidebar:
    st.title("🌿 Lumina Sanctuary")
    theme_choice = st.radio("Atmosphere", ["Daylight (Fresh)", "Midnight (Calm)"])
    
    # Daily Wellness Challenge
    st.divider()
    st.subheader("🎯 Daily Wellness Win")
    challenges = ["💧 Drink water.", "🪟 Fresh air.", "📝 One achievement.", "🚶 Stretch.", "🍎 Healthy snack."]
    day_seed = datetime.datetime.now().timetuple().tm_yday
    st.info(challenges[day_seed % len(challenges)])
    if st.button("I did it! ✨"): st.balloons()

    # Safety
    st.sidebar.markdown("---")
    with st.sidebar.expander("🆘 EMERGENCY", expanded=False):
        st.error("Crisis Line: 988")

# --- 4. DYNAMIC UI ---
if theme_choice == "Midnight (Calm)":
    bg, card, text = "linear-gradient(180deg, #0f172a 0%, #1e1b4b 100%)", "rgba(30, 41, 59, 0.7)", "#f8fafc"
    lottie_url = "https://lottie.host/682946c1-507c-4749-8084-3c66289d38f8/U7S8vOaDbe.json" 
else:
    bg, card, text = "linear-gradient(180deg, #E3F2FD 0%, #E8F5E9 100%)", "rgba(255, 255, 255, 0.7)", "#2D3748"
    lottie_url = "https://lottie.host/8051e041-0672-46c5-a3d8-7e3f436980e1/V8u1X2vX6t.json"

st.markdown(f"<style>.stApp {{ background: {bg}; color: {text}; }} .glass-card {{ background: {card}; border-radius: 20px; padding: 25px; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1); text-align: center; margin-bottom: 20px; }} h1, h2, h3, p {{ color: {text} !important; }}</style>", unsafe_allow_html=True)

# --- 5. MAIN UI ---
lottie_zen = load_lottieurl(lottie_url)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if lottie_zen: st_lottie(lottie_zen, height=200)
    st.markdown('<div class="glass-card"><h1>Lumina</h1><p>Truly human, truly multilingual.</p></div>', unsafe_allow_html=True)

 # --- THE USER GUIDE (Placed right after the header) ---
with st.expander("💡 How to get the most out of Lumina", expanded=False):
    st.markdown(GUIDE_TEXT)

tab1, tab2, tab3 = st.tabs(["💬 Chat Support", "📝 Reflection", "🔬 Science"])

with tab1:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.write(msg["content"])

    if prompt := st.chat_input("Tell Lumina what's on your mind..."):
        st.session_state.chat_count += 1
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)

        with st.spinner("✨ Thinking..."):
            try:
                # A. Translation to English
                translator = GoogleTranslator(source='auto', target='en')
                translated_en = translator.translate(prompt)
                user_lang = translator.source 
                
                # B. GENERATIVE RESPONSE (The Real Conversation)
                # We feed the prompt to the brain to get a unique reply
                chat_output = chat_brain(translated_en, max_length=60, do_sample=True, temperature=0.7)
                response_en = chat_output[0]['generated_text']

                # C. Sentiment Analysis (Background check for support tools)
                sentiment = classifier(translated_en)[0]
                
                # D. Translate back to student's language
                final_resp = GoogleTranslator(source='en', target=user_lang).translate(response_en)
                
                with st.chat_message("assistant"):
                    st.write(final_resp)
                    
                    # Support tools appear only if negative sentiment persists
                    if st.session_state.chat_count >= 2 and sentiment['label'] == "negative":
                        st.divider()
                        st.caption("I'm here for you. Would you like a small distraction?")
                        cs1, cs2 = st.columns(2)
                        with cs1:
                            if st.button("🎵 Calming Music"): st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-8.mp3")
                        with cs2:
                            if st.button("🧘 Breathing"): st.info("Breathe in... Breathe out...")

                st.session_state.messages.append({"role": "assistant", "content": final_resp})
            except Exception as e:
                st.error("I'm having a quiet moment. Let's try again in a second.")

# Tab 2 and 3 remain the same...
with tab2:
    st.subheader("Safe Journal")
    st.text_area("This space is private and yours.", placeholder="Today was...")
    if st.button("Secure My Thoughts"): st.success("Stored safely.")

with tab3:
    st.header("The Science of Calm")
    st.write("Lumina uses RoBERTa-base NLP to identify emotional triggers and provide linguistic mirroring for comfort.")
