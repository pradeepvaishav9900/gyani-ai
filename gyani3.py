import streamlit as st
import PyPDF2
import pytesseract
from PIL import Image
import io
import base64
import datetime
import requests

st.set_page_config(page_title="Gyani - AI Assistant by Pradeep Vaishnav", page_icon="🧠")

# Set Groq API key from Streamlit secrets
groq_api_key = "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"  # 👈 Apni asli Groq API key yahan daalein (testing ke liye)

# Logo and Title Section
st.markdown("""
    <div style='text-align: center;'>
        <img src='https://i.imgur.com/Wr9vB2M.png' alt='Gyani Logo' width='120'/><br>
        <h1 style='margin-top: 10px;'>🧠 Gyani</h1>
        <h4 style='color: gray;'>Developed by Pradeep Vaishnav</h4>
    </div>
    <hr>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("📄 File Upload karein (PDF ya Image):", type=["pdf", "png", "jpg", "jpeg"])

def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def extract_text_from_image(file):
    image = Image.open(file)
    text = pytesseract.image_to_string(image)
    return text

text_content = ""

if uploaded_file is not None:
    file_type = uploaded_file.type
    with st.spinner("📚 Gyani file ka vishleshan kar raha hai..."):
        if file_type == "application/pdf":
            text_content = extract_text_from_pdf(uploaded_file)
        elif file_type.startswith("image/"):
            text_content = extract_text_from_image(uploaded_file)

    if text_content.strip():
        st.success("✅ File se gyaan prapt ho gaya!")
        st.text_area("📖 Extracted Content:", text_content, height=300, max_chars=10000)
    else:
        st.warning("⚠️ Koi padne layak text nahi mila file se.")

# Chat History
if 'history' not in st.session_state:
    st.session_state.history = []

user_q = st.text_input("🧠 Aapka Prashn likhiye:")
if user_q:
    st.session_state.history.append(("user", user_q))
    st.markdown(f"👤 Aapka Prashn: *{user_q}*")
    response = ""

    # Prepare Groq API request
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json"
    }

    # Prepare messages
    messages = [
        {"role": "system", "content": "🧠 Tum Gyani ho — ek samajhdaar, Hindi mein baat karne wale teacher jaise AI assistant ho. Tumhare jawab asaan, helpful, aur dosti bhare hone chahiye. Agar user ka prashn kisi file se related ho ya technical ho, to use udaharan dekar samjhao."}
    ]
    for speaker, msg in st.session_state.history[-5:]:
        role = "user" if speaker == "user" else "assistant"
        messages.append({"role": role, "content": msg})
    messages.append({"role": "user", "content": user_q})

    data = {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "messages": messages
    }

    # Make the API call
    with st.spinner("🔄 Gyani soch raha hai..."):
        res = requests.post(url, headers=headers, json=data)

    if res.status_code == 200:
        reply = res.json()["choices"][0]["message"]["content"]
        st.session_state.history.append(("gyani", reply))
        st.success("🧠 Gyani: " + reply)
    else:
        st.error(f"❌ Error: {res.status_code} - {res.text}")

# Display full conversation
st.markdown("<hr><h4>📜 Purani Baatein:</h4>", unsafe_allow_html=True)
for speaker, msg in st.session_state.history:
    if speaker == "user":
        st.markdown(f"👤 **User**: {msg}")
    else:
        st.markdown(f"🧠 **Gyani**: {msg}")

st.markdown("""
    <hr>
    <div style='text-align: center; color: gray;'>
        🤖 <strong>Gyani</strong> Chatbot ka nirmaan <strong>Pradeep Vaishnav</strong> dwara kiya gaya hai.<br>
        Jai Jagannath 🙏
    </div>
""", unsafe_allow_html=True)

# Suggested questions for better interaction
st.markdown("""
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
st.markdown(f"<p style='text-align: right; font-size: small; color: gray;'>🕒 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>", unsafe_allow_html=True)v
