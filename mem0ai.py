import os
from mem0 import Memory

# Đặt API Key của Google Gemini (lấy từ Google AI Studio)
os.environ["GOOGLE_API_KEY"] = "AIzaSyAot8_9M8Ku0ogIV41bQUb62t9kACH_YDA"


# Cấu hình Mem0 sử dụng Gemini làm LLM chính
config = {
    "llm": {
        "provider": "gemini",
        "config": {
            "model": "gemini-2.5-flash", # Hoặc gemini-1.5-pro, v.v.
            "temperature": 0.2,
            "max_tokens": 500,
        }
    }
}

# Khởi tạo Memory với cấu hình trên
m = Memory.from_config(config)

# 1. Thêm dữ liệu (Ví dụ: tin nhắn từ Assistant hoặc User)
messages = [
    {
        "role": "assistant", 
        "content": "Đã hỗ trợ người dùng tối ưu hóa đoạn code Python và xử lý thành công lỗi tensor size mismatch."
    }
]

m.add(messages, user_id="nguoi_dung_123")

# 2. Truy hồi ký ức
related_memories = m.search(query="Tôi gặp lỗi gì trước đây?", user_id="nguoi_dung_123")

for mem in related_memories:
    print(f"- {mem['memory']}")