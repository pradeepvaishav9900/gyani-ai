import streamlit as st
import PyPDF2
import pytesseract
from PIL import Image
import io
import base64
import datetime
import requests
from langdetect import detect
from bs4 import BeautifulSoup
import wikipedia

st.set_page_config(page_title="Gyani - AI Assistant by Pradeep Vaishnav", page_icon="🤖")

# Logo and Title
st.markdown("""
    <div style='text-align: center;'>
        <img src='https://i.imgur.com/Wr9vB2M.png' alt='Gyani Logo' width='120'/><br>
        <h1 style='margin-top: 10px;'>🤖 Gyani</h1>
        <h4 style='color: gray;'>Developed by Pradeep Vaishnav</h4>
        <p style='font-size: 14px; color: #555;'>Gyani ek AI sahayak hai jo Pradeep Vaishnav dwara banaya gaya hai. Iska uddeshya logo ko gyaan dena aur unki samasyaon ka samadhan karna hai.</p>
        <p style='font-size: 13px; color: #999;'>Creator & Owner: <strong>Pradeep Vaishnav</strong></p>
    </div>
    <hr>
""", unsafe_allow_html=True)

col1, col2 = st.columns([8, 1])
with col1:
    uploaded_file = st.file_uploader("", type=["pdf", "png", "jpg", "jpeg"], label_visibility="collapsed")
with col2:
    st.markdown("<div style='text-align: right; font-size: 22px;'>➕</div>", unsafe_allow_html=True)

text_content = ""

# Text Extraction

def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_image(file):
    image = Image.open(file)
    text = pytesseract.image_to_string(image)
    return text

if uploaded_file is not None:
    file_type = uploaded_file.type
    with st.spinner("📚 Gyani file ka vishleshan kar raha hai..."):
        if file_type == "application/pdf":
            text_content = extract_text_from_pdf(uploaded_file)
        elif "image" in file_type:
            text_content = extract_text_from_image(uploaded_file)

    st.success("✅ File se gyaan prapt ho gaya!")
    st.text_area("📖 Extracted Content:", text_content[:3000], height=300)

# Chat History
if 'history' not in st.session_state:
    st.session_state.history = []

def google_search_answer(query):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(f"https://www.google.com/search?q={query}", headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')

        for cls in [
            "BNeawe iBp4i AP7Wnd",
            "BNeawe s3v9rd AP7Wnd",
            "kno-rdesc",
            "Z0LcW",
            "BVG0Nb"
        ]:
            ans = soup.find("div", class_=cls)
            if ans:
                return ans.get_text()

        paragraphs = soup.find_all("p")
        if paragraphs:
            return paragraphs[0].get_text()

        # Try Wikipedia as fallback
        summary = wikipedia.summary(query, sentences=2, auto_suggest=True, redirect=True)
        return summary

    except Exception as e:
        return f"❌ Maaf kijiye, kuch samasya aayi hai: {str(e)}"

def local_chat(prompt):
    return None

with st.form("chat_form", clear_on_submit=True):
    cols = st.columns([8, 1])
    with cols[0]:
        user_q_multi = st.text_area("", key="chat_input", placeholder="🤖 Aap apne prashn yahan likhiye (Enter se bhejein)...")
    with cols[1]:
        submitted = st.form_submit_button("↵")

if submitted and user_q_multi:
    questions = [q.strip() for q in user_q_multi.split('\n') if q.strip()]
    for user_q in questions:
        st.session_state.history.append(("user", user_q))
        st.markdown(f"👤 Aapka Prashn: *{user_q}*")
        response = ""

        greetings = ["hello", "hi", "hlo", "ram ram", "jai shree ram", "namaste", "jai jagannath"]
        if any(greet in user_q.lower() for greet in greetings):
            response = "🤖 Gyani: Jai Jagannath 🙏 Aapka swagat hai! Aap kya janna chahenge?"
        elif user_q.lower() in text_content.lower():
            response = "🤖 Gyani: Bahut accha prashn! Haan, iska uttar mujhe aapke file me mil gaya hai. 👇"
        elif any(k in user_q.lower() for k in ["python", "java", "html", "c++", "javascript", "c language"]):
            response = "🤖 Gyani: Aapne coding ka prashn kiya hai. Filhal advanced coding AI disabled hai (OpenAI API key chahiye)."
        elif "cbse syllabus" in user_q.lower():
            response = "🤖 Gyani: Yeh raha CBSE board ka Class 1 se 12 tak ka syllabus summary link 👇\n👉 https://cbseacademic.nic.in/curriculum_2025.html"
        elif any(kiss in user_q.lower() for kiss in ["kiss", "kissing", "chumban", "चुंबन"]):
            response = "🤖 Gyani: Chumban ya pyaar se jude sawalon ke liye aapka prashn samanya gyaan mein nahi aata, par yeh ek rochak vishay hai. Samanya roop se pyaar, samman aur sahmati par adharit sambandhon ka gyaan dena bhi zaroori hai."
        elif "gyani kaun hai" in user_q.lower() or "kisne banaya" in user_q.lower() or "ballo ai kaun hai" in user_q.lower():
            response = "🤖 Gyani: Main ek AI chatbot hoon jise Pradeep Vaishnav ne banaya hai. Mera uddeshya logo ko sahayata dena aur unki gyaan ki pyaas bujhana hai."
        else:
            response = google_search_answer(user_q)

        st.success("🤖 Gyani: " + response)
        st.session_state.history.append(("gyani", response))

# Display full conversation
st.markdown("<hr><h4>📜 Purani Baatein:</h4>", unsafe_allow_html=True)
for speaker, msg in st.session_state.history:
    if speaker == "user":
        st.markdown(f"👤 **User**: {msg}")
    else:
        st.markdown(f"🤖 **Gyani**: {msg}")

st.markdown("""
    <hr>
    <div style='text-align: center; color: gray;'>
        🤖 <strong>Gyani</strong> Chatbot ka nirmaan <strong>Pradeep Vaishnav</strong> dwara kiya gaya hai.<br>
        Iska uddeshya logo ko gyaan dena aur unki samasyaon ka samadhan karna hai.<br>
        Jai Jagannath 🙏
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <div style='margin-top:30px;'>
        <h4>📝 Aap yeh prashn bhi pooch sakte hain:</h4>
        <ul>
            <li>Python me loop kaise chalta hai?</li>
            <li>Newton ka pehla niyam kya hai?</li>
            <li>HTML ka basic structure kya hota hai?</li>
            <li>Is file me syllabus hai kya?</li>
            <li>Java me factorial kaise likhen?</li>
            <li>CBSE syllabus class 6 science</li>
            <li>Class 10 Maths syllabus CBSE</li>
            <li>12th Physics important topics CBSE</li>
        </ul>
    </div>
""", unsafe_allow_html=True)

st.markdown(f"<p style='text-align: right; font-size: small; color: gray;'>🕒 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>", unsafe_allow_html=True)
