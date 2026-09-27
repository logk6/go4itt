from google import genai
import os


def generate_text(prompt):
      

# Gán API key vào biến môi trường hoặc cấu hình trực tiếp
 os.environ["GEMINI_API_KEY"] = "AIzaSyAot8_9M8Ku0ogIV41bQUb62t9kACH_YDA"

 client = genai.Client()

 def generate_text(prompt):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            prompt,
            "Hãy tóm tắt nội dung trên thành 1 đoạn văn ngắn gọn, súc tích, dễ hiểu, bằng tiếng Việt"
        ]
    )
    return response.text
 

#print(response.text)