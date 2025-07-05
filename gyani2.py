import streamlit as st
import requests
import PyPDF2
import io
import wikipedia
from langdetect import detect

st.set_page_config(page_title="Gyani v2 - Smart AI Assistant", page_icon="🧠")
st.title("🧠 Gyani v2 - Smart + Auto-Detect Mode")
st.markdown("#### Developed by Pradeep Vaishnav")

# Load API Key
groq_api_key = "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"

# Initialize history
if "history" not in st.session_state:
    st.session_state.history = []

# File upload (optional for summarizer)
uploaded_file = st.file_uploader("📂 Upload a PDF (optional)", type=["pdf"])
extracted_text = ""
if uploaded_file:
    reader = PyPDF2.PdfReader(uploaded_file)
    extracted_text = "".join(page.extract_text() or "" for page in reader.pages)

# Smart Input (Enter-to-submit enabled and clear input)
input_key = "input_box"
user_input = st.text_input("💬 Gyani se poochho:", placeholder="Type your query...", key=input_key)

# Add a submit button
submit = st.button("💬 Send")

if submit and user_input:
    query = user_input.lower()
    st.session_state.history.append(("user", query))

    # Reset the input using workaround
    st.session_state[input_key] = st.session_state.get(input_key, "")

    # Full prompt with file context if available
    full_prompt = query + (f"\n\n📎 Attached content:\n{extracted_text}" if extracted_text else "")

    # Chat messages format
    messages = [
        {"role": "system", "content": "🧠 Tum Gyani ho — ek samajhdaar, Hindi mein baat karne wale teacher jaise AI assistant ho. Jab bhi koi puche ki tumhe kisne banaya, tum hamesha sach-sach bataoge ki 'Mujhe Pradeep Vaishnav ne banaya hai.'"}
    ]
    for speaker, msg in st.session_state.history[-5:]:
        role = "user" if speaker == "user" else "assistant"
        messages.append({"role": role, "content": msg})
    messages.append({"role": "user", "content": full_prompt})

    # Call Groq API
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-8b-8192",
        "messages": messages
    }

    with st.spinner("🧠 Gyani soch raha hai..."):
        response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        reply = response.json()["choices"][0]["message"]["content"]
        st.session_state.history.append(("gyani", reply))
        st.success(f"🧠 Gyani: {reply}")
    else:
        st.error("❌ Groq API Error: " + response.text)

# Show chat history
st.markdown("---")
for speaker, msg in st.session_state.history:
    role = "👤 User" if speaker == "user" else "🧠 Gyani"
    bubble_color = "#2a2a2a" if speaker == "user" else "#1f1f1f"
    st.markdown(f"<div style='padding: 12px; background-color: {bubble_color}; border-radius: 12px; margin: 8px auto; max-width: 720px;'><b>{role}:</b> {msg}</div>", unsafe_allow_html=True)

st.markdown("<hr><div style='text-align: center; color: gray;'>🤖 Gyani banaya gaya hai <b>Pradeep Vaishnav</b> dwara 🙏</div>", unsafe_allow_html=True)
