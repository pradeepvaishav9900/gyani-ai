import streamlit as st
import PyPDF2
import pytesseract
from PIL import Image
import io
import base64
import datetime
import requests
from langdetect import detect

st.set_page_config(page_title="Ballo AI - AI Assistant by Pradeep Vaishnav", page_icon="🤖")

# Logo and Title
st.markdown("""
    <div style='text-align: center;'>
        <img src='https://i.imgur.com/Wr9vB2M.png' alt='Ballo AI Logo' width='120'/><br>
        <h1 style='margin-top: 10px;'>🤖 Ballo AI</h1>
        <h4 style='color: gray;'>Developed by Pradeep Vaishnav</h4>
        <p style='font-size: 14px; color: #555;'>Ballo AI ek AI sahayak hai jo Pradeep Vaishnav dwara banaya gaya hai. Iska uddeshya logo ko gyaan dena aur unki samasyaon ka samadhan karna hai.</p>
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
    with st.spinner("📚 Ballo AI file ka vishleshan kar raha hai..."):
        if file_type == "application/pdf":
            text_content = extract_text_from_pdf(uploaded_file)
        elif "image" in file_type:
            text_content = extract_text_from_image(uploaded_file)

    st.success("✅ File se gyaan prapt ho gaya!")
    st.text_area("📖 Extracted Content:", text_content[:3000], height=300)

# Chat History
if 'history' not in st.session_state:
    st.session_state.history = []

def local_chat(prompt):
    return "🔒 Ballo AI ka AI engine filhal offline hai. OpenAI key ki jarurat hai advance uttar ke liye."

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
            response = "🤖 Ballo AI: Jai Jagannath 🙏 Aapka swagat hai! Aap kya janna chahenge?"
            st.success(response)
        elif user_q.lower() in text_content.lower():
            response = "🤖 Ballo AI: Bahut accha prashn! Haan, iska uttar mujhe aapke file me mil gaya hai. 👇"
            st.success(response)
        elif any(k in user_q.lower() for k in ["python", "java", "html", "c++", "javascript", "c language"]):
            if any(x in user_q.lower() for x in ["code", "program", "likho", "likhna", "bana"]):
                st.markdown("🤖 Ballo AI: Aapne coding ka prashn kiya hai. Filhal advanced coding AI disabled hai (OpenAI API key chahiye).")
                st.info("Lekin main kuch basic udaharan de raha hoon:")
                if "python" in user_q.lower():
                    st.code("for i in range(5):\n    print(i)", language="python")
                elif "java" in user_q.lower():
                    st.code("public class Main {\n public static void main(String[] args) {\n  System.out.println(\"Hello\");\n }\n}", language="java")
                elif "html" in user_q.lower():
                    st.code("<html><body>Hello</body></html>", language="html")
                elif "c++" in user_q.lower():
                    st.code("#include<iostream>\nusing namespace std;\nint main() {\n cout << \"Hello\";\n return 0;\n}", language="cpp")
                elif "javascript" in user_q.lower():
                    st.code("console.log('Hello World');", language="javascript")
                elif "c language" in user_q.lower():
                    st.code("#include<stdio.h>\nint main() {\n printf(\"Hello\");\n return 0;\n}", language="c")
            else:
                response = "🤖 Ballo AI: Yeh technical coding ya vishay sambandhit prashn hai. Basic code niche diya gaya hai."
                st.info(response)
        elif "cbse syllabus" in user_q.lower():
            response = "🤖 Ballo AI: Yeh raha CBSE board ka Class 1 se 12 tak ka syllabus summary link 👇\n👉 https://cbseacademic.nic.in/curriculum_2025.html"
            st.success(response)
        elif any(kiss in user_q.lower() for kiss in ["kiss", "kissing", "chumban", "चुंबन"]):
            response = "🤖 Ballo AI: Chumban ya pyaar se jude sawalon ke liye aapka prashn samanya gyaan mein nahi aata, par yeh ek rochak vishay hai. Samanya roop se pyaar, samman aur sahmati par adharit sambandhon ka gyaan dena bhi zaroori hai."
            st.success(response)
        elif "ballo ai kaun hai" in user_q.lower() or "kisne banaya" in user_q.lower():
            response = "🤖 Ballo AI: Main ek AI chatbot hoon jise Pradeep Vaishnav ne banaya hai. Mera uddeshya logo ko sahayata dena aur unki gyaan ki pyaas bujhana hai."
            st.success(response)
        else:
            response = local_chat(user_q)
            st.success("🤖 Ballo AI: " + response)

        st.session_state.history.append(("ballo", response))

# Display full conversation
st.markdown("<hr><h4>📜 Purani Baatein:</h4>", unsafe_allow_html=True)
for speaker, msg in st.session_state.history:
    if speaker == "user":
        st.markdown(f"👤 **User**: {msg}")
    else:
        st.markdown(f"🤖 **Ballo AI**: {msg}")

st.markdown("""
    <hr>
    <div style='text-align: center; color: gray;'>
        🤖 <strong>Ballo AI</strong> Chatbot ka nirmaan <strong>Pradeep Vaishnav</strong> dwara kiya gaya hai.<br>
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
