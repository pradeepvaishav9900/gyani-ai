import streamlit as st
import pytesseract
from PIL import Image
import requests
import json

# ======== CONFIG ========
GROQ_API_KEY = "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"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "llama-3-70b-8192"  # you can also try mixtral-8x7b

# ======== UI ========
st.set_page_config(page_title="Board Answer Checker", page_icon="📘", layout="wide")
st.title("📘 Student Answer Checker (Board-Style)")

# Question bank example
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

selected_q = st.selectbox("Select a Question:", list(questions.keys()))
question_data = questions[selected_q]

st.write(f"**Question:** {question_data['text']}")
st.write("📘 Model Answer (for reference):", question_data['model_answer'])

# Answer input
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

# Grading button
if st.button("✅ Grade My Answer"):
    if not student_answer.strip():
        st.warning("Please provide an answer first.")
    else:
        with st.spinner("Evaluating your answer..."):
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
                        Question: {question_data['text']}
                        Max marks: {question_data['rubric']['max_marks']}
                        Model Answer: {question_data['model_answer']}
                        Student Answer: {student_answer}
                        
                        Rubric: {question_data['rubric']['criteria']}
                        
                        Return JSON:
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
                data = response.json()
                try:
                    result_text = data['choices'][0]['message']['content']
                    st.subheader("📊 Evaluation Result")
                    st.json(json.loads(result_text))  # parse JSON from model
                except Exception as e:
                    st.error("Error parsing the response. Raw response:")
                    st.code(data)
            else:
                st.error(f"Error: {response.status_code}")
                st.text(response.text)
