from api.v1.CybORG.CybORG.CyborgAAS.Runner.SimpleAgentRunner import SimpleAgentRunner
from fastapi import WebSocket, WebSocketDisconnect

class WebSocketConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, game_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[game_id] = websocket

    def disconnect(self, game_id: str, websocket: WebSocket):
        del self.active_connections[game_id]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)
            
class ActiveGameManager:
    def __init__(self):
        self.active_games: dict[str, SimpleAgentRunner] = {}