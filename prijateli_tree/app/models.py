"""Script that houses database models."""
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()

STR_LEN = 80


class Session(Base):
    __tablename__ = "sessions"
    session_id = Column(Integer, primary_key=True)
    player_name = Column(String(STR_LEN), nullable=False)
    player_id = Column(String(STR_LEN), nullable=False)
    player_language = Column(String(STR_LEN), nullable=False)


class Player(Base):
    __tablename__ = "players"
    player_id = Column(Integer, primary_key=True)
    player_name = Column(String(STR_LEN), nullable=False)
    player_language = Column(String(STR_LEN), nullable=False)
    total_points = Column(Integer, nullable=False, default=0)


class Game(Base):
    __tablename__ = "games"
    game_id = Column(Integer, primary_key=True)
    player_name = Column(String(STR_LEN), nullable=False)
    player_id = Column(String(STR_LEN), nullable=False)
    player_points = Column(Integer, nullable=False, default=0)
