import os
import io
import json
import time
import math
from typing import List
from PIL import Image
import pytesseract
import requests
import streamlit as st
from PyPDF2 import PdfReader
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# ----------------------------
# App config (no sidebar)
# ----------------------------
st.set_page_config(page_title="Board-style Checker (No Sidebar)", page_icon="📘", layout="wide")
st.title("📘 Board-style Answer Checker — Upload Questions & Get Marks")
st.markdown("**How to use:** Upload questions (PDF/TXT) or type questions, then select a question, provide student's answer (type or upload image), and click **Grade**. Use Streamlit Secrets (`GROQ_API_KEY`) in production.")

# ----------------------------
# Groq API key (secure)
# ----------------------------
def get_groq_key():
    # prefer Streamlit secrets -> environment -> runtime input
    key = None
    try:
        key = st.secrets["GROQ_API_KEY"]
    except Exception:
        key = os.environ.get("GROQ_API_KEY")
    if not key:
        # show small input at top of page (not sidebar) for quick local runs
        key = st.text_input("Groq API Key (or set GROQ_API_KEY in Streamlit Secrets / env)", type="password")
    return key.strip() if key else ""

GROQ_API_KEY = get_groq_key()
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = "llama-3-70b-8192"

# ----------------------------
# Helpers: PDF/text extraction
# ----------------------------
def extract_text_from_pdf(uploaded_file) -> str:
    try:
        reader = PdfReader(uploaded_file)
        text = []
        for page in reader.pages:
            txt = page.extract_text()
            if txt:
                text.append(txt)
        return "\n\n".join(text)
    except Exception as e:
        st.error(f"PDF parsing error: {e}")
        return ""

def load_questions_from_txt_or_pdf(uploaded_files) -> List[str]:
    questions = []
    for f in uploaded_files:
        name = f.name.lower()
        if name.endswith(".pdf"):
            txt = extract_text_from_pdf(f)
        else:
            raw = f.read()
            if isinstance(raw, bytes):
                try:
                    txt = raw.decode("utf-8")
                except:
                    txt = raw.decode("latin-1", errors="ignore")
            else:
                txt = str(raw)
        # split heuristically into questions by blank lines or lines starting with Q.
        blocks = [b.strip() for b in txt.split("\n\n") if b.strip()]
        # further split long blocks by "Q." or "Q" lines if present
        refined = []
        for b in blocks:
            # try common separators
            if "\nQ" in b:
                parts = [p.strip() for p in b.split("\nQ") if p.strip()]
                refined.extend(parts)
            else:
                refined.append(b)
        questions.extend(refined)
    return questions

# ----------------------------
# OCR helper (images)
# ----------------------------
def ocr_image_to_text(uploaded_image) -> str:
    try:
        img = Image.open(uploaded_image).convert("RGB")
        # basic OCR; if Hindi needed, user must have Hindi tesseract traineddata on host
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        st.error(f"OCR error: {e}")
        return ""

# ----------------------------
# Groq call helper
# ----------------------------
def call_groq(model: str, messages: List[dict], temperature: float = 0.2, max_tokens: int = 800, api_key: str = ""):
    key = api_key or GROQ_API_KEY
    if not key:
        return {"error": "No Groq API key provided. Set GROQ_API_KEY in secrets or env, or paste it above."}
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

