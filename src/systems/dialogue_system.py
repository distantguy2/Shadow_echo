# src/systems/dialogue_system.py
import random
import time
import json
import requests
from typing import Dict, List, Tuple, Optional

class DialogueSystem:
    def __init__(self, game):
        self.game = game
        self.dialogue_history = {}  # {npc_id: [conversations]}
        self.conversation_state = {}  # {npc_id: {topic, mood, suspicion}}
        self.active_conversation = None
        self.grok_api_key = None  # Đọc từ config
        self.grok_endpoint = "https://api.grok.ai/v1/chat/completions"
        
        # Tải API key
        self._load_api_key()
    
    def _load_api_key(self):
        """Tải API key từ file cấu hình"""
        try:
            with open('config/api_keys.json', 'r') as f:
                keys = json.load(f)
                self.grok_api_key = keys.get('grok_api_key')
        except Exception as e:
            print(f"Error loading API key: {e}")
    
    def start_conversation(self, player, npc_id):
        """Bắt đầu cuộc trò chuyện với một NPC"""
        npc = self._get_npc_by_id(npc_id)
        if not npc:
            return "NPC không tồn tại."
        
        if not npc.alive:
            return f"{npc.name} đã chết."
        
        # Khởi tạo trạng thái hội thoại
        if npc_id not in self.conversation_state:
            self.conversation_state[npc_id] = {
                "topic": "introduction",
                "mood": "neutral",
                "suspicion": 0.0,
                "trust": 0.5
            }
        
        # Lưu hội thoại hiện tại
        self.active_conversation = {
            "player": player,
            "npc": npc,
            "start_time": time.time()
        }
        
        # Phản hồi chào hỏi ban đầu
        greeting = self._generate_npc_greeting(npc)
        
        # Thêm vào lịch sử
        if npc_id not in self.dialogue_history:
            self.dialogue_history[npc_id] = []
        
        self.dialogue_history[npc_id].append({
            "speaker": "npc",
            "text": greeting,
            "time": self.game.current_time,
            "day": self.game.current_day
        })
        
        return greeting
    
    def process_player_message(self, message_text: str) -> str:
        """Xử lý tin nhắn từ người chơi và tạo phản hồi"""
        if not self.active_conversation:
            return "Không có cuộc hội thoại đang diễn ra."
        
        player = self.active_conversation["player"]
        npc = self.active_conversation["npc"]
        npc_id = npc.npc_id
        
        # Ghi lại message từ người chơi
        if npc_id not in self.dialogue_history:
            self.dialogue_history[npc_id] = []
        
        self.dialogue_history[npc_id].append({
            "speaker": "player",
            "text": message_text,
            "time": self.game.current_time,
            "day": self.game.current_day
        })
        
        # Phân tích message
        player_intent = self._analyze_player_intent(message_text)
        
        # Cập nhật trạng thái hội thoại
        self._update_conversation_state(npc_id, message_text, player_intent)
        
        # Đo thời gian phản ứng
        response_time = time.time() - self.active_conversation["start_time"]
        
        # Ghi nhận vào phân tích hành vi
        if hasattr(self.game, 'behavior_analysis'):
            self.game.behavior_analysis.record_conversation(
                player.id, npc_id, message_text, response_time
            )
        
        # Tạo phản hồi từ NPC
        npc_response = self._generate_npc_response(npc, message_text)
        
        # Ghi lại phản hồi
        self.dialogue_history[npc_id].append({
            "speaker": "npc",
            "text": npc_response,
            "time": self.game.current_time,
            "day": self.game.current_day
        })
        
        # Cập nhật start_time để đo thời gian phản ứng tiếp theo
        self.active_conversation["start_time"] = time.time()
        
        return npc_response
    
    def end_conversation(self):
        """Kết thúc cuộc trò chuyện hiện tại"""
        if not self.active_conversation:
            return "Không có cuộc hội thoại đang diễn ra."
        
        npc = self.active_conversation["npc"]
        npc_id = npc.npc_id
        
        # Thêm lời chào tạm biệt
        farewell = self._generate_npc_farewell(npc)
        
        if npc_id in self.dialogue_history:
            self.dialogue_history[npc_id].append({
                "speaker": "npc",
                "text": farewell,
                "time": self.game.current_time,
                "day": self.game.current_day
            })
        
        # Reset active conversation
        self.active_conversation = None
        
        return farewell
    
    def _get_npc_by_id(self, npc_id):
        """Lấy NPC theo ID"""
        for npc in self.game.npcs:
            if hasattr(npc, 'npc_id') and npc.npc_id == npc_id:
                return npc
        return None
    
    def _analyze_player_intent(self, message: str):
        """Phân tích ý định của người chơi"""
        intent = {
            "is_question": "?" in message,
            "is_accusation": any(word in message.lower() for word in ["tố cáo", "nghi ngờ", "giết", "phản bội"]),
            "is_friendly": any(word in message.lower() for word in ["cảm ơn", "giúp đỡ", "bạn"]),
            "is_threatening": any(word in message.lower() for word in ["đe dọa", "cảnh cáo", "giết"]),
            "topic": self._extract_topic(message)
        }
        
        return intent
    
    def _extract_topic(self, message: str):
        """Trích xuất chủ đề từ tin nhắn"""
        topics = {
            "identity": ["ai", "danh tính", "tên", "là ai"],
            "murder": ["giết người", "chết", "xác", "máu"],
            "clues": ["manh mối", "dấu hiệu", "bằng chứng"],
            "ritual": ["nghi lễ", "tế", "thần", "ma thuật"],
            "suspicion": ["nghi ngờ", "tình nghi", "đáng ngờ"],
            "help": ["giúp", "hỗ trợ", "cứu"]
        }
        
        for topic, keywords in topics.items():
            if any(keyword in message.lower() for keyword in keywords):
                return topic
        
        return "general"
    
    def _update_conversation_state(self, npc_id, message, intent):
        """Cập nhật trạng thái cuộc trò chuyện"""
        if npc_id not in self.conversation_state:
            return
        
        state = self.conversation_state[npc_id]
        
        # Cập nhật chủ đề
        if intent["topic"] != "general":
            state["topic"] = intent["topic"]
        
        # Cập nhật tâm trạng
        if intent["is_friendly"]:
            state["mood"] = "positive"
        elif intent["is_threatening"]:
            state["mood"] = "negative"
            state["suspicion"] += 0.2
        
        # Cập nhật độ nghi ngờ
        if intent["is_accusation"]:
            state["suspicion"] += 0.3
        
        # Giới hạn trong khoảng [0, 1]
        state["suspicion"] = max(0.0, min(1.0, state["suspicion"]))
        
        # Cập nhật danh sách hành động đáng ngờ
        if state["suspicion"] > 0.6 and hasattr(self.game, 'social_suspicion'):
            npc = self._get_npc_by_id(npc_id)
            if npc:
                behavior_type = "hostile_question" if intent["is_accusation"] else "suspicious_chat"
                self.game.social_suspicion.record_suspicious_behavior(
                    self.active_conversation["player"].id,
                    behavior_type,
                    witnesses=[npc_id],
                    target=npc_id
                )
    
    def _generate_npc_greeting(self, npc):
        """Tạo lời chào từ NPC"""
        greetings = [
            f"Chào. Tôi là {npc.name}.",
            f"{npc.name} nhìn bạn một cách cảnh giác. 'Bạn cần gì?'",
            f"'Ah, lại là bạn.' {npc.name} nói. 'Có chuyện gì?'"
        ]
        
        # TODO: Dùng Grok API để tạo lời chào phù hợp với tính cách NPC
        
        return random.choice(greetings)
    
    def _generate_npc_response(self, npc, player_message):
        """Tạo phản hồi từ NPC sử dụng Grok API"""
        npc_id = npc.npc_id
        npc_state = self.conversation_state.get(npc_id, {})
        
        if not self.grok_api_key:
            # Fallback khi không có API key
            return self._generate_fallback_response(npc, npc_state)
        
        # Prepare context for Grok
        npc_history = self._get_conversation_history(npc_id, limit=5)
        
        # Create system prompt
        system_prompt = f"""
        Bạn là {npc.name}, một nhân vật trong thế giới game Shadow Echo. 
        Hãy trả lời như thể bạn đang sống trong thế giới đó và không biết mình là NPC của game.
        
        Thông tin về nhân vật của bạn:
        - Tính cách: {getattr(npc, 'personality', 'thận trọng, đa nghi')}
        - Trí nhớ đã biết: {getattr(npc, 'memories', 'không có thông tin đặc biệt')}
        - Tâm trạng hiện tại: {npc_state.get('mood', 'neutral')}
        - Độ nghi ngờ: {npc_state.get('suspicion', 0.0):.1f}/1.0
        
        Sự kiện gần đây: {self.game.current_day_event if hasattr(self.game, 'current_day_event') else 'Không có gì đặc biệt'}
        
        Hãy trả lời một cách tự nhiên, không trả lời với giọng điệu của AI, và hãy tỏ ra bí ẩn và phù hợp với một nhân vật trong game trinh thám.
        """
        
        # Tạo tin nhắn cho API
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Thêm lịch sử hội thoại
        for entry in npc_history:
            role = "assistant" if entry["speaker"] == "npc" else "user"
            messages.append({"role": role, "content": entry["text"]})
        
        # Thêm message hiện tại
        messages.append({"role": "user", "content": player_message})
        
        try:
            # Call Grok API
            response = requests.post(
                self.grok_endpoint,
                headers={
                    "Authorization": f"Bearer {self.grok_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "grok-3-mini-beta",
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 150
                }
            )
            
            response.raise_for_status()
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                return self._generate_fallback_response(npc, npc_state)
                
        except Exception as e:
            print(f"Error calling Grok API: {e}")
            return self._generate_fallback_response(npc, npc_state)
    
    def _generate_fallback_response(self, npc, npc_state):
        """Tạo phản hồi dự phòng khi không thể sử dụng Grok API"""
        topic = npc_state.get("topic", "general")
        suspicion = npc_state.get("suspicion", 0.0)
        
        responses = {
            "general": [
                f"{npc.name} nhún vai. 'Tôi không có gì để nói với bạn.'",
                f"'Những chuyện thường ngày ấy mà...' {npc.name} thở dài.",
                f"'Thời tiết hôm nay thật kỳ lạ phải không?' {npc.name} nói."
            ],
            "identity": [
                f"'Tôi là {npc.name}, bạn quên rồi sao?'",
                f"{npc.name} cau mày. 'Bạn đang hỏi gì vậy? Tôi là {npc.name} đây.'"
            ],
            "murder": [
                f"Mắt {npc.name} mở to. 'Tôi không biết gì về vụ đó cả.'",
                f"'Đừng nói to!' {npc.name} nhìn quanh. 'Tôi nghĩ kẻ giết người vẫn còn ở đây...'"
            ],
            "clues": [
                f"'Tôi tìm thấy cái này sau nhà kho.' {npc.name} đưa cho bạn một mảnh giấy nhỏ.",
                f"'Manh mối ư? Cẩn thận nhé, không phải ai cũng muốn bạn tìm ra sự thật đâu.'"
            ]
        }
        
        response_pool = responses.get(topic, responses["general"])
        
        if suspicion > 0.7:
            return f"{npc.name} nhìn bạn đầy nghi ngờ. 'Tôi không tin bạn. Đừng có đến gần tôi nữa.'"
        
        return random.choice(response_pool)
    
    def _generate_npc_farewell(self, npc):
        """Tạo lời chào tạm biệt từ NPC"""
        farewells = [
            f"{npc.name} gật đầu. 'Hẹn gặp lại sau.'",
            f"'Tôi phải đi đây. Cẩn thận nhé,' {npc.name} nói khẽ.",
            f"{npc.name} lặng lẽ bỏ đi không nói thêm lời nào.",
        ]
        
        return random.choice(farewells)
    
    def _get_conversation_history(self, npc_id, limit=5):
        """Lấy lịch sử hội thoại với NPC"""
        if npc_id not in self.dialogue_history:
            return []
        
        history = self.dialogue_history[npc_id]
        return history[-limit:] if limit > 0 else history
    
    def get_npc_suspicion(self, npc_id):
        """Lấy mức độ nghi ngờ của NPC đối với người chơi"""
        if npc_id in self.conversation_state:
            return self.conversation_state[npc_id].get("suspicion", 0.0)
        return 0.0
    def _generate_npc_farewell(self, npc):
        """Tạo lời chào tạm biệt từ NPC"""
        farewells = [
            f"{npc.name} gật đầu. 'Hẹn gặp lại sau.'",
            f"'Tôi phải đi đây. Cẩn thận nhé,' {npc.name} nói khẽ.",
            f"{npc.name} lặng lẽ bỏ đi không nói thêm lời nào.",
        ]
        
        return random.choice(farewells)
    
    def _get_conversation_history(self, npc_id, limit=5):
        """Lấy lịch sử hội thoại với NPC"""
        if npc_id not in self.dialogue_history:
            return []
        
        history = self.dialogue_history[npc_id]
        return history[-limit:] if limit > 0 else history
    
    def get_npc_suspicion(self, npc_id):
        """Lấy mức độ nghi ngờ của NPC đối với người chơi"""
        if npc_id in self.conversation_state:
            return self.conversation_state[npc_id].get("suspicion", 0.0)
        return 0.0
