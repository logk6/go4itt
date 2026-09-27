import tempfile
import time
import streamlit as st
import google.genai as genai
from mem0 import Memory
import lyricsgenius

# ------------------ Cấu hình giao diện ------------------
st.set_page_config(page_title="Ứng dụng Tóm tắt Lời bài hát bằng Gemini", 
                   page_icon="🎵", layout="wide")

# ------------------ Sidebar ------------------
with st.sidebar:
    st.header("⚙️ Cấu hình")
    api_key = st.text_input("🔑 API Gemini", type="password")
    # Đổi mặc định thành gemini-2.5-flash
    model_choice = st.selectbox("Chọn mô hình Gemini", ["models/gemini-2.5-flash", "models/gemini-3.5-flash"])
    embedder_model = st.text_input("Embedder model", "all-MiniLM-L6-v2")

# ------------------ Khởi tạo Genius ------------------
@st.cache_resource
def lyricsgenius_client():
    return lyricsgenius.Genius("YOUR_GENIUS_API_KEY")
genius = lyricsgenius_client()

# ------------------ Config cho Mem0 ------------------
config = {
    "llm": {
        "provider": "gemini",
        "config": {
            "model": model_choice,
            "api_key": api_key
        }
    },
    "embedder": {
        "provider": "huggingface",
        "config": {
            "model": embedder_model
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

m = get_memory()

# ------------------ Tabs ------------------
tab1, tab2, tab3 = st.tabs(["🎵 Phân tích bài hát", "🔍 Tìm bài hát theo lyric", "🧠 Ký ức"])

# -------- Tab 1: Upload & Phân tích MP3 --------
with tab1:
    st.subheader("Upload & Phân tích MP3")
    uploaded_file = st.file_uploader("Chọn file âm thanh", type=["mp3", "wav", "m4a"])
    if uploaded_file:
        st.audio(uploaded_file, format="audio/mp3")
        if st.button("Phân tích Lời bài hát & Tóm tắt"):
            if not api_key:
                st.error("Vui lòng nhập API Gemini trong sidebar.")
            else:
                try:
                    client = genai.Client(api_key=api_key)
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_file_path = tmp_file.name

                    with st.spinner("Đang tải tệp âm thanh lên Gemini..."):
                        audio_file_ref = client.files.upload(file=tmp_file_path)

                    with st.spinner("Gemini đang nghe và phân tích..."):
                        response = client.models.generate_content(
                            model=model_choice,
                            contents=[
                                audio_file_ref,
                                (
                                    "Hãy nghe tệp âm thanh này và thực hiện các yêu cầu sau bằng tiếng Việt:\n"
                                    "1. Tóm tắt chi tiết, phân tích chủ đề chính, cảm xúc và thông điệp.\n"
                                    "2. Trình bày kết quả trong 5 câu."
                                ),
                            ],
                        )
                        analysis_result = response.text

                    client.files.delete(name=audio_file_ref.name)

                    st.success("Phân tích thành công!")
                    st.markdown("### 📝 Tóm tắt nội dung")
                    st.write(analysis_result)

                    # Lưu vào memory
                    user_id = "nguoi_dung_123"
                    m.add(
                        [
                            {"role": "user", "content": "Phân tích bài hát đã tải lên."},
                            {"role": "assistant", "content": analysis_result},
                        ],
                        user_id=user_id,
                    )

                    # Sinh mô tả ngắn gọn từ kết quả phân tích
                    prompt = (
                        "Dựa trên phân tích sau đây:\n"
                        f"{analysis_result}\n\n"
                        "Hãy tạo một mô tả ngắn gọn (2 câu) về chủ đề, cảm xúc và thông điệp chính của bài hát."
                    )

                    response2 = client.models.generate_content(
                        model=model_choice,
                        contents=prompt
                    )
                    description_text = response2.text

                    st.markdown("### 📝 Mô tả ngắn gọn")
                    st.write(description_text)

                    # Tự động tìm bài hát theo mô tả gần đúng
                    song = genius.search_song(description_text)
                    if song:
                        st.markdown("### 🎵 Thông tin bài hát gần đúng")
                        st.write(f"**Tên bài hát:** {song.title}")
                        st.write(f"**Ca sĩ:** {song.artist}")
                        st.text_area("Lời bài hát", song.lyrics[:500])
                    else:
                        st.warning("Không tìm thấy bài hát phù hợp với mô tả.")

                except Exception as e:
                    st.error(f"Đã xảy ra lỗi: {e}")

# -------- Tab 2: Tìm bài hát theo lyric --------
with tab2:
    st.subheader("Tìm bài hát theo lời hát")
    lyric_query = st.text_input("Nhập một đoạn lyric gần đúng:")
    if lyric_query and st.button("Tìm bài hát"):
        song = genius.search_song(lyric_query)
        if song:
            st.success(f"🎶 {song.title} - {song.artist}")
            st.text_area("Lời bài hát", song.lyrics[:500])
        else:
            st.warning("Không tìm thấy bài hát phù hợp.")

# -------- Tab 3: Ký ức --------
with tab3:
    st.subheader("Ký ức đã lưu")
    user_id = "nguoi_dung_123"
    memory_response = m.search(query="bài hát", filters={"user_id": user_id}, top_k=5)
    if isinstance(memory_response, dict):
        related_memories = memory_response.get("results", [])
    else:
        related_memories = memory_response or []
    if related_memories:
        st.write("Các ký ức liên quan:")
        for mem in related_memories:
            st.write(f"- {mem.get('memory')}")
    else:
        st.info("Chưa có ký ức nào được lưu.")
