from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, JSON
from sqlalchemy.orm import relationship

from .database import Base

class GameState(Base):
    __tablename__ = "game_states"
    # @ Temparary solution, need migration in the future 
    game_id = Column(String, primary_key=True)
    step = Column(Integer, primary_key=True)
    data = Column(JSON)
