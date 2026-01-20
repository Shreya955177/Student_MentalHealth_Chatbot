import streamlit as st
from transformers import pipeline
import sqlite3
from datetime import datetime
import pandas as pd
import time

# --- 1. DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('mood_tracker.db')
    c = conn.cursor()
    # Table for simple mood tracking
    c.execute('''CREATE TABLE IF NOT EXISTS logs 
                 (date TEXT, mood TEXT, confidence REAL)''')
    # Table for advanced journaling
    c.execute('''CREATE TABLE IF NOT EXISTS journal 
                 (date TEXT, note TEXT, trigger TEXT)''')
    conn.commit()
    conn.close()

def save_mood(mood, confidence):
    conn = sqlite3.connect('mood_tracker.db')
    c = conn.cursor()
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    c.execute("INSERT INTO logs VALUES (?, ?, ?)", (date_str, mood, confidence))
    conn.commit()
    conn.close()

def save_journal(note, trigger):
    conn = sqlite3.connect('mood_tracker.db')
    c = conn.cursor()
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    c.execute("INSERT INTO journal VALUES (?, ?, ?)", (date_str, note, trigger))
    conn.commit()
    conn.close()

# --- 2. AI MODEL LOADING ---
@st.cache_resource
def load_model():
    return pipeline("text-classification", model="bhadresh-savani/distilbert-base-uncased-emotion")

classifier = load_model()

# --- 3. COMPONENT FUNCTIONS ---

def show_sos_dashboard():
    with st.expander("🚨 EMERGENCY SOS DASHBOARD", expanded=False):
        st.error("If you are in immediate danger, please use these resources.")
        col1, col2 = st.columns(2)
        with col1:
            st.link_button("📞 Call Crisis Line (988)", "tel:988")
            st.link_button("🏫 Campus Security", "https://google.com")
        with col2:
            st.link_button("💬 Crisis Text Line", "sms:741741")
            st.link_button("🏥 Local Hospital", "https://maps.google.com")

def breathing_pacer():
    st.info("Let's do two rounds of Box Breathing (4-4-4-4).")
    status = st.empty()
    bar = st.progress(0)
    for r in range(1, 3):
        # Inhale
        for i in range(101):
            time.sleep(0.04)
            bar.progress(i)
            status.subheader(f"Round {r}: 🟢 Inhale... (4s)")
        # Hold
        status.subheader(f"Round {r}: 🟡 Hold... (4s)")
        time.sleep(4)
        # Exhale
        for i in range(100, -1, -1):
            time.sleep(0.04)
            bar.progress(i)
            status.subheader(f"Round {r}: 🔵 Exhale... (4s)")
        # Hold
        status.subheader(f"Round {r}: 🟡 Hold... (4s)")
        time.sleep(4)
    status.success("Great job. Take a moment to notice how your body feels.")

def pomodoro_sidebar():
    st.sidebar.divider()
    st.sidebar.subheader("⏳ Study Timer")
    mode = st.sidebar.radio("Mode", ["Focus (25m)", "Break (5m)"])
    if st.sidebar.button("Start Timer"):
        duration = 25 * 60 if "Focus" in mode else 5 * 60
        t_text = st.sidebar.empty()
        while duration > 0:
            m, s = divmod(duration, 60)
            t_text.metric("Remaining", f"{m:02d}:{s:02d}")
            time.sleep(1)
            duration -= 1
        st.sidebar.success("Time's up!")
        st.balloons()

# --- 4. MAIN APP LAYOUT ---
st.set_page_config(page_title="Lumina Companion", page_icon="🌱")
init_db()

# Sidebar History
with st.sidebar:
    st.title("📊 Mood Trends")
    try:
        conn = sqlite3.connect('mood_tracker.db')
        df = pd.read_sql_query("SELECT mood FROM logs", conn)
        if not df.empty:
            st.bar_chart(df['mood'].value_counts())
        conn.close()
    except:
        st.write("No history yet.")
    pomodoro_sidebar()

# Welcome Message
if "first_visit" not in st.session_state:
    st.session_state.first_visit = True

if st.session_state.first_visit:
    st.toast("Welcome to Lumina. I'm glad you're here. 👋")
    st.info("""
    ### Welcome to Lumina 🌱
    Your safe, anonymous space to vent, breathe, and focus. 
    **How are you really feeling today?**
    """)
    st.session_state.first_visit = False

# Tabs for Organization
tab1, tab2, tab3 = st.tabs(["💬 Chat & Support", "📝 Journal", "🔬 The Science"])

with tab1:
    show_sos_dashboard()
    
    # Chat Logic
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Tell me what's on your mind..."):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Safety Check
        crisis_words = ["suicide", "kill", "hurt myself", "end it"]
        if any(w in prompt.lower() for w in crisis_words):
            resp = "🚨 **I'm worried about you.** Please use the SOS dashboard at the top or call 988 immediately."
        else:
            # AI Sentiment
            pred = classifier(prompt)[0]
            label = pred['label']
            save_mood(label, pred['score'])
            
            responses = {
                "fear": "Anxiety can feel like a heavy weight. I'm here with you.",
                "sadness": "It's okay to feel down. Healing isn't a straight line.",
                "anger": "Frustration is natural. Let's find a way to breathe through it.",
                "joy": "That's wonderful! I'm so happy for you.",
                "love": "What a beautiful, positive feeling!",
                "surprise": "Sounds like an eventful day!"
            }
            resp = f"**Lumina detected: {label.capitalize()}**\n\n{responses.get(label, 'I hear you.')}"

        with st.chat_message("assistant"):
            st.markdown(resp)
            if not any(w in prompt.lower() for w in crisis_words) and label in ["fear", "anger", "sadness"]:
                if st.button("Start Breathing Pacer"):
                    breathing_pacer()
        st.session_state.messages.append({"role": "assistant", "content": resp})

with tab2:
    st.subheader("📝 Advanced Journaling")
    with st.form("j_form"):
        note = st.text_area("Write freely here...")
        trig = st.selectbox("Likely Trigger:", ["Academics", "Social", "Family", "Health", "Other"])
        if st.form_submit_button("Save Entry"):
            save_journal(note, trig)
            st.success("Reflecting helps clear the mind. Entry saved.")

with tab3:
    st.header("Why Lumina Works")
    st.write("**Box Breathing:** Stimulates the Vagus Nerve to lower your heart rate.")
    
    st.write("**Labeling Emotions:** Reduces activity in the Amygdala (the brain's fear center).")
    st.write("**Pomodoro:** Reduces task-based anxiety by breaking down cognitive load.")
