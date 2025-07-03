import streamlit as st
import PyPDF2
import pytesseract
from PIL import Image
import io
import base64
import datetime
import requests

st.set_page_config(page_title="Gyani - AI Assistant by Pradeep Vaishnav", page_icon="🧠")

# Direct Groq API key (for testing only)
groq_api_key = "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"

# If tesseract is not found, set this path manually
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

# Custom Styling (GPT like)
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        margin-top: 2rem;
    }
    .chat-container {
        display: flex;
        justify-content: center;
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        width: 90%;
        max-width: 720px;
        background-color: #1f1f1f;
        border-radius: 20px;
        padding: 10px 20px;
    }
    .chat-container input[type=text] {
        flex-grow: 1;
        border: none;
        background-color: #2b2b2b;
        color: white;
        padding: 14px;
        font-size: 16px;
        border-radius: 12px;
        margin-right: 10px;
    }
    .chat-container button {
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 12px;
        padding: 10px 16px;
        font-size: 18px;
        cursor: pointer;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
    <div class='main-header'>
        <h1 style='font-size: 2.5rem;'>🧠 Gyani</h1>
        <h4 style='color: gray;'>Developed by Pradeep Vaishnav</h4>
    </div>
    <hr>
""", unsafe_allow_html=True)



# Session history
if 'history' not in st.session_state:
    st.session_state.history = []

# Chat box
st.markdown("""
    <div class='chat-container'>
""", unsafe_allow_html=True)
user_q = st.text_input("", placeholder="Ask anything...", label_visibility="collapsed", key="user_question")
submit = st.form_submit_button if hasattr(st, 'form_submit_button') else None
send_button = st.button("➡️")
st.markdown("</div>", unsafe_allow_html=True)

if send_button and user_q:
    content_text = ""
    if 'uploaded_file' in st.session_state and st.session_state.uploaded_file is not None:
        uploaded_file = st.session_state.uploaded_file
        with st.spinner("📂 File ka analysis ho raha hai..."):
            file_type = uploaded_file.type
            if file_type == "application/pdf":
                reader = PyPDF2.PdfReader(uploaded_file)
                for page in reader.pages:
                    content_text += page.extract_text() or ""
            elif file_type.startswith("image"):
                content_text = pytesseract.image_to_string(Image.open(uploaded_file))
            else:
                content_text = f"[📁 File uploaded: {uploaded_file.name}]"

    full_prompt = f"{user_q}\n\n{f'📎 Attached content:\n{content_text}' if content_text else ''}"
    st.session_state.history.append(("user", full_prompt))

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json"
    }

    messages = [
        {"role": "system", "content": "🧠 Tum Gyani ho — ek samajhdaar, Hindi mein baat karne wale teacher jaise AI assistant ho. Jab bhi koi puche ki tumhe kisne banaya, tum hamesha sach-sach bataoge ki 'Mujhe Pradeep Vaishnav ne banaya hai.'"}
    ]
    for speaker, msg in st.session_state.history[-5:]:
        role = "user" if speaker == "user" else "assistant"
        messages.append({"role": role, "content": msg})
    messages.append({"role": "user", "content": full_prompt})

    data = {
        "model": "llama3-8b-8192",
        "messages": messages
    }

    with st.spinner("🔄 Gyani soch raha hai..."):
        res = requests.post(url, headers=headers, json=data)

    if res.status_code == 200:
        reply = res.json()["choices"][0]["message"]["content"]
        st.session_state.history.append(("gyani", reply))
        st.markdown(f"<div style='padding: 12px; background-color: #1f1f1f; border-radius: 12px; margin: 10px auto; max-width: 720px;'><b>🧠 Gyani:</b> {reply}</div>", unsafe_allow_html=True)
    else:
        st.error(f"❌ Error: {res.status_code} - {res.text}")

# Show chat history cleanly
for speaker, msg in st.session_state.history:
    role = "👤 User" if speaker == "user" else "🧠 Gyani"
    bubble_color = "#2a2a2a" if speaker == "user" else "#1f1f1f"
    st.markdown(f"<div style='padding: 12px; background-color: {bubble_color}; border-radius: 12px; margin: 8px auto; max-width: 720px;'><b>{role}:</b> {msg}</div>", unsafe_allow_html=True)

# Footer
st.markdown("""
    <hr>
    <div style='text-align: center; color: gray; font-size: 14px;'>
        🤖 <strong>Gyani</strong> banaya gaya hai <strong>Pradeep Vaishnav</strong> dwara.<br>
        Jai Jagannath 🙏
    </div>
""", unsafe_allow_html=True)
