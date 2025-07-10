import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from streamlit_drawable_canvas import st_canvas
import io

# Page settings
st.set_page_config(page_title="Liger - Design Anything", layout="wide", page_icon="🦁")

# 🦁 Display logo and app title
col1, col2 = st.columns([1, 8])
with col1:
    try:
        logo = Image.open("Liger Logo Design.png")
        st.image(logo, width=80)
    except FileNotFoundError:
        st.warning("⚠️ Logo not found. Please upload 'Liger Logo Design.png' in the app folder.")

with col2:
    st.markdown("""
        <h1 style='font-size:42px; margin-bottom:0;'>LIGER</h1>
        <p style='margin-top:0; font-size:18px; color:gray;'>Design like a beast — The fusion of Lion & Tiger</p>
    """, unsafe_allow_html=True)

st.markdown("---")

# Layout like Canva: sidebar left, canvas + controls center/right
left_col, center_col = st.columns([1, 4])

with left_col:
    st.sidebar.header("🛠 Tools")
    drawing_mode = st.sidebar.selectbox(
        "Drawing tool:", ("freedraw", "line", "rect", "circle", "transform")
    )
    stroke_width = st.sidebar.slider("Stroke width:", 1, 25, 3)
    stroke_color = st.sidebar.color_picker("Stroke color", "#000000")
    bg_image = st.sidebar.file_uploader("Upload Background Image", type=["png", "jpg", "jpeg"])

with center_col:
    st.subheader("🎨 Your Canvas")
    canvas_kwargs = {
        "fill_color": "rgba(255, 255, 255, 0.0)",
        "stroke_width": stroke_width,
        "stroke_color": stroke_color,
        "drawing_mode": drawing_mode,
        "key": "canvas"
    }

    if bg_image:
        image = Image.open(bg_image).convert("RGBA")
        canvas_kwargs.update({
            "background_image": image,
            "height": image.height,
            "width": image.width,
        })
    else:
        canvas_kwargs.update({
            "background_color": "#ffffff",
            "height": 500,
            "width": 800,
        })

    canvas_result = st_canvas(**canvas_kwargs)

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

    if st.button("💾 Save Your Design"):
        if canvas_result.image_data is not None:
            result_image = Image.fromarray(canvas_result.image_data.astype("uint8"))
            buf = io.BytesIO()
            result_image.save(buf, format="PNG")
            byte_im = buf.getvalue()
            st.download_button(label="📥 Download PNG", data=byte_im, file_name="liger_design.png", mime="image/png")
