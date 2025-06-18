import gradio as gr
from transformers import pipeline

# Hinglish chatbot model (lightweight)
chatbot_model = pipeline("text-generation", model="rinna/bilingual-gpt-neox-4b")

def chatbot_response(message):
    result = chatbot_model(message, max_new_tokens=100, do_sample=True, temperature=0.7)[0]['generated_text']
    return f"🧠 Gyani: {result[len(message):].strip()}"

with gr.Blocks() as demo:
    gr.Markdown("""
    # 🤖 Gyani - Hinglish Chatbot  
    Developed by **Pradeep Vaishnav**
    """)

    chatbot = gr.Chatbot()
    msg = gr.Textbox(placeholder="💬 Ask your question in Hinglish...")
    clear = gr.Button("🧹 Clear Chat")

    def user(message, history):
        response = chatbot_response(message)
        history.append((message, response))
        return "", history

    msg.submit(user, [msg, chatbot], [msg, chatbot])
    clear.click(lambda: None, None, chatbot, queue=False)

demo.launch()
