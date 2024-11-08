import datetime
import uuid
from typing import List
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Float, String, JSON
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import relationship

from .database import Base

class GameState(Base):
    __tablename__ = "game_states"
    
    game_id = Column(String, ForeignKey('game_configurations.game_id', ondelete="CASCADE"), primary_key=True)
    step = Column(Integer, primary_key=True)
    data = Column(JSON)

    # Relationship to GameConfiguration
    configuration = relationship("GameConfiguration", back_populates="states")

class GameConfiguration(Base):
    __tablename__ = "game_configurations"
    
    game_id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.user_id', ondelete="CASCADE"), default="anonymous")
    red_agent = Column(String)
    blue_agent = Column(String)
    wrapper = Column(String)
    steps = Column(Integer)
    createdAt = Column(DateTime, default=datetime.datetime.now())

    # Relationship to GameState
    states = relationship("GameState", back_populates="configuration", cascade="all, delete-orphan")
    # Relationship to GameSummary (One-to-One)
    summary = relationship("GameSummary", back_populates="configuration", cascade="all, delete-orphan", uselist=False)
    # Relationship to User
    user = relationship("User", back_populates="configurations")

class GameSummary(Base):
    __tablename__ = "game_summary"
    
    game_id = Column(String, ForeignKey('game_configurations.game_id', ondelete="CASCADE"), primary_key=True)
    completed = Column(Boolean, default=False)
    steps = Column(Integer, default=0)
    final_reward = Column(Float, default=0.0)

    # Relationship to GameConfiguration
    configuration = relationship("GameConfiguration", back_populates="summary")

class User(Base):
    __tablename__ = "users"

    user_id: uuid.UUID = Column(String, primary_key=True)
    full_name = Column(String)
    email = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    # Relationship to GameConfiguration
    configurations = relationship("GameConfiguration", back_populates="user", cascade="all, delete")
    
    