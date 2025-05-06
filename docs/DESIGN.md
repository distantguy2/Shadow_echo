🕯️ Shadow Echo — Game Design Document
🎮 Overview
Shadow Echo là một tựa game sinh tồn trinh thám góc nhìn từ trên xuống (top-down) với yếu tố PvPvE, nơi người chơi xuyên không vào một thế giới lạ, không biết mình là ai hay nhiệm vụ là gì. Trong số các NPC, có một người chơi khác đang ẩn thân, và bạn phải tìm ra kẻ đó trước khi hắn phát hiện bạn.

🧱 Core Gameplay Loop
Ngày:

Khám phá bản đồ

Thu thập tài nguyên

Tương tác với NPC

Xây dựng, hồi máu, chuẩn bị

Đêm:

Xuất hiện quái vật

PvE đấu tranh sinh tồn

PvP âm thầm nếu người chơi phát hiện nhau

Một số thẻ bài sẽ có hiệu ứng khác nhau giữa ngày và đêm

🧩 Roles & Mechanics
🎭 Roles
Symbol	Name	Objective
♕	Protector	Bảo vệ NPC và tiêu diệt Traitor
♛	Traitor	Ám sát người chơi và NPC
☢	Chaos	Gây hỗn loạn, thắng bằng bất ngờ

Mỗi vai trò sẽ có thẻ bài đặc biệt để kích hoạt kỹ năng.

🃏 Card System
3 loại: weapon, utility, consumable

Một số thẻ mang 2 hiệu ứng: ngày và đêm

Thẻ hiếm kích hoạt vai trò thật

🧠 AI Behavior
NPC: có hành vi bán ngẫu nhiên nhưng phản ứng theo vai trò.

Monster AI: tìm và tấn công gần nhất.

Grok Integration (Optional): dùng Grok API để tạo phản hồi tự nhiên cho NPC.

🌐 Multiplayer
WebSocket-based real-time server

Lobby system (tối đa 5 người chơi/lobby)

State đồng bộ giữa client-server

Spectator Mode & Voice chat (optional)

Ready system trước khi bắt đầu

🖥️ Interface
pygame_ui.py: đồ họa top-down sử dụng sprites

curses_ui.py: hỗ trợ giao diện ASCII terminal (debug)

multiplayer_ui.py: hỗ trợ kết nối, tạo/join lobby, hiển thị status

🔁 Phases
Preparation Phase

Người chơi chuẩn bị trước khi đêm đến

Night Phase

PvE/PvP bắt đầu

Judgment

Người chơi đoán vai trò hoặc sử dụng thẻ xác nhận

Victory Check

Kiểm tra xem ai thắng, hoặc chuyển sang ngày mới

🧾 Command System
Người chơi nhập các lệnh như:

lua
Copy
Edit
build barricade --pos=north_gate
use ✚ --target=self
scan area
attack ♛
Hệ thống parser sẽ xử lý lệnh và đưa kết quả

🗺️ World Map
Dạng ô vuông 2D grid

Bao gồm:

Monastery

Graveyard

Forest

Hidden Caves

Ban đêm hạn chế tầm nhìn

🧪 Test Plan
Unit Test cho combat, role, command, card

Integration Test: multiplayer server

Load Testing: mô phỏng 50 client

⚙️ Extensibility
Thêm vai trò mới dễ dàng qua cards.json

Thêm bản đồ, NPC, quái vật qua file data/

Hỗ trợ AI động qua grok_integration.py

