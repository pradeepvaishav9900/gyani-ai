# 🤖 Gyani Code Generator 2.0 - Customized for Pradeep
# 🚀 Run this notebook on Google Colab with GPU (T4 or better)

!pip install -q transformers accelerate gradio

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import gradio as gr

# ✅ Better model for code generation
model_id = "deepseek-ai/deepseek-coder-1.3b-instruct"

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    trust_remote_code=True,
    torch_dtype=torch.float16,
    device_map="auto"
)

def make_prompt(user_input):
    return f"<|system|>\nYou are a helpful AI programmer. Generate clean and working code.\n<|user|>\n{user_input}\n<|assistant|>"

def generate_code(prompt):
    input_text = make_prompt(prompt)
    inputs = tokenizer(input_text, return_tensors="pt").to(model.device)
    output = model.generate(
        **inputs,
        max_new_tokens=256,
        temperature=0.7,
        do_sample=True,
        top_k=50,
        top_p=0.95,
        pad_token_id=tokenizer.eos_token_id
    )
    result = tokenizer.decode(output[0], skip_special_tokens=True)
    return result.split("<|assistant|>")[-1].strip()

# 🎨 Gradio Interface
gr.Interface(
    fn=generate_code,
    inputs=gr.Textbox(lines=4, placeholder="Apna program likhne ka idea yahan likhiye (Hindi/English)..."),
    outputs="code",
    title="🧠 Gyani Code Generator 2.0 - by Pradeep",
    description="DeepSeek Model ka use karke Python, C++, JS ke programs banayein – bas Hindi/English me batayein!"
).launch()
