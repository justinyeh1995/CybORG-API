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
    user_id = Column(String, ForeignKey('users.user_id'))
    red_agent = Column(String)
    blue_agent = Column(String)
    wrapper = Column(String)
    steps = Column(Integer)

    # Relationship to GameState
    states = relationship("GameState", back_populates="configuration")
    # Relationship to GameSummary (One-to-One)
    summary = relationship("GameSummary", back_populates="configuration", uselist=False)
    # Relationship to User
    user = relationship("User", back_populates="configurations")

class GameSummary(Base):
    __tablename__ = "game_statuses"
    game_id = Column(String, ForeignKey('game_configurations.game_id'), primary_key=True)
    completed = Column(Boolean, default=False)
    final_reward = Column(Float, default=0.0)

    # Relationship to GameConfiguration
    configuration = relationship("GameConfiguration", back_populates="summary")

class User(Base):
    __tablename__ = "users"
    user_id = Column(String, primary_key=True)
    username = Column(String)
    email = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    # Relationship to GameConfiguration
    configurations = relationship("GameConfiguration", back_populates="user")
