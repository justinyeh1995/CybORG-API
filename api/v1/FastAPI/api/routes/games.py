# main.py
import signal
import subprocess
import psutil
from fastapi import (
    APIRouter,
    Depends,
    Request,
    Query,  # used for query parameters
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
import redis.asyncio as redis
import uuid
import json
import asyncio
from sqlalchemy.orm import Session
from api.v1.FastAPI.api.utils.connection_manager import WebSocketConnectionManager
from api.v1.FastAPI.crud import crud_game as crud
from api.v1.FastAPI.api.deps import SessionDep, CurrentUserDep
from api.v1.FastAPI.schemas import GameConfig, GameConfigSummarySchema, GameConfigurationSchema, GameSummarySchema
import logging
import inspect
import api.v1.CybORG.CybORG.CyborgAAS.Runner.SimpleAgentRunner

# Retrieve the file path using inspect
agent_runner_file_path = inspect.getfile(api.v1.CybORG.CybORG.CyborgAAS.Runner.SimpleAgentRunner)
agent_runner_abs_path = os.path.abspath(agent_runner_file_path)

router = APIRouter()

# Initialize Redis client
redis_server = os.getenv('REDIS_SERVER', 'localhost')
redis_client = redis.Redis(host=redis_server, port=6379, db=0, decode_responses=True)

# Initialize WebSocket Connection Manager
websocket_connection_manager = WebSocketConnectionManager()

# Global dictionaries to keep track of subprocesses and tasks
active_runner_procs = {}
runner_proc_tasks = {}

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

# TODO: fix the response model for all the endpoints

@router.get("/", response_model=None)
async def get_all_games(db: SessionDep):
    """
    Returns all games stored in the database
    """
    try:
        games_data = crud.get_all_game_meta(db)
        return {"games": games_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/start", 
             response_model=None, 
             )
async def start_game(
    config: GameConfig, 
    db: SessionDep, 
    current_user: CurrentUserDep,
    ):
    """
    Create a new game
    """
    try:
        user_id = current_user.user_id
        print("Current user is", user_id)
        
        # Generate game_id and initialize state
        game_id = str(uuid.uuid4())

        print(f"AgentRunner.py Path: {agent_runner_abs_path}")

        # Start the subprocess using asyncio
        runner_proc = await asyncio.create_subprocess_exec(
            "python3",
            "-u",  # Unbuffered stdout
            agent_runner_abs_path,  # Path to SimpleAgentRunner.py
            "--game_id", game_id,
            "--num_steps", str(config.steps),
            "--wrapper_type", config.wrapper,
            "--red_agent_type", config.red_agent,
            "--blue_agent_type", config.blue_agent,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            preexec_fn=os.setsid  # Start in a new session
        )

        if not runner_proc:
            raise HTTPException(status_code=500, detail="Failed to start runner process")

        print(runner_proc.pid, "Running")

        # Store active game info in Redis
        game_data = {
            "runner_proc_pid": runner_proc.pid
        }
        await redis_client.hset(f"game:{game_id}", mapping=game_data)

        # Function to read stream and publish to Redis channel
        async def read_stream_and_publish(stream, channel_name):
            try:
                while True:
                    line = await stream.readline()
                    if not line:
                        break
                    message = line.decode().rstrip()
                    await redis_client.publish(channel_name, message)
            except Exception as e:
                print(f"Error reading stream: {e}")

        # Start tasks to read from stdout and stderr
        stdout_channel = f"game:{game_id}:stdout"
        stderr_channel = f"game:{game_id}:stderr"

        task_stdout = asyncio.create_task(read_stream_and_publish(runner_proc.stdout, stdout_channel))
        task_stderr = asyncio.create_task(read_stream_and_publish(runner_proc.stderr, stderr_channel))

        # Keep track of the subprocess and tasks
        active_runner_procs[game_id] = runner_proc
        runner_proc_tasks[game_id] = [task_stdout, task_stderr]

        # store it in the database
        crud.start_new_game(user_id, game_id, config, db)
        print(f"Game started with ID: {game_id}")
        
        return {"game_id": game_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{game_id}", response_model=GameConfigSummarySchema)
async def get_game_status(game_id: str, db: SessionDep):
    """
    Returns the game status for the given game_id
    it returns gameConfig model
    """
    game_config_summary = crud.get_game_config_summary(game_id, db)
    if not game_config_summary:
        raise HTTPException(status_code=404, detail="Game config not found")
    
    configuration, summary = game_config_summary
    return GameConfigSummarySchema(
        configuration=GameConfigurationSchema.from_orm(configuration),
        summary=GameSummarySchema.from_orm(summary)
    )
    

@router.post("/{game_id}", response_model=None)
async def run_next_step(game_id: str, db: SessionDep):
    """
    Run the next step in the game and return the game state.
    No body for this request
    """
    # Retrieve game info from Redis
    game_info = await redis_client.hgetall(f"game:{game_id}")
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
    await redis_client.publish(f'game_{game_id}_main', "Next Step")

    # Using Redis Lists
    state_list_key = f"game:{game_id}:states"
    state_snapshot = await redis_client.brpop(state_list_key, timeout=300)

    if not state_snapshot:
        return {"Status": "End of Game or Timeout"}

    _, state_data = state_snapshot
    data = json.loads(state_data)
    state_snapshot = data.get("state_snapshot")
    current_step = data.get("current_step")
    completed = data.get("completed")
    # Store in DB
    crud.create_game_state(game_id, current_step, state_snapshot, db)
    
    crud.update_step_game_summary(game_id, current_step, db)
    
    if completed:
        # Mark as completed in game summary
        crud.end_game(game_id, db)
    
    return {
        "StateSnapshot": state_snapshot,
        "Completed": completed
    }

@router.delete("/{game_id}", response_model=None)
async def end_game(game_id: str, db: SessionDep):
    """
    Delete a game and associated game states from the database and Redis cache
    """
    # Retrieve game info from Redis
    game_info = await redis_client.hgetall(f"game:{game_id}")
    if game_info:

      runner_proc_pid = int(game_info.get('runner_proc_pid', 0))

      if runner_proc_pid:
          try:
              # Terminate the process group
              os.killpg(os.getpgid(runner_proc_pid), signal.SIGTERM)
              # Wait for the child process to prevent it from becoming a zombie
              os.waitpid(runner_proc_pid, 0)
          except ProcessLookupError:
              # Process or process group does not exist
              pass
          except Exception as e:
              raise HTTPException(status_code=500, detail=f"Error terminating runner process: {str(e)}")

      # Cancel associated tasks
      tasks = runner_proc_tasks.pop(game_id, [])
      for task in tasks:
          task.cancel()

      # Remove from active_runner_procs
      active_runner_procs.pop(game_id, None)

      # Remove from Redis
      await redis_client.delete(f"game:{game_id}")

    # Delete game from database
    deleted_count = crud.delete_game(game_id, db)
    if not deleted_count:
        raise HTTPException(status_code=404, detail="Game not found")
    
    return {"message": f"Game with ID {game_id} and {deleted_count} associated game states deleted successfully"}

@router.get("/{game_id}/step/{step}", response_model=None)
async def get_step_state(game_id: str, step: int, db: SessionDep):
    """
    Returns the state of the game at the given step
    """
    game_state = crud.get_game_state(game_id, step, db)
    if game_state:
        return game_state.data
    else:
        raise HTTPException(status_code=404, detail="Game state not found")

@router.websocket("/ws/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str):
    """
    Websocket endpoint to stream stdout and stderr of the game
    """
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

@router.get("/{game_id}/status/", response_model=None)
async def get_game_status_websocket(game_id: str):
    """
    Returns the status of the game in a WebSocket-friendly format
    """
    game_info = await redis_client.hgetall(f"game:{game_id}")
    if not game_info:
        raise HTTPException(status_code=404, detail="Game not found or expired")

    runner_proc_pid = int(game_info.get('runner_proc_pid', 0))

    if not runner_proc_pid:
        return {"Status": "Not running"}

    # Check if the subprocess is still running
    if not psutil.pid_exists(runner_proc_pid):
        return {"Status": "Not running"}

    return {"Status": "Running"}

# @router.get("/{game_id}/stats/")
# async def get_game_stats(game_id: str, db: Session = SessionDep):
#     """
#     Returns the statistics of the game
#     """
#     game_stats = crud.get_game_stats(game_id, db)
#     if game_stats:
#         return game_stats.data
#     else:
#         raise HTTPException(status_code=404, detail="Game statistics not found")

@router.on_event("startup")
async def startup_event():
    """
    Initialize active game runner processes and tasks
     - Fetch all game IDs from Redis
     - Check if their runner processes are still running
     - If so, reconstruct the subprocess and (tasks to read stdout and stderr is not supported)
     """
    await initialize_active_games()

async def initialize_active_games():
    keys = await redis_client.keys('game:*')
    for key in keys:
        # Check if the key is of type 'hash'
        key_type = await redis_client.type(key)
        if key_type == 'hash':
            game_info = await redis_client.hgetall(key)
            game_id = key.split(":")[1]
            runner_proc_pid = int(game_info.get('runner_proc_pid', 0))
            # Reconstruct active_runner_procs
            if psutil.pid_exists(runner_proc_pid):
                # Note: You may need to adjust how you reconstruct the subprocess
                runner_proc = psutil.Process(runner_proc_pid)
                active_runner_procs[game_id] = runner_proc

@router.on_event("shutdown")
async def shutdown_event():
    # Retrieve all active games
    keys = await redis_client.keys('game:*')
    for key in keys:
        # Check if the key is of type 'hash'
        key_type = await redis_client.type(key)
        if key_type == 'hash':
            game_info = await redis_client.hgetall(key)
            game_id = key.split(":")[1]
            runner_proc_pid = int(game_info.get('runner_proc_pid', 0))
            if runner_proc_pid:
                try:
                    os.kill(runner_proc_pid, signal.SIGTERM)
                    os.waitpid(runner_proc_pid, 0)
                except OSError:
                    pass
            # Optionally, delete the game key
            await redis_client.delete(game_id)