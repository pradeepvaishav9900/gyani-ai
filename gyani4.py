import streamlit as st
import PyPDF2
import pytesseract
from PIL import Image
import io
import base64
import datetime
import openai
from openai._exceptions import OpenAIError

st.set_page_config(page_title="Gyani - AI Assistant by Pradeep Vaishnav", page_icon="🧠")

# Set OpenAI API key from Streamlit secrets
api_key = st.secrets.get("OPENAI_API_KEY")
if api_key:
    openai.api_key = api_key
else:
    st.warning("🔐 OpenAI API key missing! Add it in .streamlit/secrets.toml")

# Logo and Title
st.markdown("""
    <div style='text-align: center;'>
        <img src='https://i.imgur.com/Wr9vB2M.png' alt='Gyani Logo' width='120'/><br>
        <h1 style='margin-top: 10px;'>🧠 Gyani</h1>
        <h4 style='color: gray;'>Developed by Pradeep Vaishnav</h4>
    </div>
    <hr>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("📤 File Upload karein (PDF ya Image):", type=["pdf", "png", "jpg", "jpeg"])

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

text_content = ""

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

user_q = st.text_input("🧠 Aapka Prashn likhiye:")
if user_q:
    st.session_state.history.append(("user", user_q))
    st.markdown(f"👤 Aapka Prashn: *{user_q}*")
    response = ""

    if user_q.lower() in text_content.lower():
        response = "🧠 Gyani: Bahut accha prashn! Haan, iska uttar mujhe aapke file me mil gaya hai. 👇"
        st.success(response)
    elif any(k in user_q.lower() for k in ["python", "java", "html", "chemistry", "physics"]):
        response = "🧠 Gyani: Hmm... Yeh ek technical prashn lagta hai. Chaliye, main aapko iske baare mein thoda batata hoon:"
        st.info(response)
        if "python" in user_q.lower():
            st.code("for i in range(5):\n    print(i)", language="python")
        elif "java" in user_q.lower():
            st.code("public class Main {\n public static void main(String[] args) {\n  System.out.println(\"Hello\");\n }\n}", language="java")
        elif "html" in user_q.lower():
            st.code("<html><body>Hello</body></html>", language="html")
        elif "physics" in user_q.lower():
            st.markdown("📘 Newton ka doosra niyam: **F = m × a** (Bal = Dravya × Veegh)")
        elif "chemistry" in user_q.lower():
            st.markdown("🧪 Acid ka pH value hota hai **7 se kam**, jaise ki **HCl** ek strong acid hai.")
    elif api_key:
        try:
            chat_response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are Gyani, a wise assistant who explains in Hindi like a human teacher."},
                    {"role": "user", "content": user_q}
                ]
            )
            response = chat_response.choices[0].message.content
            st.success("🧠 Gyani: " + response)
        except OpenAIError as e:
            response = "❌ Gyani abhi sthir hai. Error: " + str(e)
            st.error(response)
    else:
        response = "🧠 Gyani: Mujhe khed hai, yeh prashn mujhe file me ya mere gyaan me nahi mila. Par main aur seekh raha hoon – aap mujhe naye sawal poochhte rahiye! 🙏"
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

st.markdown(f"<p style='text-align: right; font-size: small; color: gray;'>🕒 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>", unsafe_allow_html=True)
