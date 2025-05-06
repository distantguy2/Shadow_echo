🔗 Shadow Echo — Grok API Integration Guide
📘 Overview
Shadow Echo sử dụng Grok API để tăng tính chân thực và tương tác của NPC bằng cách cung cấp phản hồi ngữ nghĩa, hành vi AI nâng cao và các tình huống đối thoại được cá nhân hóa.

🤖 What Is Integrated?
Component	Description
npc_behavior.py	Sử dụng Grok để tạo phản hồi hội thoại như một NPC thông minh
grok_integration.py	Cầu nối xử lý gửi prompt tới Grok API và nhận kết quả
wave_generator.py	(Tùy chọn) Sử dụng AI để tạo ra các wave quái vật động

⚙️ Setup
1. Cài đặt thư viện yêu cầu
bash
Copy
Edit
pip install openai requests
2. Thêm biến môi trường API Key
bash
Copy
Edit
export GROK_API_KEY="your-api-key"
Hoặc trong .env:

ini
Copy
Edit
GROK_API_KEY=your-api-key
3. Cấu hình trong grok_integration.py
python
Copy
Edit
GROK_MODEL = "grok-3-mini-beta"
GROK_API_URL = "https://api.groq.com/v1/chat/completions"
🧠 Example Usage
📜 NPC Prompt Format
python
Copy
Edit
prompt = f"""
You are an NPC in a gothic horror game. Your name is Father Elric. You speak wisely and avoid revealing direct truths.

Player asks: "{player_input}"
Respond as Father Elric:
"""
📤 Sending to Grok API
python
Copy
Edit
response = call_grok_api(prompt)
print("NPC says:", response)
🧩 Output Example
vbnet
Copy
Edit
Player: "Do you know who's behind the murders?"
NPC: "Whispers in the chapel say the shadow wears a friendly face..."
🧪 Test It
bash
Copy
Edit
python src/ai/grok_integration.py
Hệ thống sẽ thử gửi prompt mẫu và in ra phản hồi.

🛠️ Functions Available
call_grok_api(prompt: str) -> str
Gửi đoạn prompt đến API và trả về nội dung phản hồi đầu tiên

build_prompt_from_npc(npc_name: str, player_input: str) -> str
Tạo prompt dựa trên thông tin NPC và câu hỏi người chơi

🔒 Rate Limits & Error Handling
Kiểm tra trạng thái 401 (API Key không hợp lệ)

Retry khi gặp lỗi 5xx hoặc timeout

Log toàn bộ prompt và response để debug nếu bật debug mode

🧭 Prompt Design Tips
Prompt Element	Description
Persona	"You are an old monk..."
Memory Context	Trích lại cuộc hội thoại nếu có
Instruction	"Answer cryptically but don't lie"
Output Format	"Respond in 1-2 sentences like a game NPC"

🧱 Future Expansion
Chat memory giữa NPC và player

Tự động sinh mới câu chuyện dựa trên hành động

Kết hợp Grok Vision cho nhận diện ảnh hoặc bản đồ