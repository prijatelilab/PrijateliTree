from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

STR_LEN = 80


class Session(Base):
    __tablename__ = "sessions"
    session_id = Column(Integer, primary_key=True)
    player_name = Column(String(STR_LEN), nullable=False)
    player_id = Column(Integer, ForeignKey("players.player_id"), nullable=False)
    player_language = Column(String(STR_LEN), nullable=False)
    player = relationship("Player", back_populates="sessions")


class Player(Base):
    __tablename__ = "players"
    player_id = Column(Integer, primary_key=True)
    player_name = Column(String(STR_LEN), nullable=False)
    player_language = Column(String(STR_LEN), nullable=False)
    total_points = Column(Integer, nullable=False, default=0)
    sessions = relationship("Session", back_populates="player")


class PlayerRound(Base):
    __tablename__ = "player_rounds"
    game_id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("sessions.session_id"), nullable=False)
    player_name = Column(String(STR_LEN), nullable=False)
    player_id = Column(Integer, ForeignKey("players.player_id"), nullable=False)
    player_points = Column(Integer, nullable=False, default=0)
    network_position = Column(Integer, nullable=False)
    random_draw = Column(Integer, nullable=False)
    session = relationship("Session", back_populates="player_rounds")
    player = relationship("Player", back_populates="player_rounds")


class GameRound(Base):
    __tablename__ = "game_rounds"
    game_id = Column(Integer, primary_key=True)
    bag_id = Column(Integer, nullable=False)
    network_id = Column(Integer, nullable=False)
    name_condition_id = Column(Integer, nullable=False)
