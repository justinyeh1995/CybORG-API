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
    # this is not working properly cause game.py active_games objects would not be updated
    # how can we solve this problem?
    create_game_state(game_id, 0, {}, db)
    # create new game summary
    create_game_summary(game_id, db)
    return new_game_config

def create_game_state(game_id: str, step: int, data: dict, db: Session):
    new_game_state = models.GameState(game_id=game_id, step=step, data=data)
    db.add(new_game_state)
    db.commit()
    db.refresh(new_game_state)
    return new_game_state

def create_game_summary(game_id, db):
    new_game_status = models.GameSummary(game_id=game_id, steps=0, completed=False)
    db.add(new_game_status)
    db.commit()
    db.refresh(new_game_status)
    return new_game_status

def update_game_summary(game_id, steps, completed, final_reward, db):
    game_status = db.query(models.GameSummary).filter(models.GameSummary.game_id == game_id).first()
    if game_status:
        game_status.steps = steps
        game_status.completed = completed
        game_status.final_reward = final_reward
        db.commit()
        db.refresh(game_status)
    else:
        raise HTTPException(status_code=404, detail="Game status not found")

def get_all_games(db: Session):
    return db.query(models.GameState).all()

def get_all_game_meta_with_auth(db: Session, user_id: str):
    # Subquery to get the latest step for each game
    latest_step_subquery = (
        db.query(
            models.GameState.game_id,
            func.max(models.GameState.step).label('max_step')
        )
        .join(models.GameConfiguration, models.GameState.game_id == models.GameConfiguration.game_id)
        .filter(models.GameConfiguration.user_id == user_id)  # Filter by user_id
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
        .filter(models.GameConfiguration.user_id == user_id)  # Filter by user_id
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
    
def get_game_state(game_id: str, step: int, db: Session):
    return db.query(models.GameState).filter(models.GameState.game_id == game_id, models.GameState.step == step).first()

def get_game_config(game_id: str, db: Session):
    return db.query(models.GameConfiguration).filter(models.GameConfiguration.game_id == game_id).first()

def get_game_summary(game_id: str, db: Session):
    return db.query(models.GameSummary).filter(models.GameSummary.game_id == game_id).first()

def get_game_config_summary(game_id: str, db: Session):
    return db.query(models.GameConfiguration, models.GameSummary)\
        .join(models.GameSummary, models.GameConfiguration.game_id == models.GameSummary.game_id)\
        .filter(models.GameConfiguration.game_id == game_id)\
        .first()

def delete_game(game_id: str, db: Session):
    # Delete all GameState records associated with the game_id
    deleted_count = db.query(models.GameState).filter(models.GameState.game_id == game_id).delete()
    delete_game_config_count = db.query(models.GameConfiguration).filter(models.GameConfiguration.game_id == game_id).delete()
    # Delete the game_id from GameSummary records if it exists
    db.query(models.GameSummary).filter(models.GameSummary.game_id == game_id).delete()
    # Commit the changes to the database and refresh the affected objects
    db.commit()
    # db.flush() @to-do flush vs update vs refresh
    return deleted_count

#@To-do write test for crud, why? we make a typo in game_state.step but we have to manually change it to game_state.steps
def update_step_game_summary(game_id: str, step: int, db: Session):
    """
    Update the step number of the game state
    """
    game_state = db.query(models.GameSummary).filter(models.GameSummary.game_id == game_id).first()
    if game_state:
        game_state.steps = step
        db.commit()
        db.refresh(game_state)
    else:
        raise HTTPException(status_code=404, detail="Game state not found")

def end_game(game_id: str, db: Session):
    """
    Mark the final summary of the game as completed and the final step number
    """
    game_summary = db.query(models.GameSummary).filter(models.GameSummary.game_id == game_id).first()
    if game_summary:
        game_summary.completed = True
        db.commit()
        db.refresh(game_summary)
    else:
        raise HTTPException(status_code=404, detail="Game summary not found")