import streamlit as st
import requests
import PyPDF2
import io

st.set_page_config(page_title="Gyani v2 - Smart AI Assistant", page_icon="🧠")
st.title("🧠 Gyani v2 - Smart + Cloud Compatible")
st.markdown("#### Developed by Pradeep Vaishnav")

# Load API Key
groq_api_key = "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"

# Feature Toggles
menu = st.sidebar.selectbox("🗭 Choose Feature", [
    "💬 Chat with Gyani",
    "📄 PDF Summarizer",
    "🌐 Wikipedia Search",
    "🌍 Translate (EN <-> HI)",
    "🧠 Memory Mode",
    "📌 Commands (/help, /about)",
    "🏢 Smart File Tagging",
    "📚 Context-aware Chat",
    "🧮 Math Solver",
    "📰 Current Affairs (News)"
])

# Initialize history
if "history" not in st.session_state:
    st.session_state.history = []

# Chat with Gyani (Groq API)
if menu == "💬 Chat with Gyani":
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("Aapka prashn:", placeholder="Gyani se poochho...")
        submitted = st.form_submit_button("💬 Send")
    if submitted and user_input:
        st.session_state.history.append(("user", user_input))
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {groq_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama3-8b-8192",
                "messages": [{"role": "user", "content": user_input}]
            }
        )
        if response.status_code == 200:
            reply = response.json()["choices"][0]["message"]["content"]
            st.session_state.history.append(("gyani", reply))
            st.markdown(f"**🧠 Gyani:** {reply}")
        else:
            st.error("❌ Groq response error")

# PDF Summarizer
elif menu == "📄 PDF Summarizer":
    pdf = st.file_uploader("Upload PDF", type=["pdf"])
    if pdf:
        reader = PyPDF2.PdfReader(pdf)
        text = "".join(page.extract_text() or "" for page in reader.pages)
        st.text_area("📄 Extracted Text", value=text[:2000], height=300)

# Wikipedia Search
elif menu == "🌐 Wikipedia Search":
    search = st.text_input("Search Wikipedia:")
    if search:
        try:
            import wikipedia
            result = wikipedia.summary(search, sentences=3)
            st.success(result)
        except:
            st.warning("⚠️ Result not found or language error.")

# Translator (Hindi <-> English)
elif menu == "🌍 Translate (EN <-> HI)":
    from langdetect import detect
    from googletrans import Translator
    msg = st.text_input("Enter text to translate:")
    if msg:
        try:
            translator = Translator()
            lang = detect(msg)
            to_lang = "hi" if lang == "en" else "en"
            translated = translator.translate(msg, dest=to_lang).text
            st.success(f"Translated ({to_lang.upper()}): {translated}")
        except:
            st.error("Translation error")

# Placeholder for other features (skeleton)
else:
    st.info(f"{menu} feature is under development in Gyani v2.")
