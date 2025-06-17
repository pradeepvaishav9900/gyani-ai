import streamlit as st
import PyPDF2
import pytesseract
from PIL import Image
import io
import base64

st.set_page_config(page_title="Gyani - AI Assistant by Pradeep Vaishnav", page_icon="🧠")

# Logo and Title Section (audio removed)
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
    with st.spinner("Gyani file ka vishleshan kar raha hai..."):
        if file_type == "application/pdf":
            text_content = extract_text_from_pdf(uploaded_file)
        elif "image" in file_type:
            text_content = extract_text_from_image(uploaded_file)

    st.success("✅ File se gyaan prapt ho gaya!")
    st.text_area("📖 Extracted Content:", text_content[:3000], height=300)

user_q = st.text_input("🧠 Aapka Prashn likhiye:")
if user_q:
    if user_q.lower() in text_content.lower():
        st.success("✅ Gyani: Haan, iska uttar file me mil gaya hai!")
    elif any(k in user_q.lower() for k in ["python", "java", "html", "chemistry", "physics"]):
        st.info("🧠 Gyani: Yeh prashn technical hai, main iska basic jawab de raha hoon:")
        if "python" in user_q.lower():
            st.code("for i in range(5):\n    print(i)", language="python")
        elif "java" in user_q.lower():
            st.code("public class Main {\n public static void main(String[] args) {\n  System.out.println(\"Hello\");\n }\n}", language="java")
        elif "html" in user_q.lower():
            st.code("<html><body>Hello</body></html>", language="html")
        elif "physics" in user_q.lower():
            st.markdown("Newton ka doosra niyam: **F = m × a**")
        elif "chemistry" in user_q.lower():
            st.markdown("Acid ka pH hota hai < 7, jaise HCl.")
    else:
        st.warning("Gyani: Maaf kijiye, mujhe iss prashn ka sahi uttar nahi mila.")

st.markdown("""
    <hr>
    <p style='text-align: center; color: gray;'>
        🤖 <strong>Gyani</strong> Chatbot ka nirmaan <strong>Pradeep Vaishnav</strong> dwara kiya gaya hai.<br>
        Jai Jagannath 🙏
    </p>
""", unsafe_allow_html=True)
