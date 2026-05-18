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
                    user_message = f"Syllabus:\n{syllabus_data}\n\nStudent Confidence: {confidence}\nDays to Assessment: {days_remaining}\nStruggle: \"{student_struggle}\"\nProvide:\n1. Brief diagnosis.\n2. A day-by-day table study schedule over {days_remaining} days (exactly 5 columns).\n3. A mini-quiz at the end."
                    
                    response = client.messages.create(
                        model="claude-haiku-4-5-20251001",
                        max_tokens=2000,
                        system=shared_system_instructions + "\n- MUST output a study schedule as a Markdown table with exactly 5 columns. Keep it simple.",
                        messages=[{"role": "user", "content": user_message}]
                    )
                    
                    response_text = response.content[0].text
                    if response_text:
                        st.success("Plan Generated Successfully!")
                        st.markdown(response_text)
                        st.markdown("---")
                        st.subheader("📺 Recommended Dr. Aziati Lecture Materials")
                        st.write("👉 **Action Required:** Based on your generated study plan above, please click the **Playlist Menu icon (三)** in the top right corner of the video player below. Scroll through and select the exact lecture material that matches your current topic!")
                        st.video(random.choice(youtube_videos))
                        st.markdown("---")
                        
                        clean_md = response_text.replace("\n||\n", "\n|---|---|---|---|---|\n").replace("\n| |\n", "\n|---|---|---|---|---|\n")
                        try:
                            pdf_bytes = create_pdf(clean_md)
                            st.download_button(label="📥 Download Plan as PDF", data=pdf_bytes, file_name="ECM420_Study_Plan.pdf", mime="application/pdf")
                        except Exception as pdf_error:
                             st.error("⚠️ PDF conversion failed, but you can copy the text above.")
                except Exception as e:
                    st.error(f"An error occurred: {e}")

# ==========================================
# TAB 2: FEYNMAN CONCEPT CHECKER
# ==========================================
with tab2:
    st.info("**Tool 2: Feynman Checker** - Explain an ECM420 concept in your own words below, and I will grade your understanding!")
    student_explanation = st.text_area("Explain a concept to me (e.g., How does Gauss's Law work?):", height=150)
    if st.button("Check My Understanding 🧠"):
        if not student_explanation:
            st.warning("⚠️ Please type your explanation first!")
        else:
            with st.spinner("Reviewing your explanation like a strict but fair professor..."):
                log_to_sheets(confidence, days_remaining, "Feynman Checker", student_explanation)
                try:
                    client = anthropic.Anthropic(api_key=st.secrets["CLAUDE_API_KEY"])
                    feynman_prompt = f"The student has provided the following explanation of an Electromagnetics concept:\n\"{student_explanation}\"\nTask:\n1. Point out exactly what they got right.\n2. Gently correct any misconceptions.\n3. Give them a 'Comprehension Score' out of 10."
                    
                    response = client.messages.create(
                        model="claude-haiku-4-5-20251001",
                        max_tokens=1000,
                        system=shared_system_instructions,
                        messages=[{"role": "user", "content": feynman_prompt}]
                    )
                    st.success("Review Complete!")
                    st.markdown(response.content[0].text)
                except Exception as e:
                    st.error(f"An error occurred: {e}")

# ==========================================
# TAB 3: REAL-WORLD ANALOGY ENGINE
# ==========================================
with tab3:
    st.info("**Tool 3: Analogy Engine** - Tell me what formula or concept you are stuck on, and I will explain it using a real-world physical analogy.")
    analogy_topic = st.text_input("What concept is confusing you? (e.g., Divergence, Magnetic Flux)")
    if st.button("Give Me an Analogy 🌍"):
        if not analogy_topic:
            st.warning("⚠️ Please enter a topic!")
        else:
            with st.spinner("Brewing up a real-world analogy..."):
                log_to_sheets(confidence, days_remaining, "Analogy Engine", analogy_topic)
                try:
                    client = anthropic.Anthropic(api_key=st.secrets["CLAUDE_API_KEY"])
                    analogy_prompt = f"The student is struggling to intuitively understand this concept: \"{analogy_topic}\".\nTask:\n1. Explain this using a highly vivid, real-world physical analogy.\n2. Map the variables directly to the analogy.\n3. Keep it encouraging."
                    
                    response = client.messages.create(
                        model="claude-haiku-4-5-20251001",
                        max_tokens=1000,
                        system=shared_system_instructions,
                        messages=[{"role": "user", "content": analogy_prompt}]
                    )
                    st.success("Analogy Generated!")
                    st.markdown(response.content[0].text)
                except Exception as e:
                    st.error(f"An error occurred: {e}")

