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

# Smart Input Form
text_input_key = "input_box"
with st.form("ask_gyani"):
    user_input = st.text_input("💬 Gyani se poochho:", placeholder="Type your query...", key=text_input_key)
    submitted = st.form_submit_button("💬 Send")

if submitted and user_input:
    query = user_input.lower()
    st.session_state[text_input_key] = ""  # Safe input clear

    try:
        # Auto-detect modes
        if query.startswith("/help") or query.startswith("/about"):
            st.info("🧠 Gyani v2 - Smart Assistant. Features: Chat, Wiki, PDF Reader, Math.")

        elif any(word in query for word in ["who is", "history", "कौन", "था"]):
            lang = detect(user_input)
            wikipedia.set_lang(lang if lang in ["en", "hi"] else "en")
            result = wikipedia.summary(user_input, sentences=3)
            st.success(f"🌐 Wikipedia Result:
{result}")

        elif any(sym in query for sym in ["+", "-", "*", "/", "=", "solve"]):
            try:
                result = eval(query.split("=")[0])
                st.success(f"🧮 Result: {result}")
            except:
                st.error("❌ Unable to solve the expression.")

        elif "summarize" in query or (uploaded_file and "pdf" in query):
            if extracted_text:
                st.text_area("📄 Extracted Text:", value=extracted_text[:2000], height=300)
            else:
                st.warning("⚠️ No PDF uploaded to summarize.")

        else:
            # Default: Chat with Gyani
            st.session_state.history.append(("user", user_input))
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {groq_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama3-8b-8192",
                    "messages": [
                        {"role": "system", "content": "Tum ek helpful, simple Hindi aur English bolne wale assistant ho. Humesha simple, short aur clean reply do. Funny ya alag language mat use karo. Jab bhi koi puche ki tumhe kisne banaya, tum hamesha bataoge: 'Mujhe Pradeep Vaishnav ne banaya hai.'"},
                        {"role": "user", "content": user_input}
                    ]
                }
            )
            if response.status_code == 200:
                reply = response.json()["choices"][0]["message"]["content"]
                st.session_state.history.append(("gyani", reply))
                st.markdown(f"**🧠 Gyani:** {reply}")
            else:
                st.error("❌ Groq response error")

    except Exception as e:
        st.warning(f"⚠️ Error: {str(e)}")
