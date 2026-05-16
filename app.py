import streamlit as st
import google.generativeai as genai
import os
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from fpdf import FPDF

# 1. Page Configuration
st.set_page_config(page_title="EMT-Predict & Pace", page_icon="⚡", layout="wide")

# 2. Sidebar Layout
st.sidebar.title("⚡ EMT-Predict & Pace")
st.sidebar.write("**UiTM ECM420 Adaptive Study Planner**")
st.sidebar.markdown("---")

st.sidebar.subheader("Student Profile")
confidence = st.sidebar.slider("Confidence Level in ECM420 (1=Lost, 10=Confident)", 1, 10, 5)
days_remaining = st.sidebar.number_input("Days Remaining until Exam/Quiz", min_value=1, max_value=30, value=7)

# ---------------------------------------------------------
# Step: REPLACE ONLY SECTION 3 IN YOUR app.py ON GITHUB
# ---------------------------------------------------------

# 3. Main Page Content
st.title("Welcome to your ECM420 AI Tutor 🎓")

# --- CALMER, SMALLER IMAGE ---
# We use a minimalist image and force a smaller, fixed width (400px)
st.image("https://images.unsplash.com/photo-1516979187457-637abb4f9353?q=80&w=600&auto=format&fit=crop", width=400, caption="Calm Minds, Bright Futures")
# ----------------------------

st.info("""
**👉 HOW TO USE YOUR AI TUTOR:**
1. **Set your profile (Left Sidebar):** Adjust your confidence level and the days remaining until your test.
2. **Describe your struggle:** Be specific! (e.g., *"I don't know how to apply Gauss's Law to a cylindrical surface."*)
3. **Generate:** Click the button below to get your custom sprint schedule.
""")

st.write("Having trouble with Electromagnetics Theory? Tell me exactly what is confusing you, and I will generate a custom, day-by-day sprint schedule mapped directly to your UiTM syllabus.")

student_struggle = st.text_area(
    "Describe your struggle:",
    height=150
)

# Database Logging Function
def log_to_sheets(conf_level, days, struggle):
    try:
        creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS_JSON"])
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        sheet = client.open("ECM420_Database").sheet1
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([current_time, conf_level, days, struggle])
    except Exception as e:
        print(f"Database Error: {e}")

# --- NEW: PDF GENERATOR FUNCTION ---
def create_pdf(plan_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)
    # Replaces emojis and special characters so the PDF doesn't crash
    safe_text = plan_text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 7, text=safe_text)
    return bytes(pdf.output())
# -----------------------------------

# 4. The Action Button & AI Logic
if st.button("Generate My Sprint Plan 🚀"):
    if not student_struggle:
        st.warning("⚠️ Please describe what you are struggling with so I can help!")
    else:
        with st.spinner("Analyzing your learning gap and checking the ECM420 syllabus..."):
            
            log_to_sheets(confidence, days_remaining, student_struggle)
            
            try:
                syllabus_data = "Syllabus not found. Please provide general electromagnetics advice."
                if os.path.exists("syllabus.txt"):
                    with open("syllabus.txt", "r", encoding="utf-8") as file:
                        syllabus_data = file.read()

                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                system_prompt = f"""
                You are an empathetic, expert university professor teaching Electromagnetics Theory (course code ECM420) at UiTM. 
                A student has come to you for help.
                
                Here is the official ECM420 syllabus and course outline for your reference:
                ---
                {syllabus_data}
                ---
                
                Student's Current Confidence Level (1-10): {confidence}
                Days until their assessment: {days_remaining}
                Their specific struggle: "{student_struggle}"
                
                Please provide:
                1. A brief, encouraging diagnosis validating their struggle.
                2. A structured, day-by-day study schedule spreading out the concepts over {days_remaining} days. Reference the syllabus. IMPORTANT: Paraphrase all concepts to avoid recitation filters.
                3. A suggested checkpoint question or mini-quiz at the end.
                
                Format the response beautifully using Markdown headings, bold text, and bullet points.
                """
                
                response = model.generate_content(
                    system_prompt,
                    safety_settings=[
                        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
                    ]
                )
                
                if response.candidates and response.candidates[0].content.parts:
                    st.success("UiTM-Aligned Plan Generated Successfully!")
                    st.markdown(response.text)
                    
                    # --- PDF DOWNLOAD BUTTON ---
                    st.markdown("---")
                    pdf_bytes = create_pdf(response.text)
                    st.download_button(
                        label="📥 Download Plan as PDF",
                        data=pdf_bytes,
                        file_name="ECM420_Study_Plan.pdf",
                        mime="application/pdf"
                    )
                    # ---------------------------
                    
                else:
                    block_reason = response.candidates[0].finish_reason if response.candidates else "UNKNOWN_ERROR"
                    st.error(f"⚠️ The AI blocked the response. (Error Code: {block_reason}). Try rephrasing your struggle or shortening the syllabus.")
                
            except Exception as e:
                st.error(f"An error occurred while contacting the AI: {e}")
