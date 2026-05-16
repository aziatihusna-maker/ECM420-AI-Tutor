import streamlit as st
import google.generativeai as genai
import os

# 1. Page Configuration
st.set_page_config(page_title="EMT-Predict & Pace", page_icon="⚡", layout="wide")

# 2. Sidebar Layout
st.sidebar.title("⚡ EMT-Predict & Pace")
st.sidebar.write("**UiTM ECM420 Adaptive Study Planner**")
st.sidebar.markdown("---")

st.sidebar.subheader("Student Profile")
confidence = st.sidebar.slider("Confidence Level in ECM420 (1=Lost, 10=Confident)", 1, 10, 5)
days_remaining = st.sidebar.number_input("Days Remaining until Exam/Quiz", min_value=1, max_value=30, value=7)

# 3. Main Page Content
st.title("Welcome to your ECM420 AI Tutor 🎓")

# --- IMPROVED VISIBILITY: Colored Info Box ---
st.info("""
**👉 HOW TO USE YOUR AI TUTOR:**
1. **Set your profile (Left Sidebar):** Adjust your confidence level and the days remaining until your test.
2. **Describe your struggle:** Be specific! (e.g., *"I don't know how to apply Gauss's Law to a cylindrical surface."*)
3. **Generate:** Click the button below to get your custom sprint schedule.
""")
# ---------------------------------------------

st.write("Having trouble with Electromagnetics Theory? Tell me exactly what is confusing you, and I will generate a custom, day-by-day sprint schedule mapped directly to your UiTM syllabus.")

student_struggle = st.text_area(
    "Describe your struggle:",
    height=150
)

# 4. The Action Button & AI Logic
if st.button("Generate My Sprint Plan 🚀"):
    if not student_struggle:
        st.warning("⚠️ Please describe what you are struggling with so I can help!")
    else:
        with st.spinner("Analyzing your learning gap and checking the ECM420 syllabus..."):
            try:
                # Read the syllabus file
                syllabus_data = "Syllabus not found. Please provide general electromagnetics advice."
                if os.path.exists("syllabus.txt"):
                    with open("syllabus.txt", "r", encoding="utf-8") as file:
                        syllabus_data = file.read()

                # Configure the AI using Streamlit Secrets
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
                1. A brief, encouraging diagnosis validating their struggle (ECM420 is tough!).
                2. A structured, day-by-day study schedule spreading out the concepts over {days_remaining} days. Ensure your advice references topics from the syllabus. IMPORTANT: Do NOT quote the syllabus verbatim. Paraphrase all concepts in your own words to avoid recitation filters.
                3. A suggested checkpoint question or mini-quiz at the end to test their understanding.
                
                Format the response beautifully using Markdown headings, bold text, and bullet points. Use LaTeX formatting only if you need to output complex physics equations (using $ and $$ delimiters).
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
                    
                    # --- NEW: Download Button ---
                    st.markdown("---")
                    st.download_button(
                        label="📥 Download Your Study Plan",
                        data=response.text,
                        file_name="ECM420_Study_Plan.txt",
                        mime="text/plain"
                    )
                    st.caption("💡 *Tip: You can also right-click anywhere on this page and select 'Print' to save it as a PDF!*")
                    # ----------------------------
                    
                else:
                    block_reason = response.candidates[0].finish_reason if response.candidates else "UNKNOWN_ERROR"
                    st.error(f"⚠️ The AI blocked the response. (Error Code: {block_reason}). Try rephrasing your struggle or shortening the syllabus.")
                
            except Exception as e:
                st.error(f"An error occurred while contacting the AI: {e}")
