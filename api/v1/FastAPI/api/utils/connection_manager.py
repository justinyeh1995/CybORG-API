from typing import Dict
from fastapi import WebSocket 

class WebSocketConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, game_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[game_id] = websocket

    def disconnect(self, game_id: str, websocket: WebSocket):
        if game_id in self.active_connections:
            del self.active_connections[game_id]

    async def send_personal_message(self, message: str, simulation_id: str):
        websockets = self.active_connections.get(simulation_id, [])
        for connection in websockets:
            await connection.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)
            