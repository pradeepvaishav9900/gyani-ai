# STEP 1: Install required packages
!pip install transformers gradio

# STEP 2: Load FLAN-T5-Large model
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import gradio as gr

model_name = "google/flan-t5-large"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

def generate_response(prompt):
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_length=256)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# STEP 3: Gradio Chat Interface
def chat_fn(user_input, chat_history):
    response = generate_response(user_input)
    chat_history = chat_history or []
    chat_history.append((user_input, response))
    return chat_history, chat_history

with gr.Blocks() as demo:
    gr.Markdown("## 🧠 Gyani Lite (T4 GPU Compatible)")
    chatbot = gr.Chatbot()
    msg = gr.Textbox(placeholder="Gyani se kuch bhi poochho...")
    state = gr.State()
    msg.submit(chat_fn, [msg, state], [chatbot, state])
    msg.submit(lambda: "", None, msg)
    demo.launch(share=True)
