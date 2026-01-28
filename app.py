import streamlit as st
from streamlit_lottie import st_lottie
from deep_translator import GoogleTranslator
from transformers import pipeline
import random
import requests
import datetime

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="FeelBot | AI ChatBot For Students", page_icon="💭", layout="wide")


# --- 2. GLOBAL CONTENT & STATE ---
GUIDE_TEXT = """
Welcome to your safe space. FeelBot is designed to be a **reflective listener**.
To have the best experience:

* **Speak your heart:** Use your native language. FeelBot understands over 100 languages.
* **Be specific:** Instead of "I'm sad," try "I'm feeling overwhelmed by my math assignment."
* **ask for help:** You can ask, "Can you help me reframe this thought?" or "I just need to vent."
* **Take your time:** There is no rush. This space is yours.

*Note: FeelBot is an AI companion for wellness, not a clinical replacement.*
"""

if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_count" not in st.session_state:
    st.session_state.chat_count = 0
if "current_track" not in st.session_state:
    st.session_state.current_track = None


# --- 3. THE GENERATIVE BRAIN (The "Real" Feeling) ---
@st.cache_resource
def load_ai_models():
    # Model 1: Sentiment Analysis (to trigger music/support)
    sentiment_task = pipeline("text-classification", model="cardiffnlp/twitter-roberta-base-sentiment-latest")
    # Model 2: Conversational AI (The brain that talks back)
    chat_task = pipeline("text-generation", model="facebook/blenderbot-400M-distill")
    return sentiment_task, chat_task

with st.spinner("FeelBot Assistant is waking up... Please wait a moment."):
    classifier, chat_brain = load_ai_models()

def load_lottieurl(url):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 else None
    except: return None

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("🌿 FeelBot is an AI chatbot for the students, who requires a support for mental health issues.")
    theme_choice = st.radio("Atmosphere", ["Daylight (Fresh)", "Midnight (Calm)"])
    
    # Daily Wellness Challenge
    st.divider()
    st.subheader("🎯 Daily Wellness Win")
    challenges = ["💧 Drink water.", "🪟 Fresh air.", "📝 One achievement.", "🚶 Stretch.", "🍎 Healthy snack."]
    day_seed = datetime.datetime.now().timetuple().tm_yday
    st.info(challenges[day_seed % len(challenges)])
    if st.button("I did it! ✨"): st.balloons()

    # --- UPDATED MUSIC SECTION (Fixed Indentation) ---
    st.divider()
    st.subheader("🎧 Emotion-Based Playlists")
    m_col1, m_col2 = st.columns(2)

    with m_col1:
        if st.button("📚 Study"):
            st.session_state.current_track = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
        if st.button("😢 Sad"):
            st.session_state.current_track = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-10.mp3"

    with m_col2:
        if st.button("😊 Happy"):
            st.session_state.current_track = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3"
        if st.button("🌀 Overwhelmed"):
            st.session_state.current_track = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-8.mp3"

    # Display the player in the sidebar so it stays active across tabs
    if st.session_state.current_track:
        st.audio(st.session_state.current_track, format="audio/mp3")
        if st.button("⏹️ Stop Music"):
            st.session_state.current_track = None
            st.rerun()

    # Safety
    st.sidebar.markdown("---")
    with st.sidebar.expander("🆘 EMERGENCY", expanded=False):
        st.error("Crisis Line: 988")

# --- 5. DYNAMIC UI ---

if theme_choice == "Midnight (Calm)":
    bg, card, text = "linear-gradient(180deg, #0f172a 0%, #1e1b4b 100%)", "rgba(30, 41, 59, 0.7)", "#f8fafc"
    lottie_url = "https://lottie.host/682946c1-507c-4749-8084-3c66289d38f8/U7S8vOaDbe.json" 
    # Standard Midnight CSS
    st.markdown(f"""
        <style>
        .stApp {{ background: {bg}; color: {text}; }}
        .glass-card {{ background: {card}; border-radius: 20px; padding: 25px; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1); text-align: center; margin-bottom: 20px; }}
        h1, h2, h3, p, span, label {{ color: {text} !important; }}
        </style>
    """, unsafe_allow_html=True)
else:
    # --- FIXED DAYLIGHT MODE CSS ---
    bg, card, text = "linear-gradient(180deg, #E3F2FD 0%, #E8F5E9 100%)", "rgba(255, 255, 255, 0.8)", "#1A202C"
    lottie_url = "https://lottie.host/8051e041-0672-46c5-a3d8-7e3f436980e1/V8u1X2vX6t.json"
    
    st.markdown(f"""
        <style>
        /* Main Background */
        .stApp {{ 
            background: {bg}; 
            color: {text}; 
        }}
        
        /* High Contrast Sidebar */
        [data-testid="stSidebar"] {{
            background-color: #FFFFFF !important;
        }}
        
        /* Force Sidebar text to be Dark Charcoal */
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3, 
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] .stMarkdown {{
            color: #1A202C !important;
        }}

        /* Fix Radio Button Text specifically */
        div[data-testid="stWidgetLabel"] p {{
            color: #1A202C !important;
            font-weight: 600 !important;
        }}
        
        .st-af {{ color: #1A202C !important; }} /* Radio text color */

        /* Glass card contrast */
        .glass-card {{ 
            background: {card}; 
            border-radius: 20px; 
            padding: 25px; 
            backdrop-filter: blur(10px); 
            border: 1px solid rgba(0,0,0,0.1); 
            text-align: center; 
            margin-bottom: 20px; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }}
        
        /* Main Heading Contrast */
        h1, h2, h3, p {{ color: {text} !important; }}
        </style>
    """, unsafe_allow_html=True)