# ==========================================
# TAB 4: INSTRUCTOR ADMIN DASHBOARD
# ==========================================
with tab4:
    st.markdown("### 🔒 Instructor Analytics Dashboard")
    st.write("Enter the admin password to view real-time class analytics.")
    
    admin_password = st.text_input("Password", type="password")
    correct_password = st.secrets.get("ADMIN_PASSWORD", "default_fallback_password")

    if st.button("Login"):
        if admin_password == correct_password:
            st.session_state["admin_logged_in"] = True
            st.rerun()
        else:
            st.error("❌ Incorrect Password")

    if st.session_state.get("admin_logged_in", False):
        st.success("✅ Logged in successfully!")
        
        if st.button("Refresh Data 🔄"):
            st.rerun()

        st.markdown("---")
        with st.spinner("Fetching live data from Google Sheets..."):
            try:
                client = get_gspread_client()
                sheet = client.open("ECM420_Database").sheet1
                data = sheet.get_all_records()
                
                if not data:
                    st.info("No data has been logged yet. Tell your students to start using the app!")
                else:
                    df = pd.DataFrame(data)
                    
                    # BULLETPROOF FIX: Strip away any hidden spaces in the Google Sheet column names
                    df.columns = df.columns.astype(str).str.strip()
                    
                    # Ensure Confidence Level acts as a number for the charts
                    if 'Confidence Level' in df.columns:
                        df['Confidence Level'] = pd.to_numeric(df['Confidence Level'], errors='coerce')
                    
                    if 'Confidence Level' in df.columns and 'Tool Used' in df.columns:
                        
                        # --- Metrics Row ---
                        colA, colB = st.columns(2)
                        with colA:
                            st.metric(label="Total Interactions Logged", value=len(df))
                        with colB:
                            avg_conf = df['Confidence Level'].mean()
                            st.metric(label="Average Class Confidence", value=f"{avg_conf:.1f} / 10")
                        
                        st.markdown("---")
                        
                        # --- Charts Row ---
                        colC, colD = st.columns(2)
                        
                        with colC:
                            st.markdown("**🛠️ Most Popular Learning Tools**")
                            tool_counts = df['Tool Used'].value_counts().reset_index()
                            tool_counts.columns = ['Tool Used', 'Count']
                            fig_pie = px.pie(tool_counts, values='Count', names='Tool Used', hole=0.3)
                            st.plotly_chart(fig_pie, use_container_width=True)

                        with colD:
                            st.markdown("**📊 Student Confidence Distribution**")
                            fig_bar = px.histogram(df, x='Confidence Level', nbins=10, 
                                                   labels={'Confidence Level': 'Confidence (1-10)'},
                                                   color_discrete_sequence=['#2E7D32'])
                            st.plotly_chart(fig_bar, use_container_width=True)

                        st.markdown("---")
                        
                        # --- Word Cloud Section ---
                        st.markdown("**☁️ Student Struggles Word Cloud**")
                        st.write("The larger the word, the more frequently students are asking about it!")
                        
                        if 'Student Input' in df.columns:
                            # Combine all text inputs into one big string
                            text_data = " ".join(df['Student Input'].dropna().astype(str).tolist())
                            
                            if text_data.strip(): # Ensure there is actually text
                                # Generate a green-themed word cloud
                                wordcloud = WordCloud(width=800, height=400, background_color='white', colormap='Greens').generate(text_data)
                                
                                # Display it using matplotlib
                                fig_wc, ax = plt.subplots(figsize=(10, 5))
                                ax.imshow(wordcloud, interpolation='bilinear')
                                ax.axis('off') # Hide axes
                                st.pyplot(fig_wc)
                            else:
                                st.info("Not enough text data to generate a word cloud yet.")
                        else:
                            st.warning("⚠️ Could not generate Word Cloud: Missing 'Student Input' column.")
                        
                        st.markdown("---")

                        # --- Raw Data Table ---
                        st.markdown("**📝 Raw Student Inputs**")
                        
                        # BULLETPROOF FIX: Safely pick the columns that actually exist to
