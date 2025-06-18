import streamlit as st
from PIL import Image, ImageFilter
import cv2
import numpy as np
import tempfile
import os

st.set_page_config(page_title="Photo & Video Editing App", page_icon="🖼️")

# Title
st.title("🖼️ Photo & Video Editing App")

# Image Editing Section
st.header("Image Editing")
uploaded_image = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

if uploaded_image is not None:
    # Open the image
    image = Image.open(uploaded_image)
    st.image(image, caption="Original Image", use_column_width=True)

    # Image Editing Options
    edit_option = st.selectbox("Choose an editing option", ["None", "Blur", "Enhance", "Resize"])

    if edit_option == "Blur":
        if st.button("Apply Blur"):
            edited_image = image.filter(ImageFilter.BLUR)
            st.image(edited_image, caption="Blurred Image", use_column_width=True)

    elif edit_option == "Enhance":
        if st.button("Enhance Image"):
            edited_image = image.filter(ImageFilter.SHARPEN)
            st.image(edited_image, caption="Enhanced Image", use_column_width=True)

    elif edit_option == "Resize":
        width = st.number_input("Enter new width", min_value=1, value=image.width)
        height = st.number_input("Enter new height", min_value=1, value=image.height)
        if st.button("Resize Image"):
            edited_image = image.resize((width, height))
            st.image(edited_image, caption="Resized Image", use_column_width=True)

# Video Editing Section
st.header("Video Editing")
uploaded_video = st.file_uploader("Upload a video", type=["mp4", "mov", "avi"])

if uploaded_video is not None:
    # Save the uploaded video to a temporary file
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_video.read())
    video_path = tfile.name

    # Display the video
    st.video(video_path)

    # Video Editing Options
    st.subheader("Video Editing Options")
    trim_start = st.number_input("Trim Start (seconds)", min_value=0, value=0)
    trim_end = st.number_input("Trim End (seconds)", min_value=0, value=10)

    if st.button("Trim Video"):
        # Load the video using OpenCV
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        start_frame = int(trim_start * fps)
        end_frame = int(trim_end * fps)

        # Create a VideoWriter object
        output_path = os.path.join(tempfile.gettempdir(), "trimmed_video.mp4")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (int(cap.get(3)), int(cap.get(4))))

        # Read and write frames
        current_frame = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            if start_frame <= current_frame <= end_frame:
                out.write(frame)
            current_frame += 1

        cap.release()
        out.release()

        # Display the trimmed video
        st.video(output_path)

# Clean up temporary files
if uploaded_video is not None:
    os.remove(video_path)
