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

uploaded_file = st.file_uploader("<b>📄 File Upload karein (PDF ya Image):</b>", type=["pdf", "png", "jpg", "jpeg"])

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
    with st.spinner("<i>📚 Gyani file ka vishleshan kar raha hai...</i>"):
        if file_type == "application/pdf":
            text_content = extract_text_from_pdf(uploaded_file)
        elif file_type.startswith("image/"):
            text_content = extract_text_from_image(uploaded_file)

    if text_content.strip():
        st.success("✅ File se gyaan prapt ho gaya!")
        st.text_area("📖 Extracted Content:", text_content, height=300, max_chars=10000)
    else:
        st.warning("⚠️ Koi padne layak text nahi mila file se.")

if 'history' not in st.session_state:
    st.session_state.history = []

# Stylish chat interface box at bottom like screenshot
st.markdown("""
<style>
.chat-bar {
    position: fixed;
    bottom: 1rem;
    left: 50%;
    transform: translateX(-50%);
    width: 95%;
    max-width: 700px;
    display: flex;
    align-items: center;
    background: #2b2b2b;
    border-radius: 20px;
    padding: 10px 15px;
    box-shadow: 0 0 12px rgba(0, 0, 0, 0.3);
    z-index: 9999;
}
.chat-bar input {
    flex: 1;
    padding: 8px 12px;
    border-radius: 10px;
    border: none;
    background: #1c1c1c;
    color: #fff;
}
.chat-bar button {
    margin-left: 10px;
    padding: 8px 15px;
    background-color: #4CAF50;
    border: none;
    color: white;
    border-radius: 10px;
    cursor: pointer;
}
</style>
<div class="chat-bar">
    <form action="#" method="post" onsubmit="return false;">
        <input id="chat_input" name="chat_input" placeholder="💬 Kuch bhi poochhiye...">
        <button onclick="document.querySelector('button[data-testid=\"submit_button\"]').click();">➡️</button>
    </form>
</div>
<script>
const input = document.getElementById("chat_input");
input.addEventListener("keydown", function(e) {
    if (e.key === "Enter") {
        e.preventDefault();
        document.querySelector('button[data-testid="submit_button"]').click();
    }
});
</script>
""", unsafe_allow_html=True)

chat_image = st.file_uploader("🖼️ Image bhejein:", type=["jpg", "jpeg", "png"], key="chat_image")

user_q = st.text_input("", placeholder="", label_visibility="collapsed", key="chat_box")
submit = st.button("Send", key="submit_button")

if user_q or submit:
    image_text = ""
    if chat_image:
        with st.spinner("🖼️ Image se gyaan prapt kiya ja raha hai..."):
            image_text = extract_text_from_image(chat_image)

    full_prompt = f"{user_q}\n\n{f'🖼️ Image ka content:\n{image_text}' if image_text else ''}"
    st.session_state.history.append(("user", full_prompt))
    st.markdown(f"<div style='padding: 10px; border-left: 4px solid #ffd700; background-color: #2c2c2c; border-radius: 6px;'>👤 <b>Aapka Prashn:</b> {user_q} {'<i>(🖼️ image ke saath)</i>' if chat_image else ''}</div>", unsafe_allow_html=True)

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
        st.markdown(f"<div style='padding: 10px; background-color: #232323; border-radius: 6px;'><b>🧠 Gyani:</b> {reply}</div>", unsafe_allow_html=True)
    else:
        st.error(f"❌ Error: {res.status_code} - {res.text}")

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
