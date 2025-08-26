import streamlit as st
import requests

# -------------------------------
# App Title
# -------------------------------
st.set_page_config(page_title="Gyani AI", page_icon="🧠", layout="wide")
st.title("🧠 Gyani AI - Chat with Groq API")

# -------------------------------
# Sidebar for API Key & Settings
# -------------------------------
st.sidebar.header("Settings")
api_key = st.sidebar.text_input("Enter your Groq API Key", type="password", value="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")
model = st.sidebar.selectbox("Choose Model", ["llama3-8b-8192", "mixtral-8x7b-32768"])
temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.7)

# -------------------------------
# Chat History
# -------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# -------------------------------
# Chat Input
# -------------------------------
st.subheader("💬 Start Chatting")
user_input = st.text_input("Ask something...", placeholder="Type your question here...")

# -------------------------------
# Function to call Groq API
# -------------------------------
def get_groq_response(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature
    }
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        return data["choices"][0]["message"]["content"]
    else:
        return f"Error: {response.status_code} - {response.text}"

# -------------------------------
# Process User Input
# -------------------------------
if st.button("Send"):
    if user_input.strip() != "":
        # Add user message to history
        st.session_state.chat_history.append(("You", user_input))

        # Get response from Groq API
        with st.spinner("Thinking..."):
            ai_response = get_groq_response(user_input)

        # Add AI response to history
        st.session_state.chat_history.append(("Gyani", ai_response))

# -------------------------------
# Display Chat History
# -------------------------------
st.subheader("📜 Chat History")
for sender, message in st.session_state.chat_history:
    if sender == "You":
        st.markdown(f"**🧑 You:** {message}")
    else:
        st.markdown(f"**🤖 Gyani:** {message}")
