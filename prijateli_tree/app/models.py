"""Script that houses database models."""
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base


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


class PlayerRound(Base):
    __tablename__ = "player_rounds"
    game_id = Column(Integer, primary_key=True)
    session_id = Column(Integer, nullable=False)
    player_name = Column(String(STR_LEN), nullable=False)
    player_id = Column(String(STR_LEN), nullable=False)
    player_points = Column(Integer, nullable=False, default=0)
    # where the player is in the network
    network_position = Column(Integer, nullable=False)
    # random draw shown
    random_draw = Column(Integer, nullable=False)


class GameRound(Base):
    __tablename__ = "game_rounds"
    game_id = Column(Integer, primary_key=True)
    # chosen bag
    bag_id = Column(Integer, nullable=False)
    # network condition
    network_id = Column(Integer, nullable=False)
    # Names condition
    name_condition_id = Column(Integer, nullable=False)
