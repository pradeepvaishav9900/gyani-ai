import streamlit as st
import json, os, uuid, datetime
from PIL import Image
import requests

# -----------------------------
# App Name & Branding: MASTER
# Student-only app with built-in question bank & Groq evaluation (optional)
# -----------------------------
APP_NAME = "MASTER"
APP_TAGLINE = "Board Exam Evaluator — Student Edition"
LOGO_EMOJI = "📘"

DATA_DIR = "data"
USERS_FP = os.path.join(DATA_DIR, "users.json")
QUESTIONS_FP = os.path.join(DATA_DIR, "questions.json")
SUBMISSIONS_FP = os.path.join(DATA_DIR, "submissions.json")
UPLOADS_DIR = os.path.join(DATA_DIR, "uploads")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)

# -----------------------------
# Sample question bank (minimal examples)
# Replace /data/questions.json with full 10th/12th papers (previous 5-6 years) in same format.
# -----------------------------
SAMPLE_QUESTIONS = {
    "q_10_phy_kin_001": {
        "id": "q_10_phy_kin_001",
        "class": "10",
        "subject": "Physics",
        "chapter": "Kinematics",
        "question_text": "State and explain the equations of motion for uniformly accelerated motion.",
        "total_marks": 5,
        "model_answer": "s = ut + 1/2 at^2; v = u + at; v^2 = u^2 + 2as. Explain each variable and give small example.",
        "rubric": [
            {"keyword": "s = ut +", "weight": 2, "hint": "include term with 1/2 at^2"},
            {"keyword": "v = u + at", "weight": 1, "hint": "write velocity equation"},
            {"keyword": "v^2 = u^2 + 2as", "weight": 2, "hint": "energy-like relation"}
        ],
        "source": "sample"
    }
}

# Ensure questions file exists (preload sample if empty)
if not os.path.exists(QUESTIONS_FP):
    with open(QUESTIONS_FP, "w", encoding="utf-8") as f:
        json.dump(SAMPLE_QUESTIONS, f, ensure_ascii=False, indent=2)

# Default users: demo student (student-only app)
DEFAULT_USERS = {"student_demo": {"password": "student123", "role": "student", "full_name": "Demo Student"}}
for fp, default in [
    (USERS_FP, DEFAULT_USERS),
    (SUBMISSIONS_FP, {}),
]:
    if not os.path.exists(fp):
        with open(fp, "w", encoding="utf-8") as f:
            json.dump(default, f, ensure_ascii=False, indent=2)