# ----------------------------
# PDF report generation
# ----------------------------
def generate_pdf_report(question, student_answer, grading_json) -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    margin = 40
    y = height - margin

    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, y, "Board-style Grading Report")
    y -= 30

    c.setFont("Helvetica", 11)
    c.drawString(margin, y, f"Question:")
    y -= 18
    for line in question.splitlines():
        c.drawString(margin + 10, y, line[:100])
        y -= 14
        if y < 100:
            c.showPage(); y = height - margin
    y -= 6

    c.drawString(margin, y, "Student Answer:")
    y -= 18
    for line in student_answer.splitlines():
        c.drawString(margin + 10, y, line[:100])
        y -= 14
        if y < 100:
            c.showPage(); y = height - margin

    y -= 6
    c.drawString(margin, y, "Grading Result:")
    y -= 18

    # pretty-print grading JSON
    try:
        scores = grading_json.get("scores", {})
        total = grading_json.get("total_score", "")
        c.drawString(margin + 10, y, f"Total Score: {total}")
        y -= 18
        c.drawString(margin + 10, y, "Breakdown:")
        y -= 16
        for k, v in scores.items():
            c.drawString(margin + 20, y, f"{k}: {v}")
            y -= 14
            if y < 100:
                c.showPage(); y = height - margin
        y -= 8
        c.drawString(margin + 10, y, "Missing Points:")
        y -= 14
        for item in grading_json.get("missing_points", [])[:50]:
            c.drawString(margin + 20, y, f"- {item}")
            y -= 12
            if y < 100:
                c.showPage(); y = height - margin
        y -= 8
        c.drawString(margin + 10, y, "Mistakes:")
        y -= 14
        for item in grading_json.get("mistakes", [])[:50]:
            c.drawString(margin + 20, y, f"- {item}")
            y -= 12
            if y < 100:
                c.showPage(); y = height - margin
        y -= 8
        c.drawString(margin + 10, y, "Improvement:")
        y -= 14
        for line in str(grading_json.get("improvement", "")).splitlines():
            c.drawString(margin + 10, y, line[:100])
            y -= 12
            if y < 100:
                c.showPage(); y = height - margin
    except Exception as e:
        c.drawString(margin + 10, y, f"Error creating report content: {e}")

    c.showPage()
    c.save()
    buf.seek(0)
    return buf.read()

# ----------------------------
# UI: Upload or type questions
# ----------------------------
st.header("1. Upload or Type Questions")
uploaded_q_files = st.file_uploader("Upload question files (PDF or TXT). You can upload multiple.", accept_multiple_files=True, type=["pdf", "txt"])
typed_q = st.text_area("OR paste / type questions here (separate multiple questions with a blank line):", height=120)

questions_list = []
if uploaded_q_files:
    questions_from_files = load_questions_from_txt_or_pdf(uploaded_q_files)
    questions_list.extend(questions_from_files)
if typed_q and typed_q.strip():
    # split by blank lines
    typed_blocks = [b.strip() for b in typed_q.split("\n\n") if b.strip()]
    questions_list.extend(typed_blocks)

# remove empties and trim
questions_list = [q.strip() for q in questions_list if q.strip()]

if not questions_list:
    st.info("No questions loaded yet. Upload files or type questions above.")
else:
    st.success(f"Loaded {len(questions_list)} question(s).")

