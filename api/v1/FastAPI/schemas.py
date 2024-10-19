from pydantic import BaseModel
from typing import Dict, Any

###########################################################################################
# These classes defines Pydanitc models for the API, different from the SQLAlchemy models #
###########################################################################################

class GameConfig(BaseModel):
    """
    Use in request body validation for the game configuration 
    when creating a new game.
    """
    red_agent: str = "B_lineAgent"
    blue_agent: str = "BlueReactRemoveAgent"
    wrapper: str = "simple"
    steps: int = 10
