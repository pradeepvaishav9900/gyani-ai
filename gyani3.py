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

# Logo and Title Section
st.markdown("""
    <div style='text-align: center;'>
        <img src='https://i.imgur.com/Wr9vB2M.png' alt='Gyani Logo' width='120'/><br>
        <h1 style='margin-top: 10px;'>🧠 Gyani</h1>
        <h4 style='color: gray;'>Developed by Pradeep Vaishnav</h4>
    </div>
    <hr>
""", unsafe_allow_html=True)

if 'history' not in st.session_state:
    st.session_state.history = []

uploaded_file = st.file_uploader("📄 File ya photo/video bhejein (PDF, Image, Video):", type=["pdf", "jpg", "jpeg", "png", "mp4", "mov", "avi"], key="chat_image")

# Display chat history
st.markdown("<hr><h4>📜 Purani Baatein:</h4>", unsafe_allow_html=True)
for speaker, msg in st.session_state.history:
    if speaker == "user":
        st.markdown(f"<div style='padding: 8px; background-color: #2a2a2a; border-left: 4px solid #ffcc00;'>👤 <b>User:</b> {msg}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='padding: 8px; background-color: #1f1f1f; border-left: 4px solid #00cc99;'>🧠 <b>Gyani:</b> {msg}</div>", unsafe_allow_html=True)

# Footer and Suggestions
st.markdown("""
    <hr>
    <div style='text-align: center; color: gray;'>
        🤖 <strong>Gyani</strong> Chatbot ka nirmaan <strong>Pradeep Vaishnav</strong> dwara kiya gaya hai.<br>
        Jai Jagannath 🙏
    </div>
    <div style='margin-top:30px;'>
        <h4>📝 Aap yeh prashn bhi pooch sakte hain:</h4>
        <ul>
            <li>Python me loop kaise chalta hai?</li>
            <li>Newton ka pehla niyam kya hai?</li>
            <li>HTML ka basic structure kya hota hai?</li>
            <li>Is file me syllabus hai kya?</li>
        </ul>
    </div>
""", unsafe_allow_html=True)

# Timestamp
st.markdown(f"<p style='text-align: right; font-size: small; color: gray;'>🕒 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>", unsafe_allow_html=True)

# Chat input form styled like screenshot
with st.form("chat_form", clear_on_submit=True):
    st.markdown("""
    <style>
    .css-13sdm1v { display: none; }
    .custom-input-box {
        position: fixed;
        bottom: 10px;
        left: 50%;
        transform: translateX(-50%);
        width: 90%;
        max-width: 720px;
        display: flex;
        background-color: #1f1f1f;
        padding: 10px;
        border-radius: 12px;
        z-index: 999;
    }
    .custom-input-box textarea {
        flex-grow: 1;
        margin-right: 8px;
        border-radius: 8px;
        background-color: #2b2b2b;
        color: white;
        border: none;
        padding: 10px;
    }
    .custom-input-box button {
        background-color: #4CAF50;
        border: none;
        border-radius: 8px;
        padding: 8px 12px;
        color: white;
        cursor: pointer;
    }
    </style>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown("<div class='custom-input-box'>", unsafe_allow_html=True)
        user_q = st.text_area("", placeholder="💬 Kuch bhi poochhiye...", label_visibility="collapsed", key="user_question")
        submitted = st.form_submit_button("➡️")
        st.markdown("</div>", unsafe_allow_html=True)

    if submitted and user_q:
        content_text = ""
        if uploaded_file is not None:
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
        st.markdown(f"<div style='padding: 10px; border-left: 4px solid #ffd700; background-color: #2c2c2c; border-radius: 6px;'>👤 <b>Aapka Prashn:</b> {user_q} {'<i>(📎 file ke saath)</i>' if uploaded_file else ''}</div>", unsafe_allow_html=True)

        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {groq_api_key}",
            "Content-Type": "application/json"
        }

        messages = [
            {"role": "system", "content": "🧠 mera naam gyani hai — ek samajhdaar, Hindi mein baat karne wale teacher jaise AI assistant ho. Jab bhi koi puche ki tumhe kisne banaya, tum hamesha sach-sach bataoge ki 'Mujhe Pradeep Vaishnav ne banaya hai.'"}
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
            st.markdown(f"<div style='padding: 10px; background-color: #232323; border-radius: 6px;'><b>🧠 Gyani:</b> {reply}</div>", unsafe_allow_html=True)
        else:
            st.error(f"❌ Error: {res.status_code} - {res.text}")
