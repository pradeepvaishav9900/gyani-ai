import openai
import gradio as gr
import os

# 🔝 Set your OpenAI API key here
openai.api_key = "YOUR_OPENAI_API_KEY"  # 🔁 Replace this with your actual key or use os.getenv("OPENAI_API_KEY")

def gyani_chatbot(user_input):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Or use "gpt-4" if your key supports it
            messages=[
                {"role": "system", "content": "Tumhara naam Gyani hai. Tum ek helpful aur smart AI ho jo Hindi aur English dono mein baat karta hai."},
                {"role": "user", "content": user_input}
            ],
            temperature=0.7,
            max_tokens=200
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"❌ Error: {str(e)}"

# 🧠 Gradio UI
demo = gr.Interface(
    fn=gyani_chatbot,
    inputs=gr.Textbox(placeholder="Apna prashn yahan likho..."),
    outputs=gr.Textbox(label="🧠 Gyani ka Uttar"),
    title="Gyani - Aapka AI Sathi",
    description="💬 Hindi-English AI Chatbot powered by OpenAI"
)

# 🔁 Launch
demo.launch()
