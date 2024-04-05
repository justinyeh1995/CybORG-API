from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Union
from pprint import pprint
import redis
import uuid
import json


from CybORG import CybORG, CYBORG_VERSION 
# @To-Do import CyborgAAS...
from CybORG.CyborgAAS.Runner.SimpleAgentRunner import SimpleAgentRunner

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow specific origins (or use ["*"] for all)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Redis connection # for persistent issue
r = redis.Redis(host='localhost', port=6379, db=0)

# @To-Do: Better persistence support of an object needed in the future (run it as a subprocess, and store it in queue?)
# Mapping of game_id to SimpleAgentRunner instances
active_games = {}

class GameConfig(BaseModel):
    red_agent: str = "B_lineAgent"
    blue_agent: str = "BlueReactRemoveAgent"
    wrapper: str = "simple"
    steps: int = 10


@app.post("/api/game")
async def start_game(request: Request, config: GameConfig):
    
    # Generate game_id and initialize state
    game_id = str(uuid.uuid4())
    
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

@app.post("/api/game/{game_id}")
async def run_next_step(game_id: str):

    runner = active_games.get(game_id) 
    if not runner:
        raise HTTPException(status_code=404, detail="Game not found")

    game_state_bytes = r.get(game_id)
    game_state = json.loads(game_state_bytes)
    
    state_snapshot = runner.run_next_step()
    
    game_state["step"] = runner.current_step
    game_state["state"] = state_snapshot

    # Store in Redis
    r.set(game_id, json.dumps(game_state))  # Serialize game_state to store in Redis

    return state_snapshot

@app.post("/api/game/all/{game_id}")
async def run_all_steps(game_id: str):

    runner = active_games.get(game_id)
    if not runner:
        raise HTTPException(status_code=404, detail="Game not found")

    game_states = runner.run_all_step()
    
    game_state = {
        "game_id": game_id,
        "history": runner.game_state_manager.game_states,
    }

    # Store in Redis
    r.set(game_id, json.dumps(game_state))  # Serialize game_state to store in Redis

    return state_snapshot

@app.get("/api/game/{game_id}")
async def get_latest_state(game_id: str):

    runner = active_games.get(game_id)
    if not runner:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game_state_raw = r.get(game_id)
    game_state.loads(game_state_raw)
    
    return game_state.state

@app.delete("/api/game/{game_id}")
async def end_game(game_id: str):
    if game_id in active_games:
        # Include any teardown logic for the runner here
        del active_games[game_id]
        # Clean up any persistent state in Redis or other databases
        r.delete(game_id)
        return {"message": "Game ended successfully"}
    else:
        raise HTTPException(status_code=404, detail="Game not found")
        
@app.get("/")
def read_root():
    print("Hello FastAPI")
    return {"Hello": "World"}




