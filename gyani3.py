import streamlit as st
import PyPDF2
import pytesseract
from PIL import Image
import io
import base64
import datetime
import openai

st.set_page_config(page_title="Gyani - AI Assistant by Pradeep Vaishnav", page_icon="🧠")

# Set OpenAI API key from Streamlit secrets
oai_key = st.secrets.get("OPENAI_API_KEY")
if oai_key:
    openai.api_key = oai_key
else:
    st.warning("🔐 OpenAI API key missing! Add it in .streamlit/secrets.toml")

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

    # Conversation prompt for better, natural reply
    conversation = [{"role": "system", "content": "🧠 Tum Gyani ho — ek samajhdaar, Hindi mein baat karne wale teacher jaise AI assistant ho. Tumhare jawab asaan, helpful, aur dosti bhare hone chahiye. Agar user ka prashn kisi file se related ho ya technical ho, to use udaharan dekar samjhao."}]

    for speaker, msg in st.session_state.history[-5:]:
        role = "user" if speaker == "user" else "assistant"
        conversation.append({"role": role, "content": msg})

    conversation.append({"role": "user", "content": user_q})

    if oai_key:
        try:
            response_obj = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=conversation
            )
            response = response_obj["choices"][0]["message"]["content"]
            st.success("🧠 Gyani: " + response)
        except Exception as e:
            response = "❌ Gyani abhi sthir hai. Error: " + str(e)
            st.error(response)
    else:
        response = "🧠 Gyani: Mujhe khed hai, OpenAI key nahi mili. File ka analysis to ho gaya, par AI se jawab dena sambhav nahi." 
        st.warning(response)

    st.session_state.history.append(("gyani", response))

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
st.markdown(f"<p style='text-align: right; font-size: small; color: gray;'>🕒 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>", unsafe_allow_html=True)

