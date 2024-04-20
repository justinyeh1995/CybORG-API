from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse
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

    if not state_snapshot:
        return {"Status": "End of Game"}
    
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

    # @To-Do: decide how to store states for review 
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
        
@app.get("/", response_class=HTMLResponse)
def read_root():
    print("Hello FastAPI")
    return """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Justin's Portfolio</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 0; padding: 0; box-sizing: border-box; }
                    .container { max-width: 800px; margin: auto; padding: 20px; }
                    header { text-align: center; padding: 50px 0; }
                    header h1 { margin: 0; }
                    section { margin-bottom: 40px; }
                    .projects img { max-width: 100%; height: auto; }
                    footer { background-color: #f3f3f3; text-align: center; padding: 20px 0; }
                </style>
            </head>
            <body>
                <header>
                    <h1>Justin Yeh🌳</h1>
                    <p>Welcome to my professional portfolio.</p>
                </header>
                
                <div class="container">
                    <section>
                        <h2>About Me</h2>
                        <p>Hello, I'm Justin Yeh(Madarin Name: 葉致廷 Yè Zhìtíng), a Master’s student in Computer Science at Vanderbilt University with a fervent interest in leveraging technology to solve complex problems, particularly within the realms of cybersecurity and data-driven applications. Check out some projects that I've done. Cheers, 🥂</p>
                    </section>
                    
                    <section>
                        <h2>Projects</h2>
                        <div class="projects">
                            <!-- Project 1 -->
                            <div class="project">
                                <h3>SolitaireJS.com</h3>
                                <img src="path_to_image" alt="Project Image">
                                <p>Description of your project. What was your role, what technologies did you use, and what was the outcome?</p>
                                <a href="https://solitairejs.com/" target="_blank">View Project</a>
                            </div>
                            
                            <!-- Project 2 -->
                            <div class="project">
                                <h3>iOS AR Visualization App</h3>
                                <img src="https://raw.githubusercontent.com/cage-challenge/cage-challenge-2/main/images/figure1.png" alt="Project Image">
                                <p>This App visulize the underlying network state of <a href="https://github.com/cage-challenge/cage-challenge-2" target="_blank">CybORG 2</a> in AR using SwiftUI, ARKit, RealityKit.</p>
                                <a href="https://github.com/justinyeh1995/CybORG-ARViz/" target="_blank">View Project</a>
                            </div>
                        </div>
                    </section>
                    
                    <section>
                        <h2>Contact</h2>
                        <p>Let people know how to get in touch with you. You can list your email address, LinkedIn profile, or other contact information here.</p>
                    </section>
                </div>
                
                <footer>
                    <p>&copy; 2024 Justin Yeh. All rights reserved.</p>
                </footer>
            </body>
            </html>
            """