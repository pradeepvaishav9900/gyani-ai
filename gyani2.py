import streamlit as st
import requests
import PyPDF2
import io
import wikipedia
from langdetect import detect

st.set_page_config(page_title="Gyani v2 - Smart AI Assistant", page_icon="🧠")
st.title("🧠 Gyani v2 - Smart + Auto-Detect Mode")
st.markdown("#### Developed by Pradeep Vaishnav")

# Load API Key
groq_api_key = "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"

# Initialize history
if "history" not in st.session_state:
    st.session_state.history = []

# File upload (optional for summarizer)
uploaded_file = st.file_uploader("📂 Upload a PDF (optional)", type=["pdf"])
extracted_text = ""
if uploaded_file:
    reader = PyPDF2.PdfReader(uploaded_file)
    extracted_text = "".join(page.extract_text() or "" for page in reader.pages)

# Smart Input Form
text_input_key = "input_box"
with st.form("ask_gyani"):
    user_input = st.text_input("💬 Gyani se poochho:", placeholder="Type your query...", key=text_input_key)
    submitted = st.form_submit_button("💬 Send")

if submitted and user_input:
    query = user_input.lower()
    
