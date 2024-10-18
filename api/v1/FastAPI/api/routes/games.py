# main.py
import subprocess
import psutil
from fastapi import (
    APIRouter,
    Depends,
    Request,
    Query, # used for query parameters
    WebSocket,
    WebSocketException,
    WebSocketDisconnect,
    HTTPException,
)

from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict, AsyncGenerator
import sys
import os
# import redis.asyncio as redis
import redis
import uuid
import json
import asyncio

from sqlalchemy.orm import Session

from api.v1.FastAPI.api.utils.connection_manager import WebSocketConnectionManager


from FastAPI import crud
from FastAPI.database import SessionLocal
from FastAPI.schemas import GameConfig

import logging
import inspect
import api.v1.CybORG.CybORG.CyborgAAS.Runner.AgentRunner
import api.v1.CybORG.CybORG.CyborgAAS.Runner.SimpleAgentRunner

# Retrieve the file path using inspect
agent_runner_file_path = inspect.getfile(api.v1.CybORG.CybORG.CyborgAAS.Runner.SimpleAgentRunner)
agent_runner_abs_path = os.path.abspath(agent_runner_file_path)


router = APIRouter()

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize Redis client
redis_server = os.getenv('REDIS_SERVER', 'localhost')
redis_client = redis.Redis(host=redis_server, port=6379, db=0, decode_responses=True) 

# Initialize WebSocket Connection Manager
websocket_connection_manager = WebSocketConnectionManager()

