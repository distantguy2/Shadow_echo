import asyncio
import websockets
import json
from queue import Queue
from typing import Callable, Dict

class GameClient:
    def __init__(self, server_url: str = "ws://localhost:8765"):
        self.server_url = server_url
        self.websocket = None
        self.player_id = None
        self.lobby_id = None
        self.connected = False
        self.callbacks: Dict[str, Callable] = {}
        self.message_queue = Queue()

    async def connect(self, player_name: str) -> bool:
        """
        Kết nối đến server và gửi yêu cầu 'join' với tên của người chơi.
        """
        try:
            self.websocket = await websockets.connect(self.server_url)
            
            # Gửi join request với tên người chơi
            await self.websocket.send(json.dumps({
                "type": "join",
                "name": player_name
            }))
            
            # Bắt đầu xử lý nhận message từ server
            asyncio.create_task(self.receive_messages())
            self.connected = True
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    async def receive_messages(self):
        """
        Lắng nghe và xử lý các message nhận được từ server.
        Nếu có callback đăng ký với message type, gọi callback đó.
        """
        try:
            async for message in self.websocket:
                data = json.loads(message)
                
                # Nếu nhận được message 'connected', lưu lại player_id
                if data["type"] == "connected":
                    self.player_id = data.get("player_id")
                
                # Gọi callback nếu đã đăng ký
                callback = self.callbacks.get(data["type"])
                if callback:
                    callback(data)
                else:
                    self.message_queue.put(data)
        except websockets.exceptions.ConnectionClosed:
            self.connected = False
            print("Disconnected from server")

    async def create_lobby(self, lobby_name: str):
        """
        Gửi yêu cầu tạo lobby với tên đã chọn.
        """
        if self.connected:
            await self.websocket.send(json.dumps({
                "type": "create_lobby",
                "name": lobby_name
            }))

    async def join_lobby(self, lobby_id: str):
        """
        Gửi yêu cầu tham gia lobby theo lobby_id.
        """
        if self.connected:
            await self.websocket.send(json.dumps({
                "type": "join_lobby",
                "lobby_id": lobby_id
            }))
            self.lobby_id = lobby_id

    async def set_ready(self):
        """
        Gửi yêu cầu báo sẵn sàng.
        """
        if self.connected:
            await self.websocket.send(json.dumps({
                "type": "ready"
            }))

    async def send_command(self, command: str):
        """
        Gửi các lệnh gameplay lên server (ví dụ: build, scan, use, accuse,...)
        """
        if self.connected and self.lobby_id:
            await self.websocket.send(json.dumps({
                "type": "game_action",
                "action": "command",
                "command": command
            }))

    def register_callback(self, message_type: str, callback: Callable):
        """
        Đăng ký callback xử lý cho các message theo loại.
        """
        self.callbacks[message_type] = callback