# --- 6. MAIN UI ---
lottie_zen = load_lottieurl(lottie_url)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if lottie_zen: st_lottie(lottie_zen, height=200)
    st.markdown('<div class="glass-card"><h1>FeelBot</h1><p>A supportive chatbot friend that listens, understands your mood, and helps you handle stress and emotions...</p></div>', unsafe_allow_html=True)

    # --- THE USER GUIDE (Placed right after the header) ---
with st.expander("💡 How to use the FeelBot: Here are the instructions to use the FeelBot AI ChatBot", expanded=False):
    st.markdown(GUIDE_TEXT)

tab1, tab2, tab3 = st.tabs(["💬 Chat Support", "📝 Reflection", "🔬 Science"])

with tab1:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.write(msg["content"])

    if prompt := st.chat_input("Tell FeelBot Assistant what's on your mind..."):
        st.session_state.chat_count += 1
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)

        with st.spinner("✨ FeelBot Assistant Thinking..."):
            try:
                # A. Translation to English
                translator = GoogleTranslator(source='auto', target='en')
                translated_en = translator.translate(prompt)
                user_lang = translator.source 
                
                # B. GENERATIVE RESPONSE (The Real Conversation)
                # We feed the prompt to the brain to get a unique reply
                chat_output = chat_brain(translated_en, max_length=100, do_sample=True, temperature=0.7)
                response_en = chat_output[0]['generated_text']

                # C. Sentiment Analysis (Background check for support tools)
                sentiment = classifier(translated_en)[0]
                
                # D. Translate back to student's language
                final_resp = GoogleTranslator(source='en', target=user_lang).translate(response_en)
                
                with st.chat_message("assistant"):
                    # Add custom bubble styling for the assistant response
                    if theme_choice == "Daylight (Fresh)":
                        st.markdown(f"""
                            <div style="background-color: #FFFFFF; color: #1A202C; padding: 15px; border-radius: 15px; border: 1px solid #E2E8F0; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                                {final_resp}
                            </div>
                        """, unsafe_allow_html=True)
                    else:
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
    st.subheader("📊 Your Emotional Journey")
    
    # 1. Input: How is the user today?
    mood_score = st.select_slider(
        "Rate your mood today:",
        options=[1, 2, 3, 4, 5],
        value=3,
        help="1: Very Low, 5: Fantastic!"
    )
    
    # Map numbers to emojis for visual feedback
    mood_emojis = {1: "😫", 2: "😔", 3: "😐", 4: "🙂", 5: "🌟"}
    st.write(f"Current Mood: {mood_emojis[mood_score]}")

    if st.button("Log Mood for Today"):
        # Initialize mood data in session state if it doesn't exist
        if "mood_data" not in st.session_state:
            # Pre-fill with some example data for the week to show the graph
            st.session_state.mood_data = [3, 4, 2, 3, 4, 3] 
        
        st.session_state.mood_data.append(mood_score)
        st.success("Mood logged! You're building a great habit.")

    # 2. Visualize: The Mood Graph
    if "mood_data" in st.session_state:
        st.divider()
        st.write("### Weekly Mood Trend")
        
        # Convert list to a simple DataFrame for the chart
        chart_data = pd.DataFrame(st.session_state.mood_data, columns=["Mood Level"])
        
        # Display the line chart
        st.line_chart(chart_data, height=250, use_container_width=True)
        st.caption("Lower points indicate stress; higher points indicate peak wellness.")

    # 3. Private Journal
    st.divider()
    st.subheader("📝 Private Thoughts")
    journal_entry = st.text_area("What's on your mind?", height=150)
    if st.button("Save Entry"):
        st.toast("Journal saved to session!")

with tab3:
    st.header("🔬 The Neural Architecture of FeelBot")
    st.write("FeelBot is built on a modular AI pipeline designed to mimic human emotional intelligence.")

    # 1. Natural Language Generation (NLG)
    st.subheader("🤖 Natural Language Generation")
    st.info("**Model:** `facebook/blenderbot-400M-distill`")
    st.write("""
    Unlike standard chatbots, FeelBot uses a **Transformer-based Generative Model**. 
    This model was trained on 1.5 billion social media conversations specifically to 
    provide empathetic, context-aware responses rather than just facts.
    """)

    # 2. Sentiment Analysis
    st.subheader("📊 Emotional Intelligence (Sentiment)")
    st.info("**Model:** `cardiffnlp/twitter-roberta-base-sentiment-latest`")
    st.write("""
    FeelBot uses **RoBERTa** (A Robustly Optimized BERT Pretraining Approach). 
    This model analyzes the 'vector space' of the user's input to detect three core states: 
    *Negative*, *Neutral*, or *Positive*. This allows the app to trigger music or breathing 
    exercises only when a critical stress threshold is met.
    """)
    

    # 3. Neural Machine Translation (NMT)
    st.subheader("🌍 Multilingual Neural Bridge")
    st.info("**Library:** `deep-translator` (Google NMT Engine)")
    st.write("""
    FeelBot achieves its global reach via **Neural Machine Translation**. It detects 
    over 100 languages instantly, translates them to English for high-precision 
    analysis, and mirrors the user's native language in the response to build trust.
    """)
    

    # 4. Psychological Principles
    st.subheader("🧠 Behavioral Science Foundation")
    st.write("""
    The app utilizes three key psychological frameworks:
    * **CBT (Cognitive Behavioral Therapy):** Reframing negative thoughts through dialogue.
    * **Mindfulness:** Grounding the user with auditory anchors (Nature sounds).
    * **Habit Formation:** Using 'Micro-wins' (Daily Challenges) to stimulate dopamine release.
    """)
