import streamlit as st
from PIL import Image
import pytesseract
import requests
import json
import math
import time

st.set_page_config(page_title="Board-style Answer Checker", page_icon="📘", layout="wide")
st.title("📘 Board-Style Answer Checker — MCQ + Subjective (Groq LLM + OCR)")

# ------------------------
# Sidebar: API key & options
# ------------------------
st.sidebar.header("Settings & API")
api_key_input = st.sidebar.text_input("Groq API Key (paste here or set in secrets)", type="password")
MODEL_CHOICES = ["llama-3-70b-8192", "mixtral-8x7b", "llama3-8b-8192"]
model = st.sidebar.selectbox("Choose Groq Model", MODEL_CHOICES)
temperature = st.sidebar.slider("Temperature (LLM creativity)", 0.0, 1.0, 0.2)
max_tokens = st.sidebar.number_input("Max tokens (response)", min_value=200, max_value=4000, value=800, step=100)

# Prefer secrets over typed key
def get_groq_key():
    if "GROQ_API_KEY" in st.secrets:
        return st.secrets["GROQ_API_KEY"]
    return api_key_input.strip()

GROQ_API_KEY = get_groq_key()
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

if not GROQ_API_KEY:
    st.sidebar.warning("Please provide your Groq API key in sidebar or in Streamlit secrets (GROQ_API_KEY).")

# ------------------------
# Example question bank (you can expand)
# ------------------------
st.sidebar.header("Example Question Bank")
default_bank = {
    "Long - Newton II (5 marks)": {
        "type": "subjective",
        "text": "Explain Newton's Second Law of Motion with an example.",
        "max_marks": 5,
        "model_answer": "Newton's Second Law states that net force equals mass times acceleration (F = ma). Example: pushing a box causes acceleration proportional to applied force."
    },
    "Short - Photosynthesis (4 marks)": {
        "type": "subjective",
        "text": "What is photosynthesis? Write its balanced equation.",
        "max_marks": 4,
        "model_answer": "Photosynthesis: process by which green plants synthesize food using sunlight, CO2 and water. Equation: 6CO2 + 6H2O -> C6H12O6 + 6O2"
    },
    "MCQ - Earth's axis tilt": {
        "type": "mcq",
        "text": "The tilt of Earth's axis is approximately:",
        "options": ["23.5°", "0°", "45°", "90°"],
        "correct": "23.5°",
        "max_marks": 1,
        "negative_mark": 0.0
    }
}

use_bank = st.sidebar.checkbox("Use built-in example bank", value=True)
if use_bank:
    selected_key = st.sidebar.selectbox("Pick a sample question (sidebar)", list(default_bank.keys()))
    sample = default_bank[selected_key]
else:
    sample = None

# ------------------------
# Main UI: choose/create question
# ------------------------
st.subheader("1) Question (Choose sample or enter your own)")

q_type = st.selectbox("Question type", ["subjective", "mcq"]) if not sample else sample["type"]
if sample:
    question_text = st.text_area("Question text", value=sample["text"], height=100)
else:
    question_text = st.text_area("Question text", height=100)

if q_type == "mcq":
    st.write("MCQ settings")
    if sample and "options" in sample:
        options = sample["options"]
    else:
        raw_opts = st.text_area("Enter options (one per line)", value="Option A\nOption B\nOption C\nOption D", height=100)
        options = [o.strip() for o in raw_opts.splitlines() if o.strip()]
    if sample and "correct" in sample:
        correct_option = sample["correct"]
    else:
        correct_option = st.selectbox("Select correct option (for teacher reference)", options)
    max_marks = st.number_input("Max marks for MCQ", min_value=0.0, value=float(sample.get("max_marks", 1.0) if sample else 1.0))
    negative_mark = st.number_input("Negative marking (per wrong)", min_value=0.0, value=float(sample.get("negative_mark", 0.0) if sample else 0.0))
else:
    st.write("Subjective settings")
    max_marks = st.number_input("Max marks for subjective question", min_value=1.0, value=float(sample.get("max_marks", 5.0) if sample else 5.0))
    model_answer = st.text_area("Model answer / key points (give bullet points or full answer)", value=(sample.get("model_answer","") if sample else ""), height=150)

# ------------------------
# Student answer input (text or image OCR)
# ------------------------
st.subheader("2) Student Answer (type or upload image)")
input_mode = st.radio("Answer input mode", ["Type Answer", "Upload Image (handwritten/photo)"])

student_answer_text = ""
if input_mode == "Type Answer":
    student_answer_text = st.text_area("Student answer text", height=200)
else:
    uploaded_img = st.file_uploader("Upload image (jpg/png). OCR will be used.", type=["jpg","jpeg","png"])
    if uploaded_img:
        try:
            img = Image.open(uploaded_img)
            st.image(img, caption="Uploaded answer (preview)", use_column_width=True)
            with st.spinner("Running OCR (pytesseract)..."):
                # pytesseract configuration can be adjusted e.g., lang="eng+hin"
                student_answer_text = pytesseract.image_to_string(img)
                time.sleep(0.5)
            st.text_area("OCR extracted text (editable)", value=student_answer_text, height=200)
        except Exception as e:
            st.error(f"OCR error: {e}")

