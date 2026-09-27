import tempfile
import time
import streamlit as st

import google.genai as genai

import os
from mem0 import Memory
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import lyricsgenius
import sentence_transformers

st.set_page_config(page_title="Ứng dụng Tóm tắt Lời bài hát bằng Gemini", page_icon="🎵", layout="centered")


def retry_transient_api_error(operation, *args, **kwargs):
    transient_status_codes = {408, 429, 500, 502, 503, 504}
    for attempt in range(3):
        try:
            return operation(*args, **kwargs)
        except Exception as exc:
            if getattr(exc, "code", None) not in transient_status_codes or attempt == 2:
                raise
            time.sleep(2 ** attempt)


'''
@st.cache_resource
def load_model():
    model_name = "gemma-3-270m"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.bfloat16,
        device_map="auto"
    )
    return tokenizer, model
tokenizer, model = load_model()
'''

@st.cache_resource
def lyricsgenius_client():
    return lyricsgenius.Genius("24_mjy08W4DXlM8nLeWCOYLo-nhM0fTE92c7dEOJ0WOCjaFAE-fPMjoOD1g2a2pD")
genius = lyricsgenius_client()


config = {
    "llm": {
        "provider": "gemini",
        "config": {
            "model": "gemini-3.5-flash",
            "api_key": 'AQ.Ab8RN6LloMM0JmIZNu4mJYmxywfeJUC0phk4WeOXY-tIKnNkgA'
        }
    },
    "embedder": {
        "provider": "huggingface",
        "config": {
            "model": "all-MiniLM-L6-v2"
        }
    },
    "vector_store": {
        "provider": "chroma",
        "config": {
            "collection_name": "my_memories",
            "path": "./chroma_db",
        }
    }
}

def get_memory():
    return Memory.from_config(config)

# Gọi hàm lấy memory (chú ý đặt tên hàm tránh trùng với tên biến m = mem0() cũ gây lỗi)
m = get_memory()





st.title("🎵 Trích xuất và Tóm tắt Lời bài hát (MP3)")
st.write("Tải lên tệp âm thanh/MP3 của bạn. Gemini sẽ nghe tệp trực tiếp, chép lại lời bài hát và tóm tắt ý nghĩa bằng **tiếng Việt**.")

# Nhập khóa API của Google GenAI
api_key = 'AQ.Ab8RN6LloMM0JmIZNu4mJYmxywfeJUC0phk4WeOXY-tIKnNkgA' #st.text_input("Nhập Khóa API Google Gemini của bạn:", type="password")

# Tiện ích tải lên tệp âm thanh
uploaded_file = st.file_uploader("Chọn một tệp âm thanh MP3", type=["mp3", "wav", "m4a"])

if uploaded_file is not None:
    # Trình phát lại âm thanh ngay trong ứng dụng
    st.audio(uploaded_file, format="audio/mp3")
    
    if st.button("Phân tích Lời bài hát & Tóm tắt"):
        if not api_key:
            st.error("Vui lòng nhập khóa API Gemini để tiếp tục.")
        else:
            try:
                # Khởi tạo client Google GenAI chính thức
                client = genai.Client(api_key=api_key)
                # Lưu tạm tệp tải lên vào đĩa để SDK có thể đọc tệp
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_file_path = tmp_file.name

                with st.spinner("Đang tải tệp âm thanh lên hệ thống Gemini..."):
                    # Tải tệp lên Google thông qua Files API
                    audio_file_ref = client.files.upload(file=tmp_file_path)
                
                with st.spinner("Gemini đang nghe, chép lại lời và phân tích bài hát..."):
                    # Yêu cầu Gemini xử lý tệp âm thanh và trả kết quả bằng tiếng Việt
                    response = retry_transient_api_error(
                        client.models.generate_content,
                        model="gemini-3.5-flash",
                        contents=[
                            audio_file_ref,
                            (
                                "Hãy nghe tệp âm thanh này và thực hiện các yêu cầu sau bằng tiếng Việt:\n"
                                
                                "1. Đưa ra một bản tóm tắt chi tiết, phân tích chủ đề chính, cảm xúc và thông điệp của bài hát.\n"
                                "2. Trình bày kết quả dưới dạng văn bản trong 5 câu"

                            ),
                        ],
                    )
                    
                    analysis_result = response.text

                # Xóa tệp tạm trên máy chủ Google sau khi đã xử lý xong
                client.files.delete(name=audio_file_ref.name)

                # Hiển thị kết quả ra giao diện
                st.success("Phân tích thành công!")
                st.markdown("### 📝 Lời bài hát & Tóm tắt nội dung")
                st.write(analysis_result)

                user_id = "nguoi_dung_123"
                retry_transient_api_error(
                    m.add,
                    [
                        {"role": "user", "content": "Phân tích bài hát đã tải lên."},
                        {"role": "assistant", "content": analysis_result},
                    ],
                    user_id=user_id,
                )

                memory_response = m.search(
                    query=analysis_result,
                    filters={"user_id": user_id},
                    top_k=5,
                )
                if isinstance(memory_response, dict):
                    related_memories = memory_response.get("results", [])
                else:
                    related_memories = memory_response or []

                memory_text = "\n".join(
                    f"- {memory['memory']}"
                    for memory in related_memories
                    if isinstance(memory, dict) and memory.get("memory")
                )
                prompt = (
                    "Phân tích bài hát hiện tại:\n"
                    f"{analysis_result}\n\n"
                    "Ký ức dài hạn liên quan:\n"
                    f"{memory_text or '- Chưa có ký ức liên quan.'}\n\n"
                    "Dựa trên nội dung hiện tại và ký ức liên quan, nêu chủ đề và "
                    "3 từ khóa chính bằng tiếng Việt trong 2 câu."
                )
                #inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
                #outputs = model.generate(**inputs, max_new_tokens=100)


                response2 = retry_transient_api_error(
                    client.models.generate_content,
                     model="gemini-3.5-flash",
                        contents=prompt
                )

                song = genius.search_song(response2.text)
                if song:
                    st.markdown("### 🎵 Thông tin bài hát")
                    st.write(f"**Tên bài hát:** {song.title}")
                    st.write(f"**Ca sĩ:** {song.artist}")
                    st.write(f"**Lời bài hát:** {song.lyrics[:200]}")

            except Exception as e:
                st.error(f"Đã xảy ra lỗi: {e}")
