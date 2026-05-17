import streamlit as st
import google.generativeai as genai
import os
import json
import gspread
import random
from google.oauth2.service_account import Credentials
from datetime import datetime
from markdown_pdf import MarkdownPdf, Section

# 1. Page Configuration
st.set_page_config(page_title="EMT-Predict & Pace", page_icon="⚡", layout="centered")

# --- Image & Video Databases for Randomization ---
# A list of cool, simple electromagnetics/physics images from Unsplash
em_images = [
    "https://images.unsplash.com/photo-1518770660439-4636190af475?q=80&w=600&auto=format&fit=crop", # Circuit/Tech
    "https://images.unsplash.com/photo-1581092334651-ddf26d9a09d0?q=80&w=600&auto=format&fit=crop", # Science lab
    "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?q=80&w=600&auto=format&fit=crop", # Magnetic waves abstract
    "https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=600&auto=format&fit=crop"  # Electromagnetic space/earth
]

# Dr. Aziati's Cleaned YouTube Video Links
youtube_videos = [
    "https://www.youtube.com/watch?v=CQcfN21XrKI", 
    "https://www.youtube.com/watch?v=acvNnQBC7mM",
    "https://www.youtube.com/watch?v=BD3d3C2JQdA",
    "https://www.youtube.com/watch?v=EOO880qh2yU"
]
# -----------------------------------------------------

# 2. Sidebar Layout
if os.path.exists("Logo.png"):
    st.sidebar.image("Logo.png", use_container_width=True)

st.sidebar.title("⚡ ESP")
st.sidebar.write("**Electromagnetic Smart Planner**")
st.sidebar.write("UiTM ECM420 Adaptive Study Planner & Tutor")
st.sidebar.markdown("---")

st.sidebar.subheader("Student Profile")
confidence = st.sidebar.slider("Confidence Level in ECM420 (1=Lost, 10=Confident)", 1, 10, 5)
days_remaining = st.sidebar.number_input("Days Remaining until Exam/Quiz", min_value=1, max_value=30, value=7)

# 3. Main Page Content
main_col1, main_col2 = st.columns([3, 1], vertical_alignment="center")

with main_col1:
    st.markdown(
        "<h2 style='margin: 0;'>⚡ ESP: Electromagnetic Smart Planner</h2>", 
        unsafe_allow_html=True
    )

with main_col2:
    fke_filename = "FKE logo.jpg"
    if os.path.exists(fke_filename):
        st.image(fke_filename, use_container_width=True)
    else:
        st.image("https://aims.uitm.edu.my/images/uitm_logo.png", use_container_width=True)

# --- RANDOM MOBILE FRIENDLY IMAGE ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image(random.choice(em_images), use_container_width=True, caption="Master the Forces of Nature ⚡")
# ------------------------------------

st.info("""
**👉 HOW TO USE YOUR AI TUTOR:**
1. **Set your profile (Left Sidebar):** Adjust your confidence level and days left. *(📱 Mobile users: Tap the **`>`** arrow at the top left of your screen to open the sidebar!)*
2. **Describe your struggle:** Be specific! (e.g., *"I don't know how to apply Gauss's Law."*)
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

# PDF Generator Function
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
                1. A brief, encouraging diagnosis validating their struggle. CRITICAL: In your diagnosis, explicitly tell the student to watch the recommended video lecture provided below in the app.
                2. A structured, day-by-day study schedule spreading out the concepts over {days_remaining} days. Reference the syllabus. IMPORTANT: You MUST format this study schedule strictly as a Markdown table with exactly 5 columns. You MUST include a valid formatting separator row right under the headers (e.g., |---|---|---|---|---|). Paraphrase all concepts to avoid recitation filters.
                3. A suggested checkpoint question or mini-quiz at the end.
                
                CRITICAL FORMATTING RULES FOR PDF COMPATIBILITY:
                - DO NOT use LaTeX, MathJax, or dollar signs ($ or $$) for equations or Greek letters under ANY circumstances. The PDF converter will crash.
                - Use plain English words for Greek letters (e.g., type "rho", "theta", "phi", "epsilon").
                - Use plain keyboard text for formulas (e.g., type "x = r * cos(theta)").
                - Keep text formatting simple. Use standard **bold** and *italics* only. Do not skip heading levels (use ## then ###).
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
                    
                    # --- EXTRA RANDOM IMAGE & RANDOM VIDEO IN THE ANSWER ---
                    st.markdown("---")
                    
                    # Pop in a second random EM image to break up the text visually!
                    st.image(random.choice(em_images), use_container_width=True, caption="Visualize the Field")
                    
                    st.subheader("📺 Recommended Dr. Aziati Lecture")
                    st.write("Based on your study plan, here is a helpful lecture to get you started:")
                    # Picks a random video from the cleaned list!
                    st.video(random.choice(youtube_videos))
                    # ------------------------------------------------------------
                    
                    # --- PDF DOWNLOAD BUTTON ---
                    st.markdown("---")
                    
                    clean_md = response.text.replace("\n||\n", "\n|---|---|---|---|---|\n")
                    clean_md = clean_md.replace("\n| |\n", "\n|---|---|---|---|---|\n")
                    
                    try:
                        pdf_bytes = create_pdf(clean_md)
                        st.download_button(
                            label="📥 Download Plan as PDF",
                            data=pdf_bytes,
                            file_name="ECM420_Study_Plan.pdf",
                            mime="application/pdf"
                        )
                    except Exception as pdf_error:
                         st.error(f"⚠️ Plan generated, but PDF conversion failed: {pdf_error}. You can still copy the text above.")
                    # ---------------------------
                    
                else:
                    block_reason = response.candidates[0].finish_reason if response.candidates else "UNKNOWN_ERROR"
                    st.error(f"⚠️ The AI blocked the response. (Error Code: {block_reason}). Try rephrasing your struggle or shortening the syllabus.")
                
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "quota" in error_msg.lower():
                    st.warning("⏳ The AI tutor is currently helping a lot of students at once! Please take a deep breath, wait a minute or two, and click Generate again.")
                else:
                    st.error(f"An error occurred while contacting the AI: {e}")
