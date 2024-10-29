from pydantic import BaseModel, ConfigDict, Field
from typing import Dict, Any, Optional, Union

class Base(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
###########################################################################################
# These classes defines Pydanitc models for the API, different from the SQLAlchemy models #
###########################################################################################

class GameConfig(Base):
    """
    Use in request body validation for the game configuration 
    when creating a new game.
    """
    red_agent: str = "B_lineAgent"
    blue_agent: str = "BlueReactRemoveAgent"
    wrapper: str = "simple"
    steps: int = 10

# class Token(BaseModel):
#     access_token: str
#     token_type: str = "bearer"

#############################################################################
# For serialization and deserialization of the request and response objects #
#############################################################################

class GameSummarySchema(Base):
    game_id: str
    completed: bool
    steps: int
    final_reward: float

    class Config:
        orm_mode = True

class GameConfigurationSchema(Base):
    game_id: str
    user_id: Optional[str] = Field(default="anonymous") 
    red_agent: str
    blue_agent: str
    wrapper: str
    steps: int

    class Config:
        orm_mode = True

class GameConfigSummarySchema(Base):
    configuration: GameConfigurationSchema
    summary: GameSummarySchema
    
    class Config:
        orm_mode = True
       
########
# User #
########

class User(Base):
    user_id: str
    email: str
    full_name: Union[str, None] = None
    is_superuser: Union[bool, None] = False
    is_active: Union[bool, None] = True
    
#######
# JWT #
#######

# JSON payload containing access token
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    
# Contents of JWT token
class TokenPayload(BaseModel):
    sub: str | None = None