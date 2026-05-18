import streamlit as st
import anthropic
import os
import json
import gspread
import random
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
# UPDATED: Now accepts 'tool_used' as a parameter to track which tab they clicked!
def log_to_sheets(conf_level, days, tool_used, student_input):
    try:
        if "GOOGLE_CREDENTIALS_JSON" in st.secrets:
            creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS_JSON"])
            scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
            creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
            client = gspread.authorize(creds)
            sheet = client.open("ECM420_Database").sheet1
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Appends 5 columns to your Google Sheet
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
tab1, tab2, tab3 = st.tabs(["🚀 Sprint Plan", "🧠 Feynman Checker", "🌊 Analogy Engine"])

# ==========================================
# TAB 1: SPRINT PLANNER 
# ==========================================
with tab1:
    st.info("**Tool 1: Sprint Plan** - Tell me what topic you are struggling with, and I will generate a custom, day-by-day study schedule aligned with your remaining days.")

    student_struggle = st.text_area("Having trouble with Electromagnetics Theory? Tell me exactly what is confusing you:", height=100)

    if st.button("Generate My Sprint Plan 🚀"):
        if not student_struggle:
            st.warning("⚠️ Please describe what you are struggling with so I can help!")
        else:
            with st.spinner("Analyzing your learning gap with Claude AI..."):
                # LOGGING: Tags as "Sprint Plan"
                log_to_sheets(confidence, days_remaining, "Sprint Plan", student_struggle)
                
                try:
                    syllabus_data = "Syllabus not found. Please provide general electromagnetics advice."
                    if os.path.exists("syllabus.txt"):
                        with open("syllabus.txt", "r", encoding="utf-8") as file:
                            syllabus_data = file.read()

                    client = anthropic.Anthropic(api_key=st.secrets["CLAUDE_API_KEY"])
                    
                    user_message = f"""
                    Syllabus:\n{syllabus_data}\n\n
                    Student Confidence: {confidence}\nDays to Assessment: {days_remaining}\nStruggle: "{student_struggle}"\n
                    Provide:
                    1. Brief diagnosis.
                    2. A day-by-day table study schedule over {days_remaining} days (exactly 5 columns).
                    3. A mini-quiz at the end.
                    """
                    
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
    st.info("**Tool 2: Feynman Checker** - The best way to learn is to teach. Explain an ECM420 concept in your own words below, and I will grade your understanding like a professor!")
    
    student_explanation = st.text_area("Explain a concept to me (e.g., How does Gauss's Law work? Why do we use cylindrical coordinates?):", height=150)
    
    if st.button("Check My Understanding 🧠"):
        if not student_explanation:
            st.warning("⚠️ Please type your explanation first!")
        else:
            with st.spinner("Reviewing your explanation like a strict but fair professor..."):
                # LOGGING: Tags as "Feynman Checker"
                log_to_sheets(confidence, days_remaining, "Feynman Checker", student_explanation)
                
                try:
                    client = anthropic.Anthropic(api_key=st.secrets["CLAUDE_API_KEY"])
                    
                    feynman_prompt = f"""
                    The student has provided the following explanation of an Electromagnetics concept in their own words:
                    "{student_explanation}"
                    
                    Task:
                    1. Point out exactly what they got right.
                    2. Gently correct any misconceptions or technical errors.
                    3. Give them a 'Comprehension Score' out of 10.
                    """
                    
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
    st.info("**Tool 3: Analogy Engine** - Invisible forces are notoriously abstract. Tell me what formula or concept you are stuck on, and I will explain it using a real-world physical analogy.")
    
    analogy_topic = st.text_input("What concept is confusing you? (e.g., Divergence, Magnetic Flux, Biot-Savart Law)")
    
    if st.button("Give Me an Analogy 🌍"):
        if not analogy_topic:
            st.warning("⚠️ Please enter a topic!")
        else:
            with st.spinner("Brewing up a real-world analogy..."):
                # LOGGING: Tags as "Analogy Engine"
                log_to_sheets(confidence, days_remaining, "Analogy Engine", analogy_topic)
                
                try:
                    client = anthropic.Anthropic(api_key=st.secrets["CLAUDE_API_KEY"])
                    
                    analogy_prompt = f"""
                    The student is struggling to intuitively understand this concept: "{analogy_topic}".
                    
                    Task:
                    1. Explain this concept using a highly vivid, real-world physical analogy (like water flowing through pipes, traffic, wind, rubber bands, etc.).
                    2. Map the variables of the concept directly to the analogy (e.g., "The water pressure represents voltage V, the pipe width represents resistance...").
                    3. Keep it encouraging and easy to visualize.
                    """
                    
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
