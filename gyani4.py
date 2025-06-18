import streamlit as st
from PIL import Image, ImageFilter
import cv2
import numpy as np
import tempfile
import os

st.set_page_config(page_title="Gyani - Photo & Video Editing App", page_icon="🖼️")

# Title
st.title("🖼️ Gyani - Photo & Video Editing App")
st.subheader("Developed by Pradeep Vaishnav")

# Image Editing Section
st.header("Image Editing")
uploaded_image = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

if uploaded_image is not None:
    # Open the image
    image = Image.open(uploaded_image)
    st.image(image, caption="Original Image", use_column_width=True)

    # User input for editing instructions
    user_instruction = st.text_input("Enter your editing request (e.g., 'blur', 'enhance', 'resize to 300x200')")

    if st.button("Edit Image"):
        edited_image = image  # Start with the original image

        # Process user instructions
        if "blur" in user_instruction.lower():
            edited_image = image.filter(ImageFilter.BLUR)
            st.success("Image has been blurred.")
        elif "enhance" in user_instruction.lower():
            edited_image = image.filter(ImageFilter.SHARPEN)
            st.success("Image has been enhanced.")
        elif "resize" in user_instruction.lower():
            # Extract dimensions from the user input
            dimensions = user_instruction.lower().split("resize to")[-1].strip()
            try:
                width, height = map(int, dimensions.split('x'))
                edited_image = image.resize((width, height))
                st.success(f"Image has been resized to {width}x{height}.")
            except ValueError:
                st.warning("Please specify the dimensions in the format 'width x height' (e.g., '300x200').")
        else:
            st.warning("Sorry, I can't process that request. Please try another.")

        # Display the edited image
        st.image(edited_image, caption="Edited Image", use_column_width=True)

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

    # User input for video editing instructions
    user_video_instruction = st.text_input("Enter your video editing request (e.g., 'trim from 10 to 20 seconds')")

    if st.button("Edit Video"):
        if "trim" in user_video_instruction.lower():
            # Extract trim start and end times from the user input
            try:
                times = user_video_instruction.lower().split("trim from")[-1].strip()
                start_time, end_time = map(int, times.split("to"))
                
                # Load the video using OpenCV
                cap = cv2.VideoCapture(video_path)
                fps = cap.get(cv2.CAP_PROP_FPS)
                start_frame = int(start_time * fps)
                end_frame = int(end_time * fps)

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
                st.success(f"Video has been trimmed from {start_time} to {end_time} seconds.")
            except ValueError:
                st.warning("Please specify the trim times in the format 'trim from start to end' (e.g., 'trim from 10 to 20').")
        else:
            st.warning("Sorry, I can't process that request. Please try another.")

# Clean up temporary files
if uploaded_video is not None:
    os.remove(video_path)

# Footer
st.markdown("""
    <hr>
    <div style='text-align: center; color: gray;'>
        🤖 <strong>Gyani</strong> - Photo & Video Editing App developed by <strong>Pradeep Vaishnav</strong>.<br>
        All rights reserved. 🙏
    </div>
""", unsafe_allow_html=True)
