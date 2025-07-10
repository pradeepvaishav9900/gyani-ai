import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
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
        <div style='text-align: center; padding-top: 30px;'>
            <h1 style='font-size:48px;'>Where ideas meet <span style='color:#7b68ee;'>creativity</span>.</h1>
            <p style='font-size:20px; color:gray;'>Liger helps you design and share stunning graphics in seconds — for free.</p>
            <a href='/?page=🎨+Design+Canvas'><button style='background-color:#7b68ee;color:white;border:none;padding:10px 25px;font-size:16px;border-radius:6px;margin-top:20px;'>Start designing</button></a>
        </div>
        <br><br>
        <div style='display: flex; justify-content: center; flex-wrap: wrap; gap: 30px;'>
            <div style='text-align:center;'>
                <img src='https://img.icons8.com/color/96/000000/presentation.png'/>
                <h4>Presentations</h4>
            </div>
            <div style='text-align:center;'>
                <img src='https://img.icons8.com/color/96/000000/instagram-new--v1.png'/>
                <h4>Social</h4>
            </div>
            <div style='text-align:center;'>
                <img src='https://img.icons8.com/color/96/000000/youtube-play.png'/>
                <h4>Videos</h4>
            </div>
            <div style='text-align:center;'>
                <img src='https://img.icons8.com/color/96/000000/print.png'/>
                <h4>Prints</h4>
            </div>
            <div style='text-align:center;'>
                <img src='https://img.icons8.com/color/96/000000/idea.png'/>
                <h4>Whiteboards</h4>
            </div>
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
    font_size = st.sidebar.slider("Font Size", 10, 100, 20)
    bg_image = st.sidebar.file_uploader("Upload Background Image", type=["png", "jpg", "jpeg"])

    # Filters
    st.sidebar.markdown("## 🎚 Photo Filters")
    brightness = st.sidebar.slider("Brightness", 0.5, 2.0, 1.0)
    contrast = st.sidebar.slider("Contrast", 0.5, 2.0, 1.0)
    sharpness = st.sidebar.slider("Sharpness", 0.5, 2.0, 1.0)
    blur_radius = st.sidebar.slider("Blur Radius", 0.0, 10.0, 0.0)

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
        image = ImageEnhance.Brightness(image).enhance(brightness)
        image = ImageEnhance.Contrast(image).enhance(contrast)
        image = ImageEnhance.Sharpness(image).enhance(sharpness)
        if blur_radius > 0:
            image = image.filter(ImageFilter.GaussianBlur(blur_radius))
        canvas_kwargs["background_image"] = image
        canvas_kwargs["height"] = image.height
        canvas_kwargs["width"] = image.width

    canvas_result = st_canvas(**canvas_kwargs)

    # Add text to image
    if st.sidebar.button("Add Text to Canvas"):
        if canvas_result.image_data is not None:
            img = Image.fromarray(canvas_result.image_data.astype("uint8"))
            draw = ImageDraw.Draw(img)
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
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
