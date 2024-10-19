from sqlalchemy import Boolean, Column, ForeignKey, Integer, Float, String, JSON
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
    # user_id = Column(String, index=True)  # Add user_id field
    red_agent = Column(String)
    blue_agent = Column(String)
    wrapper = Column(String)
    steps = Column(Integer)
    
    # Relationship to GameState
    states = relationship("GameState", back_populates="configuration")
    # Relationship to GameStatus
    status = relationship("GameStatus", back_populates="configuration")

class GameStatus(Base):
    __tablename__ = "game_statuses"
    game_id = Column(String, ForeignKey('game_configurations.game_id'), primary_key=True)
    completed = Column(Boolean, default=False)
    final_reward = Column(Float, default=0.0)
    
    # Relationship to GameConfiguration
    configuration = relationship("GameConfiguration", back_populates="status")