# -----------------------------
# Utility functions
# -----------------------------
def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def new_id(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

# -----------------------------
# Auth (student-only)
# -----------------------------
def register_user(username, password, full_name):
    users = load_json(USERS_FP)
    if username in users:
        return False, "Username already exists"
    users[username] = {"password": password, "role": "student", "full_name": full_name}
    save_json(USERS_FP, users)
    return True, "Registered successfully"

def authenticate(username, password):
    users = load_json(USERS_FP)
    if username in users and users[username]["password"] == password:
        return True, users[username]
    return False, None

# -----------------------------
# Keyword-based auto-grader (fallback)
# -----------------------------
def keyword_grade(answer_text, rubric, total_marks):
    if not answer_text or not rubric:
        return None, "No auto grading available"
    text = answer_text.lower()
    score = 0.0
    feedback_lines = []
    weight_sum = sum(item.get("weight", 1.0) for item in rubric) or 1.0
    for item in rubric:
        kw = item.get("keyword", "").lower()
        w = float(item.get("weight", 1.0))
        part_marks = (w / weight_sum) * float(total_marks)
        if kw and kw in text:
            score += part_marks
            feedback_lines.append(f"✔ Covered: '{kw}' (+{part_marks:.1f})")
        else:
            hint = item.get("hint", "")
            msg = f"✘ Missing: '{kw}'"
            if hint:
                msg += f" → Hint: {hint}"
            feedback_lines.append(msg)
    return round(score, 1), "\n".join(feedback_lines)

# -----------------------------
# Groq-based evaluation (optional)
# Requires: set GROQ_API_KEY and GROQ_MODEL in Streamlit secrets or env vars
# Guidance: On Streamlit Cloud set secrets: GROQ_API_KEY and GROQ_MODEL (e.g. 'groq-alpha' or model name)
# Endpoint format used here is a common REST form; if Groq uses a different endpoint update the URL below.
# -----------------------------
def evaluate_with_groq(answer_text, question_text, model_answer, total_marks):
    api_key = os.getenv("GROQ_API_KEY") or (st.secrets.get("GROQ_API_KEY") if "GROQ_API_KEY" in st.secrets else None)
    model = os.getenv("GROQ_MODEL") or (st.secrets.get("GROQ_MODEL") if "GROQ_MODEL" in st.secrets else "groq-alpha")
    if not api_key:
        # No Groq configured — fallback
        if model_answer and model_answer.strip():
            return None, "Groq not configured — model answer available for reference"
        return keyword_grade(answer_text, [], total_marks)

    # Build a prompt for board-style grading
    prompt = (
        f"You are a CBSE board examiner. Question:\n{question_text}\n\nModel answer:\n{model_answer or 'N/A'}\n\n"
        f"Student answer:\n{answer_text}\n\nRespond with a JSON object like: {{\"score\": number, \"feedback\": string}} where score is out of {total_marks}."
    )

    # Example endpoint — update if your Groq account uses another one
    url = f"https://api.groq.com/v1/models/{model}/generate"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    body = {"prompt": prompt, "max_tokens": 400, "temperature": 0.2}
    try:
        resp = requests.post(url, headers=headers, json=body, timeout=20)
        if resp.status_code != 200:
            return None, f"Groq API error: {resp.status_code} — {resp.text}"
        text = resp.json().get("text") or resp.text
        # Try to extract JSON object from response
        import re
        m = re.search(r"\{[\s\S]*\}", text)
        if m:
            j = json.loads(m.group(0))
            return float(j.get("score")), j.get("feedback")
        return None, text
    except Exception as e:
        return None, f"Groq evaluation failed: {e}"

# -----------------------------
# UI Components (student-only flow)
# -----------------------------
def navbar():
    st.markdown(f"<h1>{LOGO_EMOJI} {APP_NAME}</h1><p style='font-size:16px;color:#4a4a4a;margin-top:-10px'>{APP_TAGLINE}</p>", unsafe_allow_html=True)
    if st.session_state.get("auth"):
        user = st.session_state["auth"]
        st.markdown(f"**Signed in:** {user['full_name']}")
        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()

def sidebar_auth():
    st.sidebar.header("Account (Student only)")
    tab = st.sidebar.tabs(["Login","Register"])
    with tab[0]:
        u = st.text_input("Username", key="login_u")
        p = st.text_input("Password", type="password", key="login_p")
        if st.button("Login", key="login_btn"):
            ok, user = authenticate(u, p)
            if ok:
                user["username"] = u
                st.session_state["auth"] = user
                st.success("Logged in")
                st.rerun()
            else:
                st.error("Invalid credentials")
    with tab[1]:
        name = st.text_input("Full name", key="reg_name")
        nu = st.text_input("Choose username", key="reg_u")
        np = st.text_input("Choose password", type="password", key="reg_p")
        if st.button("Register", key="reg_btn"):
            if not (name and nu and np):
                st.warning("Please fill all fields")
            else:
                ok,msg = register_user(nu,np,name)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)

def load_questions():
    qs = load_json(QUESTIONS_FP)
    merged = {**SAMPLE_QUESTIONS, **qs}
    return merged