async def subscribe_to_channel(channel: str) -> AsyncGenerator[str, None]:
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(channel)
    try:
        async for message in pubsub.listen():
            if message['type'] == 'message':
                yield message['data']
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.close()

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
async def start_game(config: GameConfig, db: Session = Depends(get_db)):
    """
    Create a new game 
    """
    try: 
        # Generate game_id and initialize state
        game_id = str(uuid.uuid4())
        
        crud.start_new_game(game_id, config, db)
       
        print(f"AgentRunner.py Path: {agent_runner_abs_path}")
         
        # Start the subprocess
        runner_proc = subprocess.Popen(
            [
                "python3",
                "-u",  # Unbuffered stdout
                agent_runner_abs_path,  # Path to AgentRunner.py
                "--game_id", game_id, 
                "--num_steps", str(config.steps), 
                "--wrapper_type", config.wrapper,
                "--red_agent_type", config.red_agent, 
                "--blue_agent_type", config.blue_agent,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        if not runner_proc:
            raise HTTPException(status_code=500, detail="Failed to start runner process")
            
        print(runner_proc.pid, "Running")
        
        # Store active game info in Redis
        game_data = {
            "runner_proc_pid": runner_proc.pid
            # Add more fields if needed
        }
        
        redis_client.hset(f"game:{game_id}", mapping=game_data)
        # Optionally, set an expiration time
        # await redis_client.expire(f"game:{game_id}", 3600)  # Expires in 1 hour

        return {"game_id": game_id}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# @router.post("/start")
# async def start_game(config: GameConfig, db: Session = Depends(get_db)):
#     """
#     Create a new game 
#     """
#     try: 
#         # Generate game_id and initialize state
#         game_id = str(uuid.uuid4())
        
#         crud.start_new_game(game_id, config, db)
       
#         logging.info(f"AgentRunner.py Path: {agent_runner_abs_path}")
         
#         # Start the subprocess
#         runner_proc = await asyncio.create_subprocess_exec(
#             "python3",
#             "-u",  # Unbuffered stdout
#             # agent_runner_abs_path,  # Path to AgentRunner.py
#             "/cage/api/v1/CybORG/CybORG/CyborgAAS/Runner/SimpleAgentRunner.py",
#             "--game_id", game_id, 
#             "--num_steps", str(config.steps), 
#             "--wrapper_type", config.wrapper,
#             "--red_agent_type", config.red_agent, 
#             "--blue_agent_type", config.blue_agent,
#             stdout=asyncio.subprocess.PIPE,
#             stderr=asyncio.subprocess.PIPE
#         )
        
#         if not runner_proc:
#             raise HTTPException(status_code=500, detail="Failed to start runner process")
            
#         logging.info(runner_proc.pid, "Running")
#         # Store active game info in Redis
#         game_data = {
#             "runner_proc_pid": runner_proc.pid
#             # Add more fields if needed
#         }
        
#         await redis_client.hset(f"game:{game_id}", mapping=game_data)
#         # Optionally, set an expiration time
#         # await redis_client.expire(f"game:{game_id}", 3600)  # Expires in 1 hour

#         return {"game_id": game_id}
    
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

@router.get("/{game_id}")
async def get_game_status(game_id: str, db: Session = Depends(get_db)):
    game_config = crud.get_game_config(game_id, db)
    if game_config:
        return game_config
    else:
        raise HTTPException(status_code=404, detail="Game config not found")

@router.post("/{game_id}")
async def run_next_step(game_id: str, db: Session = Depends(get_db)):
    """
    Run the next step in the game and return the game state.
    No body for this request
    """
    # Retrieve game info from Redis
    game_info = redis_client.hgetall(f"game:{game_id}")
    if not game_info:
        raise HTTPException(status_code=404, detail="Game not found or expired")
    
    runner_proc_pid = int(game_info.get('runner_proc_pid', 0))
    print(runner_proc_pid)
    
    if not runner_proc_pid:
        raise HTTPException(status_code=404, detail="Runner process not found")
    
    # Check if the subprocess is still running
    if not psutil.pid_exists(runner_proc_pid):
        raise HTTPException(status_code=404, detail="Runner process not running")
    
    # Publish a message to trigger the next step
    redis_client.publish(f'game_{game_id}_main', "Next Step")
    
    # Using Redis Lists
    state_list_key = f"game:{game_id}:states"
    state_snapshot = redis_client.brpop(state_list_key, timeout=300)
    
    if not state_snapshot:
        return {"Status": "End of Game or Timeout"}
    
    _, state_data = state_snapshot
    data = json.loads(state_data)
    state_snapshot = data.get("state_snapshot")
    current_step = data.get("current_step")
    
    if not state_snapshot:
        return {"Status": "End of Game"}
    
    # Store in DB
    crud.create_game_state(game_id, current_step, state_snapshot, db)
    
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
    if not deleted_count:
        raise HTTPException(status_code=404, detail="Game not found")
    # Remove from Redis
    redis_client.delete(f"game:{game_id}")
        
    return {"message": f"Game with ID {game_id} and {deleted_count} associated game states deleted successfully"}

@router.websocket("/ws/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str):
    await websocket.accept()
    websocket_connection_manager.connect(websocket, game_id) 
    
    stdout_channel = f"game:{game_id}:stdout"
    stderr_channel = f"game:{game_id}:stderr"

    async def listen_channel(channel: str, prefix: str):
        async for message in subscribe_to_channel(channel):
            await websocket.send_text(f"{prefix}: {message}")

    try:
        # Create tasks for both stdout and stderr
        task_stdout = asyncio.create_task(listen_channel(stdout_channel, "STDOUT"))
        task_stderr = asyncio.create_task(listen_channel(stderr_channel, "STDERR"))

        # Wait until both tasks are completed
        await asyncio.gather(task_stdout, task_stderr)
    except WebSocketDisconnect:
        websocket_connection_manager.disconnect(websocket, game_id)
    except Exception as e:
        await websocket.send_text(f"Error: {str(e)}")
        await websocket.close()

# @router.websocket("/ws/simple/{game_id}")
# async def websocket_endpoint(websocket: WebSocket, game_id: str):
#     await websocket.accept()
#     websocket_connection_manager.connect(websocket, game_id) 
    
#     try:
#         # Retrieve runner process
#         runner_proc = active_runner_procs.get(game_id)
#         if not runner_proc:
#             await websocket.send_text("Runner process not found.")
#             await websocket.close()
#             return

#         # Function to stream output
#         async def stream_output(pipe, prefix):
#             try:
#                 while True:
#                     line = await pipe.readline()
#                     if line:
#                         decoded_line = line.decode('utf-8').rstrip()
#                         message = f"{prefix}: {decoded_line}"
#                         await websocket_connection_manager.broadcast(game_id, message)
#                     else:
#                         break
#             except Exception as e:
#                 await websocket.send_text(f"Error streaming {prefix}: {str(e)}")

#         # Create tasks for stdout and stderr
#         task_stdout = asyncio.create_task(stream_output(runner_proc.stdout, "STDOUT"))
#         task_stderr = asyncio.create_task(stream_output(runner_proc.stderr, "STDERR"))

#         # Wait for both streams to complete
#         await asyncio.gather(task_stdout, task_stderr)
    
#     except WebSocketDisconnect:
#         websocket_connection_manager.disconnect(websocket, game_id)
#     except Exception as e:
#         await websocket.send_text(f"Error: {str(e)}")
#         await websocket.close()
