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

st.sidebar.subheader("Student Profile")
confidence = st.sidebar.slider("ECM420 Confidence (1-10)", 1, 10, 5)
days_remaining = st.sidebar.number_input("Days to Assessment", min_value=1, max_value=30, value=7)

# --- 4. Main Page Content ---
st.markdown("<h2 style='margin: 0; padding-bottom: 20px;'>⚡ ESP: Electromagnetic Smart Planner</h2>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image(random.choice(em_images), use_container_width=True, caption="Master the Forces of Nature ⚡")

st.info("""
**👉 HOW TO USE YOUR AI TUTOR:**
1. **Set your profile (Left Sidebar):** Adjust your confidence level and days left. 
2. **Describe your struggle:** Be specific! (e.g., *"I don't know how to apply Gauss's Law."*)
3. **Generate:** Click the button below to get your custom sprint schedule.
""")

student_struggle = text_area_input = st.text_area("Having trouble with Electromagnetics Theory? Tell me exactly what is confusing you:", height=150)

# --- 5. Helper Functions ---
def log_to_sheets(conf_level, days, struggle):
    try:
        if "GOOGLE_CREDENTIALS_JSON" in st.secrets:
            creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS_JSON"])
            scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
            creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
            client = gspread.authorize(creds)
            sheet = client.open("ECM420_Database").sheet1
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sheet.append_row([current_time, conf_level, days, struggle])
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

# --- 6. Execution Block (Claude AI) ---
if st.button("Generate My Sprint Plan 🚀"):
    if not student_struggle:
        st.warning("⚠️ Please describe what you are struggling with so I can help!")
    else:
        with st.spinner("Analyzing your learning gap with Claude AI..."):
            log_to_sheets(confidence, days_remaining, student_struggle)
            
            try:
                syllabus_data = "Syllabus not found. Please provide general electromagnetics advice."
                if os.path.exists("syllabus.txt"):
                    with open("syllabus.txt", "r", encoding="utf-8") as file:
                        syllabus_data = file.read()

                # Initialize Anthropic Client
                client = anthropic.Anthropic(api_key=st.secrets["CLAUDE_API_KEY"])
                
                system_instructions = """
                You are an empathetic, expert university professor teaching Electromagnetics Theory (course code ECM420) at UiTM. 
                CRITICAL RULES:
                - NO LaTeX, MathJax, or dollar signs ($ or $$). Write out Greek letters (e.g., epsilon, mu).
                - MUST output a Markdown table with exactly 5 columns.
                - Keep formatting simple so the PDF engine does not crash.
                """
                
                user_message = f"""
                Syllabus:\n{syllabus_data}\n\n
                Student Confidence: {confidence}\nDays to Assessment: {days_remaining}\nStruggle: "{student_struggle}"\n
                Provide:
                1. Brief diagnosis.
                2. A day-by-day table study schedule over {days_remaining} days.
                3. A mini-quiz at the end.
                """
                
                response = client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=2000,
                    system=system_instructions,
                    messages=[{"role": "user", "content": user_message}]
                )
                
                response_text = response.content[0].text
                
                if response_text:
                    st.success("Plan Generated Successfully!")
                    st.markdown(response_text)
                    st.markdown("---")
                    
                    st.subheader("📺 Recommended Dr. Aziati Lecture")
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
