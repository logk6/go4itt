import streamlit as st

# File uploader for MP3
uploaded_file = st.file_uploader("Upload an MP3 file", type=["mp3"])

if uploaded_file is not None:
    # Play the uploaded MP3
    st.audio(uploaded_file, format="audio/mp3")











