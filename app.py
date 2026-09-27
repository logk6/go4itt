import streamlit as st
import os
import splittt
import sumar

st.title("Local MP3 Player")

audio_file_path = r"C:\Users\hp\Desktop\mpt\Đen - Trốn Tìm ft. MTV band (M-V).mp3"  # Replace with the path to your local MP3 file

try:
    # Open the local file in binary read mode
    with open(audio_file_path, "rb") as audio_file:
        audio_bytes = audio_file.read()
        
    # Play the audio bytes-
    st.audio(audio_bytes, format="audio/mp3")
    
    text_vocal = splittt.splitt(audio_file_path)
    text_summary = sumar.generate_text(f"Summarize the following text in Vietnamese: {text_vocal}")
    st.write("Transcript:")
    st.write(text_vocal)
    st.write("Summary:")
    st.write(text_summary)
    



except FileNotFoundError:
    st.error(f"Could not find the file at: {audio_file_path}")