import streamlit as st
import anthropic
import os
import json
import gspread
import random
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from google.oauth2.service_account import Credentials
from datetime import datetime
from markdown_pdf import MarkdownPdf, Section

# --- 1. Page Configuration ---
st.set_page_config(page_title="EMT-Predict & Pace", page_icon="⚡", layout="centered")

# --- 2. Databases for Randomization ---
em_images = [
    "https://images.unsplash.com/photo-1518770660439-4636190af475?q=80&w=600&auto=format&fit=crop", 
    "https://images.unsplash.com/photo-1581092334651-ddf26d9a09d0?q=80&w=600&auto=format&fit=crop", 
    "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?q=80&w=600&auto=format&fit=crop"
]

youtube_videos = [
    "https://www.youtube.com/watch?v=CQcfN21XrKI&list=PLPOivWONMRkcdSL5-ae1w1NTJqIWCwYW6", 
    "https://www.youtube.com/watch?v=acvNnQBC7mM&list=PLPOivWONMRkcdSL5-ae1w1NTJqIWCwYW6"
]

# --- 3. Sidebar Layout ---
fke_filename = "FKElogo.png"
if os.path.exists(fke_filename):
    st.sidebar.image(fke_filename, use_container_width=True)
else:
    st.sidebar.image("https://aims.uitm.edu.my/images/uitm_logo.png", use_container_width=True)

if os.path.exists("Logo.png"):
    st.sidebar.image("Logo.png", use_container_width=True)

st.sidebar.markdown("### ⚡ ESP\n**Electromagnetic Smart Planner**\n*UiTM ECM420 Tutor*")
st.sidebar.markdown("---")

st.sidebar.info("""
**💡 How to use this panel:**
* **Confidence Level:** Be honest! A lower score tells the AI to explain things more gently and thoroughly.
* **Days to Assessment:** This determines exactly how many days your custom Sprint Plan will cover.
""")

st.sidebar.subheader("Student Profile")
confidence = st.sidebar.slider("ECM420 Confidence (1-10)", 1, 10, 5)
days_remaining = st.sidebar.number_input("Days to Assessment", min_value=1, max_value=30, value=7)

# --- 4. Main Page Content ---
st.markdown("<h2 style='margin: 0; padding-bottom: 20px;'>⚡ ESP: Electromagnetic Smart Planner</h2>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image(random.choice(em_images), use_container_width=True, caption="Master the Forces of Nature ⚡")

st.markdown("### Welcome to your Personal AI Teaching Assistant! 🤖")
st.write("""
Electromagnetics Theory can be tough, but you don't have to study alone. I am here to help you navigate the ECM420 syllabus using three unique learning tools. 

*(Make sure you set your Profile in the left sidebar first! Mobile users: Tap the **`>`** arrow at the top left to open the menu).*
""")

# --- 5. Helper Functions ---
def get_gspread_client():
    creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS_JSON"])
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    return gspread.authorize(creds)

def log_to_sheets(conf_level, days, tool_used, student_input):
    try:
        if "GOOGLE_CREDENTIALS_JSON" in st.secrets:
            client = get_gspread_client()
            sheet = client.open("ECM420_Database").sheet1
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sheet.append_row([current_time, conf_level, days, tool_used, student_input])
    except Exception as e:
        print(f"Database Logging Error: {e}")

def create_pdf(markdown_text):
    pdf = MarkdownPdf(toc_level=2) 
    content = f"# ECM420 Study Plan\n\n{markdown_text}"
    pdf.add_section(Section(content))
    temp_filename = "temp_plan.pdf"
    pdf.save(temp_filename)
    with open(temp_filename, "rb") as f:
        pdf_bytes = f.read()
    os.remove(temp_filename)
    return pdf_bytes

shared_system_instructions = """
You are an empathetic, expert university professor teaching Electromagnetics Theory (course code ECM420) at UiTM. 
CRITICAL MATHEMATICAL NOTATION RULES:
- You MUST adopt the exact mathematical notation used in Matthew N.O. Sadiku's "Elements of Electromagnetics" and the UiTM ECM420 Appendix.
- DO NOT use standard LaTeX or dollar signs ($ or $$) as it will crash the app's PDF generator.
- Use Markdown bolding for vectors (e.g., **E**, **D**, **H**, **B**).
- For unit vectors, DO NOT USE UNDERSCORES. Use bold 'a' followed directly by the coordinate direction (e.g., **a**x, **a**y, **a**z; **a**ρ, **a**φ, **a**z; **a**r, **a**θ, **a**φ).
- For differential surface area, you MUST use 'dS' (capital S). DO NOT use 'da'.
- Use rich Unicode for Greek letters and operators (e.g., ∇, ∫, ∂, π, μ₀, ε₀, ∬).
"""

# --- 6. TABS INTERFACE ---
tab1, tab2, tab3, tab4 = st.tabs(["🚀 Sprint Plan", "🧠 Feynman Checker", "🌊 Analogy Engine", "🔒 Instructor Admin"])

# ==========================================
# TAB 1: SPRINT PLANNER 
# ==========================================
with tab1:
    st.info("**Tool 1: Sprint Plan** - Tell me what topic you are struggling with, and I will generate a custom study schedule.")
    student_struggle = st.text_area("Having trouble with Electromagnetics Theory? Tell me exactly what is confusing you:", height=100)
    if st.button("Generate My Sprint Plan 🚀"):
        if not student_struggle:
            st.warning("⚠️ Please describe what you are struggling with so I can help!")
        else:
            with st.spinner("Analyzing your learning gap with Claude AI..."):
                log_to_sheets(confidence, days_remaining, "Sprint Plan", student_struggle)
                try:
                    syllabus_data = "Syllabus not found. Please provide general electromagnetics advice."
                    if os.path.exists("syllabus.txt"):
                        with open("syllabus.txt", "r", encoding="utf-8") as file:
                            syllabus_data = file.read()

                    client = anthropic.Anthropic(api_key=st.secrets["CLAUDE_API_KEY"])
                    
                    user_message = f"""Syllabus:
{syllabus_data}

Student Confidence: {confidence}
Days to Assessment: {days_remaining}
Struggle: "{student_struggle}"
Provide:
1. Brief diagnosis.
2. A day-by-day table study schedule over {days_remaining} days (exactly 5 columns).
3. A mini-quiz at the end."""
                    
                    # BITE-SIZED FIX: Break the message array out
                    api_messages = [{"role": "user", "content": user_message}]
                    
                    response = client.messages.create
