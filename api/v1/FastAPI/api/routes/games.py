from api.v1.FastAPI.api.utils.connection_manager import WebSocketConnectionManager
from fastapi import (
    APIRouter,
    Cookie,
    Depends,
    Request,
    FastAPI,
    Query,
    WebSocket,
    WebSocketException,
    WebSocketDisconnect,
    HTTPException,
    status
)
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from typing import Dict

import os
import redis
import uuid
import json
import asyncio
import multiprocessing

from api.v1.CybORG.CybORG.CyborgAAS.Runner.SimpleAgentRunner import SimpleAgentRunner

from sqlalchemy.orm import Session
from FastAPI import crud
from FastAPI.database import SessionLocal
from FastAPI.schemas import GameConfig

router = APIRouter()

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
redis_server = os.getenv('REDIS_SERVER', 'localhost')
# Redis connection # for persistent issue
r = redis.Redis(host=redis_server, port=6379, db=0)

# @To-Do: Better persistence support of an object needed in the future (run it as a subprocess, and store it in queue?)
# Mapping of game_id to SimpleAgentRunner instances
active_games = {}

websocket_connection_manager = WebSocketConnectionManager()

@router.websocket("/ws/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str):
    await websocket.accept()
    websocket_connection_manager.connect(websocket, game_id) 

    try:
        # Keep the connection open
        while True:
            # Optionally receive messages from client if needed
            data = await websocket.receive_text()
            # Handle client messages
            print(f"Received data from client: {data}")
            
            # Process the message
            #...

            # Send message back to client
            await websocket.send_text(f"Processed data: {data}\r\n")
            
    except WebSocketDisconnect:
        # Handle client disconnect
        websocket_connection_manager.disconnect(websocket, game_id)
        # Optionally terminate the game
        # end_game(game_id)

@router.get("/")
async def get_all_games(db: Session = Depends(get_db)):
    """
    Returns all games stored in the database
    """
    try:
        games_data = crud.get_all_game_meta(db)
        return {"games": games_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/start")
async def start_game(request: Request, config: GameConfig, db: Session = Depends(get_db)):
    """
    Create a new game 
    """
    # Generate game_id and initialize state
    game_id = str(uuid.uuid4())
    print(request.json())
    
    crud.start_new_game(game_id, config, db)
    
    runner = SimpleAgentRunner(config.steps, config.wrapper, config.red_agent, config.blue_agent)
    runner.configure()

    active_games[game_id] = runner

    game_state = {
        "game_id": game_id,
        "max_steps": config.steps,
        "red": config.red_agent,
        "blue": config.blue_agent,
        "step": 0,
        "state": {},
    }

    # Store in Redis
    r.set(game_id, json.dumps(game_state))  # Serialize game_state to store in Redis

    # Return game_id
    return {"game_id": game_id}


@router.post("/{game_id}")
async def run_next_step(game_id: str, db: Session = Depends(get_db)):

    runner = active_games.get(game_id) 
    if not runner:
        raise HTTPException(status_code=404, detail="Game not found")

    game_state_bytes = r.get(game_id)
    game_state = json.loads(game_state_bytes)
    
    state_snapshot = runner.run_next_step()

    if not state_snapshot:
        return {"Status": "End of Game"}
    
    game_state["step"] = runner.current_step
    game_state["state"] = state_snapshot

    # Store in Redis
    r.set(game_id, json.dumps(game_state))  # Serialize game_state to store in Redis

    # Store in DB
    crud.create_game_state(game_id, runner.current_step, state_snapshot, db)
    
    return state_snapshot


@router.get("/{game_id}/step/{step}")
async def get_step_state(game_id: str, step: int, db: Session = Depends(get_db)):
    game_state = crud.get_game_state(game_id, step, db)
    if game_state:
        return game_state.data
    else:
        raise HTTPException(status_code=404, detail="Game state not found")


@router.delete("/{game_id}")
async def end_game(game_id: str, db: Session = Depends(get_db)):
    deleted_count = crud.delete_game(game_id, db)
    r.delete(game_id)
    if game_id in active_games:
        del active_games[game_id]
        
    if deleted_count:
        return {"message": f"Game with ID {game_id} and {deleted_count} associated game states deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Game not found")