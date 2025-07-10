import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from streamlit_drawable_canvas import st_canvas
import io

st.set_page_config(page_title="Liger - Design Anything", page_icon="🦁")
st.title("🦁🐯 Liger - Your Creative Canvas")
st.markdown("Design with the power of **Lion + Tiger** 🖌️")

# Canvas settings
stroke_width = st.sidebar.slider("Stroke width:", 1, 25, 3)
stroke_color = st.sidebar.color_picker("Stroke color", "#000000")

# Upload background image
bg_image = st.sidebar.file_uploader("Upload Background Image", type=["png", "jpg", "jpeg"])
if bg_image:
    image = Image.open(bg_image)
    image = image.convert("RGBA")
    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 0.0)",
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_image=image,
        height=image.height,
        width=image.width,
        drawing_mode="freedraw",
        key="canvas",
    )
else:
    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 0.0)",
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color="#ffffff",
        height=400,
        width=600,
        drawing_mode="freedraw",
        key="canvas",
    )

# Add text
st.subheader("📝 Add Text")
text_input = st.text_input("Enter your text:", "My Liger Design")
text_color = st.color_picker("Text Color", "#000000")

if st.button("Add Text to Canvas"):
    if canvas_result.image_data is not None:
        img = Image.fromarray(canvas_result.image_data.astype("uint8"))
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()
        draw.text((50, 50), text_input, font=font, fill=text_color)
        st.image(img)

# Save image
if st.button("💾 Save Your Design"):
    if canvas_result.image_data is not None:
        result_image = Image.fromarray(canvas_result.image_data.astype("uint8"))
        buf = io.BytesIO()
        result_image.save(buf, format="PNG")
        byte_im = buf.getvalue()
        st.download_button(label="📥 Download PNG", data=byte_im, file_name="liger_design.png", mime="image/png")
