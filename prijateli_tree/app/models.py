from sqlalchemy import Column, Date, DateTime, ForeignKey, Identity, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func as sql_func


Base = declarative_base()

STR_LEN = 80


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, Identity(start=1, cycle=True), primary_key=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=sql_func.now(),
        unique=False,
    )
    first_name = Column(String, nullable=False, unique=False)
    last_name = Column(String, nullable=False, unique=False)
    email = Column(String, nullable=True, unique=True)
    phone_number = Column(String, nullable=True, unique=True)
    birth_date = Column(Date, nullable=True, unique=False)
    language_id = Column(
        Integer,
        ForeignKey("languages.id", name="users_languages_id_fkey"),
        nullable=False,
    )


class Language(Base):
    __tablename__ = "languages"
    id = Column(Integer, Identity(start=1, cycle=True), primary_key=True)
    name = Column(String, nullable=False, unique=True)
    abbr = Column(String(2), nullable=False, unique=True)


class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, Identity(start=1, cycle=True), primary_key=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=sql_func.now(),
        unique=False,
    )
    player_name = Column(String(STR_LEN), nullable=False)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    player_language = Column(String(STR_LEN), nullable=False)
    player = relationship("Player", back_populates="sessions")


class Player(Base):
    __tablename__ = "players"
    id = Column(Integer, Identity(start=1, cycle=True), primary_key=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=sql_func.now(),
        unique=False,
    )
    player_name = Column(String(STR_LEN), nullable=False)
    player_language = Column(String(STR_LEN), nullable=False)
    total_points = Column(Integer, nullable=False, default=0)
    sessions = relationship("Session", back_populates="player")


class PlayerRound(Base):
    __tablename__ = "player_rounds"
    game_id = Column(Integer, Identity(start=1, cycle=True), primary_key=True)
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
    id = Column(Integer, Identity(start=1, cycle=True), primary_key=True)
    network_id = Column(Integer, nullable=False)
    name_condition_id = Column(Integer, nullable=False)
