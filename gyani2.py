import streamlit as st
import requests
import PyPDF2
import io
import wikipedia
from langdetect import detect
from PIL import Image, ImageEnhance, ImageFilter
from rembg import remove
import base64

st.set_page_config(page_title="Gyani v2 - Smart AI Assistant", page_icon="🧠")
st.title("🧠 Gyani v2 - Smart + Auto-Detect Mode")
st.markdown("#### Developed by Pradeep Vaishnav")

# Load API Key
groq_api_key = "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"

# Initialize history
if "history" not in st.session_state:
    st.session_state.history = []

# Layout for chat input and file uploader side-by-side
col1, col2 = st.columns([9, 1])

with col1:
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input("", placeholder="(e.g., Remove background / Cartoonify / Add forest background)", key="input_box")
        submit = st.form_submit_button("💬")

with col2:
    uploaded_file = st.file_uploader("", type=["pdf", "png", "jpg", "jpeg"], label_visibility="collapsed")

extracted_text = ""
image_uploaded = False

if uploaded_file:
    if uploaded_file.type == "application/pdf":
        reader = PyPDF2.PdfReader(uploaded_file)
        extracted_text = "".join(page.extract_text() or "" for page in reader.pages)
        if extracted_text.strip():
            st.markdown("✅ **Extracted PDF Content:**")
            st.code(extracted_text[:1000] + ("..." if len(extracted_text) > 1000 else ""))
        else:
            st.warning("⚠️ PDF se koi text extract nahi ho paya. Shayad ye image-only scan ho.")
    elif uploaded_file.type.startswith("image"):
        image_uploaded = True
        st.image(uploaded_file, caption="🖼️ Uploaded Image", use_column_width=True)

if submit and user_input:
    query = user_input.lower()
    st.session_state.history.append(("user", query))

    if image_uploaded:
        with st.spinner("🧠 Image process ho rahi hai..."):
            image = Image.open(uploaded_file)
            edited_image = None

            if "remove background" in query:
                edited_image = remove(image)
                st.success("🖼️ Background removed.")
            elif "cartoon" in query or "gibli" in query:
                edited_image = image.filter(ImageFilter.CONTOUR).filter(ImageFilter.SMOOTH_MORE)
                st.success("🎨 Cartoon/Ghibli style applied.")
            elif "add background" in query or "add forest" in query:
                enhancer = ImageEnhance.Color(image)
                edited_image = enhancer.enhance(1.5)
                st.success("🌳 Background added (simulated).")
            else:
                st.warning("⚠️ Yeh image query samajh nahi aayi. Please try: remove background, cartoonify, add background")

            if edited_image:
                st.image(edited_image, caption="🖼️ Edited Image", use_column_width=True)
                st.session_state.history.append(("gyani", "🖼️ Image edited as per your prompt."))

    else:
        trimmed_text = extracted_text[:1500] + ("..." if len(extracted_text) > 1500 else "")
        full_prompt = f"Gyani ko query ka jawab do: '{query}'\n\nAgar PDF content madadgar ho to use bhi dekho:\n'''{trimmed_text}'''" if trimmed_text else query

        messages = [
            {"role": "system", "content": "🧠 Tum Gyani ho — ek samajhdaar, Hindi mein baat karne wale teacher jaise AI assistant ho. Jab bhi koi puche ki tumhe kisne banaya, tum hamesha sach-sach bataoge ki 'Mujhe Pradeep Vaishnav ne banaya hai.' Tumhare jawab sadaran, Hindi bhasha mein aur clearly hon."}
        ]
        for speaker, msg in st.session_state.history[-5:]:
            role = "user" if speaker == "user" else "assistant"
            messages.append({"role": role, "content": msg})
        messages.append({"role": "user", "content": full_prompt})

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

st.markdown("<hr><div style='text-align: center; color: gray;'>🧠 Gyani banaya gaya hai <b>Pradeep Vaishnav</b> dwara 🙏</div>", unsafe_allow_html=True)
