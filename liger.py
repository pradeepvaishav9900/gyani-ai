import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from streamlit_drawable_canvas import st_canvas
import io

# Page settings
st.set_page_config(page_title="Liger - Design Anything", layout="wide", page_icon="🦁")

# Sidebar Navigation
st.sidebar.title("LIGER")
page = st.sidebar.radio("Go to", ["🏠 Home", "🎨 Design Canvas"])

# 🦁 Display logo and app title
with st.container():
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

# Home Page
if page == "🏠 Home":
    st.markdown("""
    <div style='text-align: center;'>
        <h2>Welcome to LIGER</h2>
        <p style='font-size:18px;'>Liger is a free, web-based design tool just like Canva — made for everyone who loves to create.</p>
        <img src='https://cdn-icons-png.flaticon.com/512/2921/2921222.png' width='150'>
        <p style='margin-top:20px;'>Click on <strong>🎨 Design Canvas</strong> in the sidebar to start creating now!</p>
    </div>
    """, unsafe_allow_html=True)

# Design Page
elif page == "🎨 Design Canvas":
    # Sidebar Tools
    st.sidebar.markdown("## 🛠 Toolbar")
    drawing_mode = st.sidebar.selectbox("Tool", ("freedraw", "line", "rect", "circle", "transform"))
    stroke_width = st.sidebar.slider("Stroke width", 1, 25, 3)
    stroke_color = st.sidebar.color_picker("Stroke color", "#000000")
    fill_color = st.sidebar.color_picker("Fill color (for shapes)", "#ffffff")
    text_input = st.sidebar.text_input("Text to Add", "My Liger Design")
    text_color = st.sidebar.color_picker("Text Color", "#000000")
    text_pos_x = st.sidebar.slider("Text X Position", 0, 800, 50)
    text_pos_y = st.sidebar.slider("Text Y Position", 0, 500, 50)
    bg_image = st.sidebar.file_uploader("Upload Background Image", type=["png", "jpg", "jpeg"])

    # Main Canvas Area
    st.subheader("🎨 Design Canvas")
    canvas_kwargs = {
        "fill_color": fill_color + "80",  # semi-transparent fill
        "stroke_width": stroke_width,
        "stroke_color": stroke_color,
        "drawing_mode": drawing_mode,
        "key": "canvas",
        "update_streamlit": True,
        "background_color": "#ffffff",
        "height": 500,
        "width": 800,
    }

    if bg_image:
        image = Image.open(bg_image).convert("RGBA")
        canvas_kwargs["background_image"] = image
        canvas_kwargs["height"] = image.height
        canvas_kwargs["width"] = image.width

    canvas_result = st_canvas(**canvas_kwargs)

    # Add text to image
    if st.sidebar.button("Add Text to Canvas"):
        if canvas_result.image_data is not None:
            img = Image.fromarray(canvas_result.image_data.astype("uint8"))
            draw = ImageDraw.Draw(img)
            font = ImageFont.load_default()
            draw.text((text_pos_x, text_pos_y), text_input, font=font, fill=text_color)
            st.image(img)

    # Save functionality
    if st.sidebar.button("💾 Save Design"):
        if canvas_result.image_data is not None:
            result_image = Image.fromarray(canvas_result.image_data.astype("uint8"))
            buf = io.BytesIO()
            result_image.save(buf, format="PNG")
            byte_im = buf.getvalue()
            st.download_button(label="📥 Download PNG", data=byte_im, file_name="liger_design.png", mime="image/png")
