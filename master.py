import streamlit as st
import json, os, uuid, datetime
from PIL import Image

# -----------------------------
# App Name & Branding: MASTER
# -----------------------------
APP_NAME = "MASTER"
APP_TAGLINE = "Board Exam Evaluator"
LOGO_EMOJI = "📘"

DATA_DIR = "data"
USERS_FP = os.path.join(DATA_DIR, "users.json")
QUESTIONS_FP = os.path.join(DATA_DIR, "questions.json")
SUBMISSIONS_FP = os.path.join(DATA_DIR, "submissions.json")
UPLOADS_DIR = os.path.join(DATA_DIR, "uploads")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)

# Default teacher account
DEFAULT_USERS = {
    "teacher": {"password": "teacher123", "role": "teacher", "full_name": "Demo Teacher"}
}

for fp, default in [
    (USERS_FP, DEFAULT_USERS),
    (QUESTIONS_FP, {}),
    (SUBMISSIONS_FP, {}),
]:
    if not os.path.exists(fp):
        with open(fp, "w", encoding="utf-8") as f:
            json.dump(default, f, ensure_ascii=False, indent=2)

# -----------------------------
# Utility Functions
# -----------------------------

def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def new_id(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

# -----------------------------
# Auth Functions
# -----------------------------

def register_user(username, password, full_name, role):
    users = load_json(USERS_FP)
    if username in users:
        return False, "Username already exists"
    users[username] = {"password": password, "role": role, "full_name": full_name}
    save_json(USERS_FP, users)
    return True, "Registered successfully"

def authenticate(username, password):
    users = load_json(USERS_FP)
    if username in users and users[username]["password"] == password:
        return True, users[username]
    return False, None

# -----------------------------
# Auto Grading (Keyword-based)
# -----------------------------

def auto_grade(answer_text, rubric, total_marks):
    if not answer_text or not rubric:
        return None, "No auto grading available"
    text = answer_text.lower()
    score = 0.0
    feedback = []
    weight_sum = sum(r.get("weight", 1) for r in rubric)
    for r in rubric:
        kw = r.get("keyword", "").lower()
        weight = r.get("weight", 1)
        hint = r.get("hint", "")
        part = (weight / weight_sum) * total_marks
        if kw in text:
            score += part
            feedback.append(f"✔ '{kw}' covered (+{round(part,1)})")
        else:
            miss = f"✘ Missing '{kw}'"
            if hint:
                miss += f" → Hint: {hint}"
            feedback.append(miss)
    return round(score, 1), "\n".join(feedback)

# -----------------------------
# UI Components
# -----------------------------

def navbar():
    st.markdown(f"<h1>{LOGO_EMOJI} {APP_NAME}</h1><p style='font-size:18px;color:#4a4a4a'>{APP_TAGLINE}</p>", unsafe_allow_html=True)
    if st.session_state.get("auth"):
        user = st.session_state["auth"]
        st.markdown(f"**Signed in:** {user['full_name']} ({user['role']})")
        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()

def sidebar_auth():
    st.sidebar.header("Account")
    tab = st.sidebar.tabs(["Login", "Register"])
    with tab[0]:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            ok, user = authenticate(u, p)
            if ok:
                user["username"] = u
                st.session_state["auth"] = user
                st.rerun()
            else:
                st.error("Invalid credentials")
    with tab[1]:
        name = st.text_input("Full name")
        nu = st.text_input("New username")
        np = st.text_input("New password", type="password")
        role = st.selectbox("Role", ["student", "teacher"])
        if st.button("Register"):
            if not (name and nu and np):
                st.warning("Fill all fields")
            else:
                ok, msg = register_user(nu, np, name, role)
                st.success(msg) if ok else st.error(msg)

# -----------------------------
# Teacher Panel
# -----------------------------

def teacher_panel():
    st.subheader("Create Question")
    with st.form("qform"):
        clazz = st.selectbox("Class", ["10","12"])
        subj = st.text_input("Subject")
        chap = st.text_input("Chapter")
        qtext = st.text_area("Question")
        marks = st.number_input("Total Marks", 1, 100, 5)
        model = st.text_area("Model Answer")
        rows = st.number_input("Rubric rows", 0, 10, 3)
        rubric = []
        for i in range(rows):
            c1,c2,c3 = st.columns([2,1,2])
            kw = c1.text_input(f"Keyword {i+1}")
            wt = c2.number_input(f"Weight {i+1}",0.0,10.0,1.0)
            hint = c3.text_input(f"Hint {i+1}")
            if kw:
                rubric.append({"keyword":kw,"weight":wt,"hint":hint})
        if st.form_submit_button("Save Question"):
            qid = new_id("q")
            questions = load_json(QUESTIONS_FP)
            auth = st.session_state["auth"]
            questions[qid] = {"id":qid,"created_by":auth["username"],"class":clazz,"subject":subj,"chapter":chap,"question_text":qtext,"total_marks":marks,"model_answer":model,"rubric":rubric,"created_at":datetime.datetime.utcnow().isoformat()}
            save_json(QUESTIONS_FP, questions)
            st.success(f"Question saved (ID: {qid})")

    st.subheader("Review Submissions")
    subs = load_json(SUBMISSIONS_FP)
    qs = load_json(QUESTIONS_FP)
    if not subs:
        st.info("No submissions yet")
        return
    for sid, s in subs.items():
        q = qs.get(s["question_id"],{})
        with st.expander(f"Submission {sid} by {s['student_username']}"):
            st.write("Question:", q.get("question_text"))
            st.write("Answer:", s.get("answer_text"))
            if s.get("answer_image_path") and os.path.exists(s.get("answer_image_path")):
                st.image(s.get("answer_image_path"))
            score = st.number_input(f"Score for {sid}",0.0,float(q.get("total_marks",0)),s.get("teacher_score") or 0.0)
            fb = st.text_area(f"Feedback for {sid}", s.get("teacher_feedback") or "")
            if st.button(f"Save {sid}"):
                s["teacher_score"] = score
                s["teacher_feedback"] = fb
                s["status"] = "graded"
                s["updated_at"] = datetime.datetime.utcnow().isoformat()
                subs[sid] = s
                save_json(SUBMISSIONS_FP, subs)
                st.success("Saved")

# -----------------------------
# Student Panel
# -----------------------------

def student_panel():
    st.subheader("Practice & Submit")
    qs = load_json(QUESTIONS_FP)
    if not qs:
        st.info("No questions available")
        return
    clazz = st.selectbox("Class",sorted({q['class'] for q in qs.values()}))
    subj = st.selectbox("Subject",sorted({q['subject'] for q in qs.values()}))
    chap = st.selectbox("Chapter",sorted({q['chapter'] for q in qs.values()}))
    q_list=[q for q in qs.values() if q['class']==clazz and q['subject']==subj and q['chapter']==chap]
    if not q_list:
        st.warning("No matching questions")
        return
    q_sel = st.selectbox("Select Question",q_list,format_func=lambda x:x['question_text'][:50])
    with st.form("ansform"):
        ans_text = st.text_area("Answer text")
        img = st.file_uploader("Upload image")
        if st.form_submit_button("Submit"):
            img_path=None
            if img:
                fname=new_id("img")+os.path.splitext(img.name)[1]
                img_path=os.path.join(UPLOADS_DIR,fname)
                Image.open(img).save(img_path)
            auto_score=None; auto_fb=None; status="pending"
            if ans_text.strip():
                auto_score,auto_fb=auto_grade(ans_text,q_sel.get("rubric",[]),q_sel.get("total_marks",0))
                if auto_score is not None:
                    status="auto-graded"
            sid=new_id("sub")
            subs=load_json(SUBMISSIONS_FP)
            subs[sid]={"id":sid,"question_id":q_sel['id'],"student_username":st.session_state['auth']['username'],"answer_text":ans_text.strip() or None,"answer_image_path":img_path,"auto_score":auto_score,"auto_feedback":auto_fb,"teacher_score":None,"teacher_feedback":None,"status":status,"created_at":datetime.datetime.utcnow().isoformat(),"updated_at":datetime.datetime.utcnow().isoformat()}
            save_json(SUBMISSIONS_FP,subs)
            st.success(f"Submitted! ID:{sid}")
            if auto_score is not None:
                st.info(f"Auto score: {auto_score}/{q_sel['total_marks']}")
                if auto_fb:
                    st.text(auto_fb)

# -----------------------------
# Main
# -----------------------------

def main():
    st.set_page_config(page_title=f"{APP_NAME} App", page_icon="📘", layout="wide")
    navbar()
    sidebar_auth()
    if not st.session_state.get("auth"):
        st.info("Login or register to continue")
        return
    if st.session_state['auth']['role']=="teacher":
        teacher_panel()
    else:
        student_panel()

if __name__=="__main__":
    main()