def student_panel():
    st.subheader("Practice — Choose question or upload your own")
    qs = load_questions()
    classes = sorted({q.get('class') for q in qs.values()})
    clazz = st.selectbox("Class", classes)
    subjects = sorted({q.get('subject') for q in qs.values() if q.get('class')==clazz})
    subject = st.selectbox("Subject", subjects)
    chapters = sorted({q.get('chapter') for q in qs.values() if q.get('class')==clazz and q.get('subject')==subject})
    chapter = st.selectbox("Chapter", chapters)
    q_list = [q for q in qs.values() if q.get('class')==clazz and q.get('subject')==subject and q.get('chapter')==chapter]
    if not q_list:
        st.warning("No questions found for this filter")
        return
    q_sel = st.selectbox("Select question", q_list, format_func=lambda x: x['question_text'][:100])

    st.markdown("---")
    st.markdown("### Option A — Answer this built-in question")
    with st.form("answer_form"):
        ans_text = st.text_area("Write your answer (typed)")
        img = st.file_uploader("OR upload answer image (photo/scan)", type=["jpg","jpeg","png"])
        submit = st.form_submit_button("Submit Answer")
    if submit:
        img_path = None
        if img:
            ext = os.path.splitext(img.name)[1]
            img_name = new_id("img") + ext
            img_path = os.path.join(UPLOADS_DIR, img_name)
            try:
                Image.open(img).save(img_path)
            except Exception:
                with open(img_path, "wb") as f:
                    f.write(img.getbuffer())
        score = None
        fb = None
        if ans_text.strip():
            gscore, gfb = evaluate_with_groq(ans_text, q_sel.get('question_text',''), q_sel.get('model_answer',''), q_sel.get('total_marks',0))
            if gscore is not None:
                score, fb = gscore, gfb
            else:
                kscore, kfb = keyword_grade(ans_text, q_sel.get('rubric',[]), q_sel.get('total_marks',0))
                score, fb = kscore, kfb
        sid = new_id('sub')
        subs = load_json(SUBMISSIONS_FP)
        subs[sid] = {
            'id': sid,
            'question_id': q_sel['id'],
            'student_username': st.session_state['auth']['username'],
            'answer_text': ans_text.strip() or None,
            'answer_image_path': img_path,
            'auto_score': score,
            'auto_feedback': fb,
            'teacher_score': None,
            'teacher_feedback': None,
            'status': 'graded' if score is not None else 'pending',
            'created_at': datetime.datetime.utcnow().isoformat(),
            'updated_at': datetime.datetime.utcnow().isoformat()
        }
        save_json(SUBMISSIONS_FP, subs)
        st.success(f"Submitted — ID: {sid}")
        if score is not None:
            st.info(f"Score: {score} / {q_sel.get('total_marks')}")
            if fb:
                st.markdown(f"**Feedback:**\n{fb}")

    st.markdown("---")
    st.markdown("### Option B — Upload your own question + answer (for custom evaluation)")
    with st.form("custom_q_form"):
        qtxt = st.text_area("Your Question text")
        ans_text2 = st.text_area("Your Answer text (or leave blank if uploading image)")
        ans_img2 = st.file_uploader("Upload answer image (optional)", type=["jpg","jpeg","png"], key="custom_img")
        total_marks2 = st.number_input("Total marks (for evaluation)", 1, 100, 5)
        submit2 = st.form_submit_button("Submit custom Q & Answer")
    if submit2:
        img_path2 = None
        if ans_img2:
            ext = os.path.splitext(ans_img2.name)[1]
            img_name = new_id("img") + ext
            img_path2 = os.path.join(UPLOADS_DIR, img_name)
            try:
                Image.open(ans_img2).save(img_path2)
            except Exception:
                with open(img_path2, "wb") as f:
                    f.write(ans_img2.getbuffer())
        score2 = None; fb2 = None
        if ans_text2.strip():
            gscore2, gfb2 = evaluate_with_groq(ans_text2, qtxt, None, total_marks2)
            if gscore2 is not None:
                score2, fb2 = gscore2, gfb2
            else:
                kscore2, kfb2 = keyword_grade(ans_text2, [], total_marks2)
                score2, fb2 = kscore2, kfb2
        sid2 = new_id('sub')
        subs = load_json(SUBMISSIONS_FP)
        subs[sid2] = {'id':sid2,'question_id':None,'question_text':qtxt,'student_username':st.session_state['auth']['username'],'answer_text':ans_text2.strip() or None,'answer_image_path':img_path2,'auto_score':score2,'auto_feedback':fb2,'status': 'graded' if score2 is not None else 'pending','created_at':datetime.datetime.utcnow().isoformat(),'updated_at':datetime.datetime.utcnow().isoformat()}
        save_json(SUBMISSIONS_FP, subs)
        st.success(f"Custom Q submitted — ID: {sid2}")
        if score2 is not None:
            st.info(f"Score: {score2} / {total_marks2}")
            if fb2:
                st.markdown(f"**Feedback:**\n{fb2}")

