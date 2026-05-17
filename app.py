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

# Dr. Aziati's YouTube Video Links WITH the playlist attached!
youtube_videos = [
    "https://www.youtube.com/watch?v=CQcfN21XrKI&list=PLPOivWONMRkcdSL5-ae1w1NTJqIWCwYW6", 
    "https://www.youtube.com/watch?v=acvNnQBC7mM&list=PLPOivWONMRkcdSL5-ae1w1NTJqIWCwYW6",
    "https://www.youtube.com/watch?v=BD3d3C2JQdA&list=PLPOivWONMRkcdSL5-ae1w1NTJqIWCwYW6",
    "https://www.youtube.com/watch?v=EOO880qh2yU&list=PLPOivWONMRkcdSL5-ae1w1NTJqIWCwYW6"
]
# -----------------------------------------------------

# 2. Sidebar Layout
# --- UPDATED: Logos are now placed side-by-side to save vertical space! ---
logo_col1, logo_col2 = st.sidebar.columns(2, vertical_alignment="center")

with logo_col1:
    fke_filename = "FKE logo.jpg"
    if os.path.exists(fke_filename):
        st.image(fke_filename, use_container_width=True)
    else:
        st.image("https://aims.uitm.edu.my/images/uitm_logo.png", use_container_width=True)

with logo_col2:
    if os.path.exists("Logo.png"):
        st.image("Logo.png", use_container_width=True)

st.sidebar.title("⚡ ESP")
st.sidebar.write("**Electromagnetic Smart Planner**")
st.sidebar.write("UiTM ECM420 Adaptive Study Planner & Tutor")
st.sidebar.markdown("---")

st.sidebar.subheader("Student Profile")
confidence = st.sidebar.slider("Confidence Level in ECM420 (1=Lost, 10=Confident)", 1, 10, 5)
days_remaining = st.sidebar.number_input("Days Remaining until Exam/Quiz", min_value=1, max_value=30, value=7)

# 3. Main Page Content
st.markdown(
    "<h2 style='margin: 0; padding-bottom: 20px;'>⚡ ESP: Electromagnetic Smart Planner</h2>", 
    unsafe_allow_html=True
)

# --- RANDOM MOBILE FRIENDLY IMAGE ---
col1, col2, col3 = st.columns([1, 2, 1])
with col
