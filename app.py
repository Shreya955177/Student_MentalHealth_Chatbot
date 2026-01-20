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
    c.execute('''CREATE TABLE IF NOT EXISTS logs 
                 (date TEXT, mood TEXT, confidence REAL)''')
    conn.commit()
    conn.close()

def save_entry(mood, confidence):
    conn = sqlite3.connect('mood_tracker.db')
    c = conn.cursor()
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    c.execute("INSERT INTO logs VALUES (?, ?, ?)", (date_str, mood, confidence))
    conn.commit()
    conn.close()

# --- 2. AI MODEL LOADING ---
@st.cache_resource
def load_model():
    # This model detects: joy, sadness, anger, fear, love, surprise
    return pipeline("text-classification", model="bhadresh-savani/distilbert-base-uncased-emotion")

classifier = load_model()

# --- 3. INTERACTIVE BREATHING TOOL ---
def breathing_exercise():
    st.write("---")
    st.write("### 🫁 Guided Box Breathing")
    st.info("Follow the bar: Inhale -> Hold -> Exhale -> Hold")
    
    status = st.empty()
    progress_bar = st.progress(0)
    
    for _ in range(2):  # 2 Cycles
        # Inhale
        for i in range(101):
            time.sleep(0.04)
            progress_bar.progress(i)
            status.subheader("🟢 Inhale... (4s)")
        time.sleep(1) # Brief pause
        
        # Hold
        status.subheader("🟡 Hold... (4s)")
        time.sleep(4)
        
        # Exhale
        for i in range(100, -1, -1):
            time.sleep(0.04)
            progress_bar.progress(i)
            status.subheader("🔵 Exhale... (4s)")
            
        # Hold
        status.subheader("🟡 Hold... (4s)")
        time.sleep(4)
    status.success("✅ Feeling a bit calmer? You're doing great.")

# --- 4. APP INTERFACE ---
st.set_page_config(page_title="Lumina Companion", page_icon="🌱")
init_db()

# Sidebar for History & Safety
with st.sidebar:
    st.title("📊 Mood History")
    try:
        conn = sqlite3.connect('mood_tracker.db')
        df = pd.read_sql_query("SELECT * FROM logs ORDER BY date DESC LIMIT 10", conn)
        if not df.empty:
            st.bar_chart(df['mood'].value_counts())
        else:
            st.write("Start chatting to see your mood history!")
        conn.close()
    except:
        st.write("History will appear here.")
    
    st.divider()
    st.title("🆘 Crisis Help")
    st.error("Emergency: Call 911 / 988")
    st.info("Text HOME to 741741")

st.title("🌱 Lumina")
st.markdown("*A safe space for students to vent, breathe, and track well-being.*")

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("How are you feeling today?"):
    # Show User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # A. Safety Check
    crisis_keywords = ["kill", "suicide", "hurt myself", "end it all"]
    if any(word in prompt.lower() for word in crisis_keywords):
        response = "🚨 **I'm very concerned about you.** Please reach out for help. You are not alone. Call 988 or text 741741 immediately."
    else:
        # B. AI Sentiment Analysis
        results = classifier(prompt)
        label = results[0]['label']
        score = results[0]['score']
        
        # Save to DB
        save_entry(label, score)

        # C. Response Mapping
        responses = {
            "fear": "It sounds like anxiety is weighing on you. Let's try to ground ourselves.",
            "sadness": "I'm sorry you're feeling down. Remember that it's okay to not be okay today.",
            "anger": "It's completely valid to feel frustrated. Let's find a way to release that tension.",
            "joy": "I love hearing that! What's the best part of your day so far?",
            "surprise": "That sounds like a lot to process at once!",
            "love": "That’s such a beautiful and positive feeling."
        }
        
        main_resp = responses.get(label, "Thank you for sharing that with me. I'm listening.")
        response = f"**Lumina detected: {label.capitalize()}**\n\n{main_resp}"

    # Show Assistant Message
    with st.chat_message("assistant"):
        st.markdown(response)
        if not any(word in prompt.lower() for word in crisis_keywords) and label in ["fear", "anger", "sadness"]:
            if st.button("Start 2-Min Breathing Exercise"):
                breathing_exercise()
    
    st.session_state.messages.append({"role": "assistant", "content": response})
