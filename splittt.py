import os
import subprocess
from importlib import import_module

try:
   whisper = import_module("whisper")
except ModuleNotFoundError as exc:
   if exc.name == "whisper":
      raise ModuleNotFoundError(
         "The Whisper package is missing. Install it with: pip install openai-whisper"
      ) from exc
   raise


def splitt(input_file_name):
    
# 1. Cấu hình tên file đầu vào
 input_file = "Đen - Trốn Tìm ft. MTV band (M-V).mp3"  # Thay bằng đường dẫn file nhạc của bạn
 #input_file = input_file_name

 print("--- Đang tiến hành tách giọng hát (Demucs) ---")
# Sử dụng mô hình htdemucs để tách stem (tách vocal ra khỏi nhạc nền)
# Lệnh này sẽ tạo ra thư mục separated/htdemucs/input_file_name/
 subprocess.run(["demucs", "-n", "htdemucs", input_file], check=True)

# Xác định đường dẫn file vocal sau khi tách
 base_name = os.path.splitext(os.path.basename(input_file))[0]
 vocal_path = os.path.join("separated", "htdemucs", base_name, "vocals.wav")

 print(f"Đã tách xong! File giọng hát lưu tại: {vocal_path}")

 print("--- Đang chuyển giọng hát thành văn bản (Whisper) ---")
# Tải mô hình Whisper (bạn có thể đổi thành 'small', 'medium', hoặc 'large' tùy cấu hình)
 model = whisper.load_model("base")

# Thực hiện nhận diện giọng nói (có thể chỉ định language="vi" nếu là tiếng Việt)
 result = model.transcribe(vocal_path, language="vi")

# In kết quả ra màn hình
 #print("\n--- KẾT QUẢ VĂN BẢN ---")
 #print(result["text"])

# Lưu kết quả ra file txt
 output_txt = f"{base_name}_transcript.txt"
 #with open(output_txt, "w", encoding="utf-8") as f:
    #f.write(result["text"])

 #print(f"\nĐã lưu toàn bộ văn bản vào file: {output_txt}")
 return result["text"]
