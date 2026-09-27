import os
import streamlit as st
from transformers import AutoModelForCausalLM, AutoTokenizer
import whisper
import chromadb
from sentence_transformers import SentenceTransformer


chroma_client = chromadb.PersistentClient(path="./local_memory")
collection = chroma_client.get_or_create_collection(name="chat_long_term_memory")


# Force offline mode so transformers doesn't ping huggingface.co
os.environ["HF_HUB_OFFLINE"] = "1"

MODEL_PATH = "gemma-3-270m"  # Path to your local folder containing model weights


'''
@st.cache_resource
def load_model():
  tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
  model = AutoModelForCausalLM.from_pretrained(
      MODEL_PATH, device_map="auto", torch_dtype="auto"
  )
  return tokenizer, model

@st.cache_resource
def load_embedder():
  return SentenceTransformer("all-MiniLM-L6-v2")
embedder = load_embedder()
'''

st.title("Gemma Offline App")
#tokenizer, model = load_model()

uploaded_file = st.file_uploader("Tải lên file MP3", type=["mp3"])
# Hàm tách lời theo câu
def split_sentences(text):
    # Tách theo dấu chấm, dấu chấm hỏi, dấu chấm than
    import re
    sentences = re.split(r'[.!?]', text)
    return [s.strip() for s in sentences if s.strip()]

if uploaded_file is not None:
    # Lưu file tạm
    with open("temp.mp3", "wb") as f:
        f.write(uploaded_file.read())

    # 🎤 Load mô hình Whisper
    st.write("Đang nhận diện lời bài hát tiếng Việt...")
    model = whisper.load_model("medium")  # có thể dùng "medium" hoặc "large" để chính xác hơn
    result = model.transcribe("temp.mp3", language="vi")  # ép ngôn ngữ tiếng Việt

    # Lấy lời bài hát
    lyrics = result["text"]
    st.subheader("Lời bài hát (tiếng Việt)")
    st.text_area("Lyrics", lyrics, height=300)

    # Tách lời theo câu
    st.subheader("Tách lời theo từng câu")
    sentences = split_sentences(lyrics)
    for i, sentence in enumerate(sentences, 1):
        st.write(f"**Câu {i}:** {sentence}")
  


'''
prompt = st.text_input("Enter your prompt:")
if prompt:
  inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
  outputs = model.generate(**inputs, max_new_tokens=200)
  response = tokenizer.decode(outputs[0], skip_special_tokens=True)
  st.write(response)
'''