# Show questions and let user select one
if questions_list:
    st.header("2. Select a Question to Grade")
    selected_index = st.selectbox("Choose question", list(range(len(questions_list))), format_func=lambda i: questions_list[i][:120] + ("..." if len(questions_list[i])>120 else ""))
    selected_question = questions_list[selected_index]
    st.markdown("**Selected question:**")
    st.write(selected_question)

    # Question settings
    q_type = st.selectbox("Question type", ["subjective", "mcq"], index=0)
    if q_type == "mcq":
        st.write("MCQ: enter options and correct option")
        opts_raw = st.text_area("Enter options (one per line)", value="Option A\nOption B\nOption C\nOption D", height=100)
        options = [o.strip() for o in opts_raw.splitlines() if o.strip()]
        correct_option = st.selectbox("Correct option (teacher reference)", options)
        max_marks = st.number_input("Max marks for MCQ", min_value=0.0, value=1.0)
        negative_mark = st.number_input("Negative marking per wrong (>=0)", min_value=0.0, value=0.0)
    else:
        max_marks = st.number_input("Max marks for subjective question", min_value=1.0, value=5.0)
        model_answer = st.text_area("Model answer / key points (for rubric):", height=150)

    # Student answer input
    st.header("3. Student's Answer")
    input_mode = st.radio("Answer input mode", ["Type answer", "Upload image (photo/handwritten)"])
    student_answer = ""
    if input_mode == "Type answer":
        student_answer = st.text_area("Student answer", height=250)
    else:
        uploaded_img = st.file_uploader("Upload student's answer image (jpg/png):", type=["jpg","jpeg","png"], key="answer_img")
        if uploaded_img:
            st.image(uploaded_img, caption="Uploaded student's answer")
            with st.spinner("Running OCR..."):
                student_answer = ocr_image_to_text(uploaded_img)
            st.text_area("OCR result (editable)", value=student_answer, height=250)

    # grading controls
    st.header("4. Grade")
    model_input = st.selectbox("Choose model", [DEFAULT_MODEL], index=0)
    temp = st.slider("Temperature (LLM creativity)", 0.0, 1.0, 0.2)
    max_tok = st.number_input("Max tokens for LLM response", min_value=200, max_value=4000, value=800, step=100)

    if st.button("Grade this answer"):
        if not GROQ_API_KEY:
            st.error("Groq API key not found. Set it in Streamlit secrets or environment, or paste above.")
        elif not selected_question.strip():
            st.warning("No question selected.")
        elif not student_answer or not student_answer.strip():
            st.warning("Please provide student's answer (type or upload image).")
        else:
            if q_type == "mcq":
                # Ask user what student selected
                chosen = st.selectbox("Assume student selected:", options)
                raw_score = float(max_marks) if chosen == correct_option else -float(negative_mark)
                score = max(0.0, raw_score)
                st.success(f"MCQ Score: {score} / {max_marks}")
                st.write("Correct option:", correct_option)
            else:
                # Build rubric weights automatically (customizable)
                rubric = {
                    "max_marks": float(max_marks),
                    "criteria": {
                        "content_correctness": round(0.5 * float(max_marks), 2),
                        "method_steps": round(0.3 * float(max_marks), 2),
                        "presentation": round(0.1 * float(max_marks), 2),
                        "language_keywords": round(0.1 * float(max_marks), 2)
                    }
                }
                # normalize
                s = sum(rubric["criteria"].values())
                if s != rubric["max_marks"]:
                    factor = rubric["max_marks"] / s
                    for k in rubric["criteria"]:
                        rubric["criteria"][k] = round(rubric["criteria"][k] * factor, 2)

                st.write("Using rubric:", rubric)

                # compose prompt asking for JSON only
                system = "You are a strict board-style examiner. Grade according to rubric and model answer. Return ONLY a JSON with keys: scores (dict of criteria), total_score (float), missing_points (list), mistakes (list), improvement (string). Numeric scores should sum to max_marks. Do not include any extra text."
                user_prompt = f"""Question: {selected_question}

Model answer / key points: {model_answer}

Rubric (max marks = {rubric['max_marks']}): {json.dumps(rubric['criteria'])}

Student answer: {student_answer}

Return the JSON as described."""
                messages = [{"role": "system", "content": system}, {"role": "user", "content": user_prompt}]
                with st.spinner("Calling Groq for grading..."):
                    resp = call_groq(model=model_input, messages=messages, temperature=temp, max_tokens=int(max_tok), api_key=GROQ_API_KEY)

                if isinstance(resp, dict) and "error" in resp:
                    st.error("Groq error: " + resp["error"])
                else:
                    # parse
                    try:
                        content = resp["choices"][0]["message"]["content"]
                    except Exception:
                        st.error("Unexpected Groq response format.")
                        st.write(resp)
                        content = None

                    parsed = None
                    if content:
                        try:
                            parsed = json.loads(content.strip())
                        except Exception:
                            try:
                                # extract first {...}
                                start = content.index("{")
                                end = content.rindex("}") + 1
                                parsed = json.loads(content[start:end])
                            except Exception as e:
                                st.warning("Could not parse JSON from LLM. Showing raw output:")
                                st.code(content)
                                parsed = None

                    if parsed:
                        total = float(parsed.get("total_score", 0.0))
                        total = max(0.0, min(total, rubric["max_marks"]))
                        parsed["total_score"] = round(total, 2)
                        st.subheader("Result")
                        st.success(f"Total: {parsed['total_score']} / {rubric['max_marks']}")
                        st.markdown("**Breakdown**")
                        st.json(parsed.get("scores", {}))
                        st.markdown("**Missing Points**")
                        st.write(parsed.get("missing_points", []))
                        st.markdown("**Mistakes**")
                        st.write(parsed.get("mistakes", []))
                        st.markdown("**Improvement Tip**")
                        st.write(parsed.get("improvement", ""))

                        # PDF report
                        if st.button("Download PDF Report"):
                            pdf_bytes = generate_pdf_report(selected_question, student_answer, parsed)
                            st.download_button("⬇️ Download Report (PDF)", data=pdf_bytes, file_name="grading_report.pdf", mime="application/pdf")
                    else:
                        st.error("Failed to parse LLM output. See raw output above for debugging.")