# -----------------------------
# Results & Leaderboard
# -----------------------------
def my_results():
    st.subheader("My Submissions & Results")
    subs = load_json(SUBMISSIONS_FP)
    qs = load_questions()
    me = st.session_state['auth']['username']
    mine = [s for s in subs.values() if s.get('student_username')==me]
    if not mine:
        st.info("No submissions yet")
        return
    for s in sorted(mine, key=lambda x: x.get('created_at','')):
        qtxt = qs.get(s.get('question_id'),{}).get('question_text') if s.get('question_id') else s.get('question_text')
        st.markdown(f"**Submission {s['id']}** — Question: {qtxt}")
        if s.get('answer_text'):
            st.write(s.get('answer_text'))
        if s.get('answer_image_path') and os.path.exists(s.get('answer_image_path')):
            st.image(s.get('answer_image_path'), use_column_width=True)
        st.write(f"Auto score: {s.get('auto_score')}\nStatus: {s.get('status')}")
        if s.get('auto_feedback'):
            st.markdown(f"**Feedback:**\n{s.get('auto_feedback')}")
        st.markdown('---')

def leaderboard():
    st.subheader('Leaderboard (based on auto/teacher scores)')
    subs = load_json(SUBMISSIONS_FP)
    qs = load_questions()
    totals = {}
    max_totals = {}
    for s in subs.values():
        user = s.get('student_username')
        score = s.get('teacher_score') if s.get('teacher_score') is not None else (s.get('auto_score') or 0)
        totals[user] = totals.get(user, 0) + float(score or 0)
        # approximate max: if linked to a question take its marks else use submitted total (not stored here)
        if s.get('question_id'):
            mq = qs.get(s.get('question_id'),{})
            max_totals[user] = max_totals.get(user,0) + float(mq.get('total_marks',0))
        else:
            max_totals[user] = max_totals.get(user,0) + 0
    board = sorted([(u, totals[u], max_totals.get(u,0)) for u in totals.keys()], key=lambda x: x[1], reverse=True)
    if not board:
        st.info('No scores yet')
        return
    st.table([{ 'Rank': i+1, 'Student': b[0], 'Marks': f"{b[1]:.1f} / {b[2]:.1f}" } for i,b in enumerate(board)])

# -----------------------------
# Main
# -----------------------------
def main():
    st.set_page_config(page_title=f"{APP_NAME}", page_icon="📘", layout='wide')
    navbar()
    sidebar_auth()
    if not st.session_state.get('auth'):
        st.info('Login or register to continue')
        return
    st.sidebar.markdown('---')
    st.sidebar.button('My Submissions', on_click=lambda: st.session_state.update({'view':'results'}))
    st.sidebar.button('Leaderboard', on_click=lambda: st.session_state.update({'view':'board'}))
    view = st.session_state.get('view','practice')
    if view=='results':
        my_results()
    elif view=='board':
        leaderboard()
    else:
        student_panel()

if __name__=="__main__":
    main()