# ------------------------
# Helper: call Groq
# ------------------------
def call_groq(model, messages, temperature=0.2, max_tokens=800):
    key = GROQ_API_KEY
    if not key:
        return {"error": "No Groq API key provided."}
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    try:
        r = requests.post(GROQ_URL, headers=headers, json=payload, timeout=60)
        if r.status_code != 200:
            return {"error": f"Groq API error {r.status_code}: {r.text}"}
        return r.json()
    except Exception as e:
        return {"error": str(e)}

# ------------------------
# Grading logic
# ------------------------
st.subheader("3) Grade (Run)")
if st.button("Grade Answer"):
    if not question_text.strip():
        st.warning("Please enter the question text.")
    elif (not student_answer_text or not student_answer_text.strip()):
        st.warning("Please provide the student's answer (text or image).")
    else:
        if q_type == "mcq":
            # simple MCQ check
            chosen_option = st.selectbox("Assume student selected:", options)
            # compute score
            score = float(max_marks) if chosen_option == correct_option else -float(negative_mark)
            score = max(score, 0.0)  # don't allow negative final
            st.success(f"MCQ Result: {score} / {max_marks}")
            st.write("**Correct option:**", correct_option)
            if chosen_option != correct_option:
                st.info("Explanation: The correct answer is shown above. Student marked wrong.")
        else:
            # Subjective: build rubric & prompt and call Groq
            rubric = {
                "max_marks": float(max_marks),
                "criteria": {
                    "content_correctness": round(0.5 * float(max_marks), 2),
                    "method_steps": round(0.3 * float(max_marks), 2),
                    "presentation": round(0.1 * float(max_marks), 2),
                    "language_keywords": round(0.1 * float(max_marks), 2)
                }
            }
            # normalize criteria to sum to max_marks
            s = sum(rubric["criteria"].values())
            if s != rubric["max_marks"]:
                factor = rubric["max_marks"] / s
                for k in rubric["criteria"]:
                    rubric["criteria"][k] = round(rubric["criteria"][k] * factor, 2)

            st.write("Using rubric:", rubric)

            # Build prompt carefully — ask for JSON only
            few_shot = """
You are a strict board-level examiner. Grade the student answer strictly according to the rubric and model answer.
Return ONLY a JSON object (no extra text) with keys:
- scores: {content_correctness:float, method_steps:float, presentation:float, language_keywords:float}
- total_score: float
- missing_points: [list of missing key points]
- mistakes: [list of mistakes or incorrect statements]
- improvement: short advice (one or two sentences)
Make numeric scores sum to max_marks (allow decimals). Cap at max_marks.
"""
            prompt_user = f"""
Question: {question_text}

Model answer / key points: {model_answer}

Rubric (max marks = {rubric['max_marks']}): {json.dumps(rubric['criteria'])}

Student answer: {student_answer_text}

Return the JSON as described.
"""

            messages = [
                {"role": "system", "content": few_shot},
                {"role": "user", "content": prompt_user}
            ]

            with st.spinner("Calling Groq for grading... (may take a few seconds)"):
                groq_resp = call_groq(model=model, messages=messages, temperature=temperature, max_tokens=max_tokens)

            # handle errors
            if isinstance(groq_resp, dict) and "error" in groq_resp:
                st.error("Groq API error: " + groq_resp["error"])
            else:
                # parse model's content
                try:
                    content = groq_resp["choices"][0]["message"]["content"]
                except Exception:
                    st.error("Unexpected Groq response format.")
                    st.write(groq_resp)
                    content = None

                if content:
                    # Try to extract JSON from content robustly
                    parsed = None
                    try:
                        parsed = json.loads(content.strip())
                    except Exception:
                        # attempt to find first { ... } in text
                        try:
                            start = content.index("{")
                            end = content.rindex("}") + 1
                            parsed = json.loads(content[start:end])
                        except Exception as e:
                            st.warning("Could not parse JSON directly. Showing raw LLM output for debugging.")
                            st.code(content)
                            parsed = None

                    if parsed:
                        # sanity: cap total_score
                        total = float(parsed.get("total_score", 0.0))
                        total = max(0.0, min(total, rubric["max_marks"]))
                        parsed["total_score"] = round(total, 2)
                        st.subheader("📊 Grading Result")
                        st.write(f"**Total:** {parsed['total_score']} / {rubric['max_marks']}")
                        st.markdown("**Breakdown:**")
                        st.json(parsed.get("scores", {}))
                        st.markdown("**Missing Points:**")
                        st.write(parsed.get("missing_points", []))
                        st.markdown("**Mistakes:**")
                        st.write(parsed.get("mistakes", []))
                        st.markdown("**Improvement Tip:**")
                        st.write(parsed.get("improvement", ""))
                        # Option: let teacher override (simple input)
                        override = st.checkbox("Teacher override marks?")
                        if override:
                            new_mark = st.number_input("Enter corrected total marks", min_value=0.0, max_value=rubric["max_marks"], value=parsed["total_score"])
                            if st.button("Save override"):
                                st.success(f"Saved override marks: {new_mark} / {rubric['max_marks']}")
                    else:
                        st.error("Failed to parse model output into JSON. See raw output above.")
