import streamlit as st
import pytesseract
from PIL import Image
import requests
import json

# -----------------------
# CONFIG
# -----------------------
# Groq API Key
# For security, best: st.secrets["GROQ_API_KEY"]
GROQ_API_KEY = "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"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "llama-3-70b-8192"  # or "mixtral-8x7b"

# -----------------------
# AUTHENTICATION (Simple Demo)
# -----------------------
# Temporary authentication without streamlit-authenticator
# Replace with real auth for production
if 'auth_status' not in st.session_state:
    st.session_state['auth_status'] = False
    st.session_state['username'] = ""

def login():
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if username == "student" and password == "student123":
            st.session_state['auth_status'] = True
            st.session_state['username'] = username
            st.sidebar.success(f"Welcome {username}!")
        elif username == "admin" and password == "admin123":
            st.session_state['auth_status'] = True
            st.session_state['username'] = username
            st.sidebar.success(f"Welcome {username}!")
        else:
            st.sidebar.error("Invalid credentials")

if not st.session_state['auth_status']:
    login()
    st.stop()

username = st.session_state['username']

# -----------------------
# QUESTION BANK
# -----------------------
questions = {
    "Q1": {
        "text": "Explain Newton's Second Law of Motion with an example.",
        "rubric": {"max_marks": 5, "criteria": ["content_correctness", "method_steps", "presentation", "language_keywords"]},
        "model_answer": "Newton's Second Law states that the rate of change of momentum is directly proportional to the applied force and takes place in the direction of force. Formula: F = ma. Example: pushing a car."
    },
    "Q2": {
        "text": "What is Photosynthesis? Write its equation.",
        "rubric": {"max_marks": 5, "criteria": ["content_correctness", "equation", "presentation"]},
        "model_answer": "Photosynthesis is the process by which green plants make food using sunlight, water, and CO2. Equation: 6CO2 + 6H2O → C6H12O6 + 6O2"
    }
}

# -----------------------
# Groq Grading Function
# -----------------------
def grade_with_groq(question, rubric, model_answer, student_answer):
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": "You are an experienced CBSE board teacher. Grade strictly according to the rubric and return JSON."
            },
            {
                "role": "user",
                "content": f"""
Question: {question}
Max marks: {rubric.get('max_marks')}
Model Answer: {model_answer}
Student Answer: {student_answer}

Rubric: {rubric['criteria']}

Return JSON like:
{{
 "scores": {{"content_correctness":float, "method_steps":float, "presentation":float}},
 "total_score":float,
 "missing_points":[...],
 "mistakes":[...],
 "improvement":"..."
}}
"""
            }
        ]
    }
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    response = requests.post(GROQ_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error from Groq API: {response.status_code}")
        st.text(response.text)
        return None

# -----------------------
# MAIN APP
# -----------------------
st.title("📘 Board Answer Checker (Student/Teacher)")

selected_q = st.selectbox("Select a Question:", list(questions.keys()))
question_data = questions[selected_q]

st.write(f"**Question:** {question_data['text']}")
st.write("📘 Model Answer (Reference):", question_data['model_answer'])

# -----------------------
# Answer Input
# -----------------------
answer_mode = st.radio("Choose Answer Input Mode:", ["Type Answer", "Upload Image"])
student_answer = ""

if answer_mode == "Type Answer":
    student_answer = st.text_area("Write your answer here:", height=150)
elif answer_mode == "Upload Image":
    uploaded_img = st.file_uploader("Upload your handwritten answer (image)", type=["jpg", "jpeg", "png"])
    if uploaded_img:
        img = Image.open(uploaded_img)
        st.image(img, caption="Uploaded Answer")
        st.write("Extracting text from image...")
        student_answer = pytesseract.image_to_string(img)
        st.text_area("Extracted Answer (editable):", student_answer, height=150)

# -----------------------
# Grading Button
# -----------------------
if st.button("✅ Grade My Answer"):
    if not student_answer.strip():
        st.warning("Please provide an answer first.")
    else:
        with st.spinner("Evaluating your answer..."):
            result = grade_with_groq(question_data['text'], question_data['rubric'], question_data['model_answer'], student_answer)
            if result:
                try:
                    result_text = result['choices'][0]['message']['content']
                    st.subheader("📊 Evaluation Result")
                    st.json(json.loads(result_text))
                except Exception as e:
                    st.error("Error parsing response. Raw response below:")
                    st.code(result)

# -----------------------
# Teacher Dashboard
# -----------------------
if username == "admin":
    st.subheader("🔧 Teacher Dashboard: Override Marks")
    override_student_answer = st.text_area("Student Answer to override / test grading:", height=150)
    if st.button("💾 Override Test Grading"):
        st.success("This is a placeholder. In a real app, you can save edited marks to DB.")
