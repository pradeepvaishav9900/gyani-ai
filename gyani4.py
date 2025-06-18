import streamlit as st
import PyPDF2
import pytesseract
from PIL import Image, ImageFilter
import datetime
import openai
import os

st.set_page_config(page_title="Gyani - AI Assistant by Pradeep Vaishnav", page_icon="🤖")

# Logo and Title
st.markdown("""
    <div style='text-align: center;'>
        <img src='NEW_LOGO_URL_HERE' alt='Gyani Logo' width='120'/><br>
        <h1 style='margin-top: 10px;'>🤖 Gyani</h1>
        <h4 style='color: gray;'>Developed by Pradeep Vaishnav</h4>
        <p style='font-size: 14px; color: #555;'>Gyani ek AI sahayak hai jo Pradeep Vaishnav dwara banaya gaya hai. Iska uddeshya logo ko gyaan dena aur unki samasyaon ka samadhan karna hai.</p>
        <p style='font-size: 13px; color: #999;'>Creator & Owner: <strong>Pradeep Vaishnav</strong></p>
    </div>
    <hr>
""", unsafe_allow_html=True)

# Image Upload and Editing
st.header("🖼️ Image Editing")
uploaded_image = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

if uploaded_image is not None:
    # Open the image
    image = Image.open(uploaded_image)
    st.image(image, caption="Original Image", use_column_width=True)

    # Image Editing Options
    st.subheader("Edit Your Image")
    edit_option = st.selectbox("Choose an editing option", ["None", "Resize", "Blur", "Enhance"])

    if edit_option == "Resize":
        width = st.number_input("Width", min_value=1, value=image.width)
        height = st.number_input("Height", min_value=1, value=image.height)
        if st.button("Resize Image"):
            resized_image = image.resize((width, height))
            st.image(resized_image, caption="Resized Image", use_column_width=True)

    elif edit_option == "Blur":
        if st.button("Apply Blur"):
            blurred_image = image.filter(ImageFilter.BLUR)
            st.image(blurred_image, caption="Blurred Image", use_column_width=True)

    elif edit_option == "Enhance":
        if st.button("Enhance Image"):
            enhanced_image = image.filter(ImageFilter.SHARPEN)
            st.image(enhanced_image, caption="Enhanced Image", use_column_width=True)

# Text Extraction
col1, col2 = st.columns([8, 1])
with col1:
    uploaded_file = st.file_uploader("Upload a PDF or Image for Text Extraction", type=["pdf", "png", "jpg", "jpeg"], label_visibility="collapsed")
with col2:
    st.markdown("<div style='text-align: right; font-size: 22px;'>➕</div>", unsafe_allow_html=True)

text_content = ""

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

def generate_response(user_q):
    # Normalize the user question for easier matching
    user_q = user_q.lower()

    # Simple knowledge base
    knowledge_base = {
        "python me loop kaise chalta hai": "Python me loop chalanay ke liye 'for' ya 'while' loop ka istemal hota hai. Example: for i in range(5): print(i)",
        "newton ka pehla niyam kya hai": "Newton ka pehla niyam kehta hai ki ek vastu tab tak apni sthiti ya gati ko nahi badlegi jab tak uspe koi bahari bal nahi lagta.",
        "html ka basic structure kya hota hai": "HTML ka basic structure kuch is prakar hota hai: <html>, <head>, <title>, <body>.",
        "java me factorial kaise likhen": "Java me factorial likhne ke liye aap recursion ya loop ka istemal kar sakte hain. Example: public int factorial(int n) { return (n == 1) ? 1 : n * factorial(n - 1); }",
        "cbse syllabus class 6 science": "CBSE syllabus class 6 science me topics jaise ki 'Food', 'Materials', 'The World of Animals', aur 'Natural Resources' shamil hain.",
        "class 10 maths syllabus cbse": "Class 10 maths syllabus me 'Real Numbers', 'Polynomials', 'Linear Equations', aur 'Quadratic Equations' shamil hain.",
        "12th physics important topics cbse": "12th physics me 'Electrostatics', 'Current Electricity', 'Magnetic Effects of Current', aur 'Optics' jaise topics important hain."
    }

    # Check if the question is in the knowledge base
    if user_q in knowledge_base:
        return f"🤖 Gyani: {knowledge_base[user_q]} Kya aapko is vishay par aur kuch janna hai?"

    # Handle casual conversational prompts
    conversational_prompts = [
        "or batao", "kya ho raha hai", "kya chal raha hai", "kya naya hai", 
        "kya haal hai", "kya scene hai", "kesa hai", "kese ho", "kya haal chaal hai"
    ]
    if any(prompt in user_q for prompt in conversational_prompts):
        return "🤖 Gyani: Main theek hoon, dhanyavaad! Aap kaise hain? Aapko kya jaanana hai?"

    # Handle greetings and casual inquiries
    greetings = ["hello", "hi", "ram ram", "jai shree ram", "namaste", "jai jagannath"]
    if any(greet in user_q for greet in greetings):
        return "🤖 Gyani: Main theek hoon, dhanyavaad! Aap kaise hain? Kya aapko kisi vishay par madad chahiye?"

    return "🤖 Gyani: Maaf kijiye, mujhe is prashn ka uttar nahi pata. Kya aap kuch aur poochna chahenge?"

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
        response = generate_response(user_q)
        st.success(response)
        st.session_state.history.append(("gyani", response))

# Display full conversation
st.markdown("<hr><h4>📜 Purani Baatein:</h4>", unsafe_allow_html=True)
for speaker, msg in st.session_state.history:
    if speaker == "user":
        st.markdown(f"👤 **User      **: {msg}")
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
            <li>Java me factorial kaise likhen?</li>
            <li>CBSE syllabus class 6 science</li>
            <li>Class 10 Maths syllabus CBSE</li>
            <li>12th Physics important topics CBSE</li>
        </ul>
    </div>
""", unsafe_allow_html=True)

st.markdown(f"<p style='text-align: right; font-size: small; color: gray;'>🕒 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>", unsafe_allow_html=True)
