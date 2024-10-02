from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, JSON
from sqlalchemy.orm import relationship

from .database import Base

class GameState(Base):
    __tablename__ = "game_states"
    game_id = Column(String, ForeignKey('game_configurations.game_id'), primary_key=True)
    step = Column(Integer, primary_key=True)
    data = Column(JSON)
    
    # Relationship to GameConfiguration
    configuration = relationship("GameConfiguration", back_populates="states")

class GameConfiguration(Base):
    __tablename__ = "game_configurations"
    game_id = Column(String, primary_key=True)
    red_agent = Column(String)
    blue_agent = Column(String)
    wrapper = Column(String)
    steps = Column(Integer)
    
    # Relationship to GameState
    states = relationship("GameState", back_populates="configuration")
