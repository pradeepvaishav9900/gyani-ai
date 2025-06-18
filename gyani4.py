import streamlit as st
import requests
import datetime

st.set_page_config(page_title="Gyani - Local AI Chatbot", page_icon="🧠")

st.markdown("""
    <div style='text-align: center;'>
        <h1>🧠 Gyani</h1>
        <h4 style='color: gray;'>Developed by Pradeep Vaishnav</h4>
        <p style='font-size: 14px; color: #555;'>Gyani ek AI chatbot hai jo ab bina OpenAI key ke bhi chal sakta hai – local AI model se!</p>
    </div>
    <hr>
""", unsafe_allow_html=True)

# Chat history
if "history" not in st.session_state:
    st.session_state.history = []

# 💬 Function to talk to Local AI via Ollama
def local_chat(prompt):
    try:
        res = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "mistral", "prompt": prompt, "stream": False}
        )
        if res.status_code == 200:
            return res.json()["response"]
        else:
            return "⚠️ Gyani: Local model se jawaab nahi mila."
    except Exception as e:
        return f"⚠️ Gyani Error: {str(e)}"

# Chat Input
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_area("👤 Aapka Prashn:", placeholder="Gyani se kuch bhi poochho...", key="input")
    submitted = st.form_submit_button("📨 Bhej do")

if submitted and user_input.strip() != "":
    st.session_state.history.append(("user", user_input.strip()))
    with st.spinner("🧠 Gyani soch raha hai..."):
        answer = local_chat(user_input.strip())
    st.session_state.history.append(("gyani", answer))

# Show full conversation
st.markdown("<hr><h4>📜 Purani Baatein:</h4>", unsafe_allow_html=True)
for speaker, msg in st.session_state.history:
    if speaker == "user":
        st.markdown(f"👤 **User**: {msg}")
    else:
        st.markdown(f"🧠 **Gyani**: {msg}")

st.markdown(f"<p style='text-align: right; font-size: small; color: gray;'>🕒 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>", unsafe_allow_html=True)
