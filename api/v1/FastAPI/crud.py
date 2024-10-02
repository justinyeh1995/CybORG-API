from http.client import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from api.v1.FastAPI import models, schemas
from api.v1.FastAPI.schemas import GameConfig

def start_new_game(game_id: str, game_config: GameConfig, db: Session):
    red_agent, blue_agent, wrapper, steps = game_config.red_agent, game_config.blue_agent, game_config.wrapper, game_config.steps
    new_game_config = models.GameConfiguration(game_id=game_id, red_agent=red_agent, blue_agent=blue_agent, wrapper=wrapper, steps=steps)
    db.add(new_game_config)
    db.commit()
    db.refresh(new_game_config)
    return new_game_config

def get_all_games(db: Session):
    return db.query(models.GameState).all()

def get_all_game_meta(db: Session):

    # Subquery to get the latest step for each game
    latest_step_subquery = (
        db.query(
            models.GameState.game_id,
            func.max(models.GameState.step).label('max_step')
        )
        .group_by(models.GameState.game_id)
        .subquery()
    )

    # Main query
    query = (
        db.query(models.GameConfiguration, models.GameState)
        .join(models.GameState,models.GameConfiguration.game_id == models.GameState.game_id)
        .join(
            latest_step_subquery,
            (models.GameState.game_id == latest_step_subquery.c.game_id) &
            (models.GameState.step == latest_step_subquery.c.max_step)
        )
    )

    results = query.all()
    
    # Process the results
    game_data = []
    for config, state in results:
        game_data.append({
            "game_id": config.game_id,
            "step": state.step,
            "config": {
                "red_agent": config.red_agent,
                "blue_agent": config.blue_agent,
                "wrapper": config.wrapper,
                "steps": config.steps
            },
            "completed": state.step >= config.steps
            # "state_data": state.data
        })
    
    return game_data

def create_game_state(game_id: str, step: int, data: dict, db: Session):
    new_game_state = models.GameState(game_id=game_id, step=step, data=data)
    db.add(new_game_state)
    db.commit()
    db.refresh(new_game_state)
    return new_game_state
    
def get_game_state(game_id: str, step: int, db: Session):
    return db.query(models.GameState).filter(models.GameState.game_id == game_id, models.GameState.step == step).first()

def delete_game(game_id: str, db: Session):
    # Delete all GameState records associated with the game_id
    deleted_count = db.query(models.GameState).filter(models.GameState.game_id == game_id).delete()
    db.commit()
    return deleted_count