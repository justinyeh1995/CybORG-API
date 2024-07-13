from pydantic import BaseModel
from typing import Dict, Any

class GameStateSchema(BaseModel):
    game_id: str
    step: int
    state: Dict[str, Any]

    class Config:
        orm_mode = True