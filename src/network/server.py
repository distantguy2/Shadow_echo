import socket
import threading
import json
import asyncio
import websockets
from dataclasses import dataclass
from typing import Dict, List, Set
from queue import Queue

@dataclass
class NetworkPlayer:
    id: str
    name: str
    websocket: websockets.WebSocketServerProtocol
    lobby_id: str = None
    ready: bool = False

class GameServer:
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.lobbies: Dict[str, 'Lobby'] = {}
        self.players: Dict[str, NetworkPlayer] = {}
        self.game_states: Dict[str, dict] = {}

    async def start(self):
        server = await websockets.serve(self.handle_client, self.host, self.port)
        print(f"Shadow Echo Server running on {self.host}:{self.port}")
        await server.wait_closed()

    async def handle_client(self, websocket, path):
        player_id = str(id(websocket))
        try:
            data = await websocket.recv()
            initial_data = json.loads(data)

            if initial_data["type"] == "join":
                player = NetworkPlayer(
                    id=player_id,
                    name=initial_data["name"],
                    websocket=websocket
                )
                self.players[player_id] = player

                await websocket.send(json.dumps({
                    "type": "connected",
                    "player_id": player_id,
                    "available_lobbies": list(self.lobbies.keys())
                }))

                async for message in websocket:
                    await self.handle_message(player_id, json.loads(message))

        except websockets.exceptions.ConnectionClosed:
            print(f"Player {player_id} disconnected")
        finally:
            if player_id in self.players:
                await self.remove_player(player_id)

    async def handle_message(self, player_id: str, data: dict):
        player = self.players.get(player_id)
        if not player:
            return

        msg_type = data.get("type")
        if msg_type == "create_lobby":
            lobby_id = self.create_lobby(data.get("name", "New Lobby"))
            await self.join_lobby(player_id, lobby_id)

        elif msg_type == "join_lobby":
            lobby_id = data.get("lobby_id")
            if lobby_id in self.lobbies:
                await self.join_lobby(player_id, lobby_id)
            else:
                await player.websocket.send(json.dumps({
                    "type": "error",
                    "message": "Lobby not found"
                }))

        elif msg_type == "ready":
            if player.lobby_id:
                player.ready = True
                await self.check_lobby_start(player.lobby_id)

        elif msg_type == "game_action":
            if player.lobby_id:
                await self.handle_game_action(player.lobby_id, player_id, data)

    def create_lobby(self, name: str) -> str:
        lobby_id = f"lobby_{len(self.lobbies)}"
        self.lobbies[lobby_id] = Lobby(lobby_id, name)
        return lobby_id

    async def join_lobby(self, player_id: str, lobby_id: str):
        player = self.players[player_id]
        lobby = self.lobbies[lobby_id]

        if len(lobby.players) < 5:
            player.lobby_id = lobby_id
            lobby.players.add(player_id)
            await self.broadcast_to_lobby(lobby_id, {
                "type": "player_joined",
                "player_id": player_id,
                "player_name": player.name,
                "current_players": len(lobby.players)
            })
        else:
            await player.websocket.send(json.dumps({
                "type": "error",
                "message": "Lobby is full"
            }))

    async def check_lobby_start(self, lobby_id: str):
        lobby = self.lobbies[lobby_id]
        ready_count = sum(1 for pid in lobby.players if self.players[pid].ready)
        if ready_count == len(lobby.players) and len(lobby.players) >= 3:
            await self.start_game(lobby_id)

    async def start_game(self, lobby_id: str):
        lobby = self.lobbies[lobby_id]
        lobby.state = "in_game"
        game_state = {
            "phase": "preparation",
            "day_count": 0,
            "time_left": 60,
            "players": {},
            "monsters": [],
            "npcs": self.create_npcs()
        }
        roles = ["♕", "♛", "☢"]
        import random
        random.shuffle(roles)
        for i, pid in enumerate(lobby.players):
            role = roles[i % len(roles)]
            game_state["players"][pid] = {
                "hp": 100,
                "role": role,
                "cards": [],
                "position": [100 + i * 50, 400]
            }
        self.game_states[lobby_id] = game_state
        await self.broadcast_to_lobby(lobby_id, {
            "type": "game_started",
            "game_state": game_state
        })

    def create_npcs(self):
        return []  # Placeholder for NPC list

    async def handle_game_action(self, lobby_id: str, player_id: str, data: dict):
        game_state = self.game_states[lobby_id]
        command = data.get("command")
        result = f"Player {player_id} executed {command}"
        game_state.setdefault("results", []).append(result)
        await self.broadcast_to_lobby(lobby_id, {
            "type": "game_update",
            "game_state": game_state,
            "action_result": result
        })

    async def broadcast_to_lobby(self, lobby_id: str, message: dict):
        for pid in self.lobbies[lobby_id].players:
            try:
                await self.players[pid].websocket.send(json.dumps(message))
            except:
                pass

    async def remove_player(self, player_id: str):
        player = self.players.get(player_id)
        if player and player.lobby_id:
            self.lobbies[player.lobby_id].players.discard(player_id)
            await self.broadcast_to_lobby(player.lobby_id, {
                "type": "player_left",
                "player_id": player_id
            })
        self.players.pop(player_id, None)

class Lobby:
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name
        self.players: Set[str] = set()
        self.state = "waiting"
        self.max_players = 5

if __name__ == "__main__":
    server = GameServer()
    asyncio.run(server.start())
