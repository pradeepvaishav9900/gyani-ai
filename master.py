import streamlit as st
import requests
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# Groq API Key (Replace with your actual key or use st.secrets)
GROQ_API_KEY = "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"

st.set_page_config(page_title="AI Exam Checker", page_icon="📝", layout="centered")

st.title("📝 AI-Based Question Checking App")
st.write("Upload questions, write answers, and get marks like a board examiner.")

# Step 1: Upload Questions
uploaded_file = st.file_uploader("Upload a text file containing questions", type=["txt"])

questions = []
if uploaded_file:
    questions = uploaded_file.read().decode("utf-8").strip().split("\n")
    st.success(f"{len(questions)} questions loaded successfully!")

# Step 2: Display Questions and Take Answers
if questions:
    st.subheader("Write Your Answers")
    answers = []
    for i, q in enumerate(questions):
        ans = st.text_area(f"Q{i+1}: {q}", height=100)
        answers.append(ans)

    # Step 3: Evaluate Answers with Groq API
    if st.button("✅ Submit for Checking"):
        with st.spinner("Checking your answers..."):
            total_marks = 0
            max_marks = len(questions) * 5  # 5 marks per question
            results = []

            for i, (q, a) in enumerate(zip(questions, answers)):
                if a.strip() == "":
                    marks = 0
                    feedback = "No answer provided."
                else:
                    prompt = f"""
                    You are a strict board examiner. Question: {q}
                    Student Answer: {a}
                    Give marks out of 5 and provide feedback in 2 lines.
                    Format: Marks: X/5 | Feedback: <your feedback>
                    """
                    response = requests.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {GROQ_API_KEY}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "llama-3.1-8b-instant",
                            "messages": [{"role": "user", "content": prompt}]
                        }
                    )

                    if response.status_code == 200:
                        ai_text = response.json()['choices'][0]['message']['content']
                        try:
                            parts = ai_text.split("|")
                            marks_text = parts[0].strip().replace("Marks:", "").strip()
                            marks = int(marks_text.split("/")[0])
                            feedback = parts[1].replace("Feedback:", "").strip()
                        except:
                            marks = 0
                            feedback = "Could not parse feedback."
                    else:
                        marks = 0
                        feedback = "API Error."

                total_marks += marks
                results.append((q, a, marks, feedback))

            percentage = (total_marks / max_marks) * 100
            st.success(f"Total Marks: {total_marks}/{max_marks} ({percentage:.2f}%)")

            # Show detailed result
            for i, (q, a, marks, feedback) in enumerate(results):
                st.markdown(f"**Q{i+1}: {q}**")
                st.markdown(f"Your Answer: {a}")
                st.markdown(f"**Marks: {marks}/5**")
                st.markdown(f"Feedback: {feedback}")
                st.write("---")

            # Step 4: Download PDF
            def generate_pdf():
                buffer = BytesIO()
                p = canvas.Canvas(buffer, pagesize=A4)
                width, height = A4
                p.setFont("Helvetica", 14)
                p.drawString(100, height - 50, "AI Exam Report")
                y = height - 100
                for i, (q, a, marks, feedback) in enumerate(results):
                    text = f"Q{i+1}: {q}\nMarks: {marks}/5\nFeedback: {feedback}\n"
                    for line in text.split("\n"):
                        p.drawString(50, y, line)
                        y -= 20
                        if y < 100:
                            p.showPage()
                            y = height - 50
                p.drawString(50, y - 30, f"Total Marks: {total_marks}/{max_marks}")
                p.save()
                buffer.seek(0)
                return buffer

            pdf_buffer = generate_pdf()
            st.download_button("📥 Download Result as PDF", pdf_buffer, "exam_report.pdf", "application/pdf")

else:
    st.info("Please upload a question file to start.")
