from sqlalchemy.orm import Session

from CybORG.FastAPI import models, schemas

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