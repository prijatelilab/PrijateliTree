import os

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Identity,
    Integer,
    String,
    UniqueConstraint,
    create_engine,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship, sessionmaker
from sqlalchemy.sql import expression
from sqlalchemy.sql import func as sql_func

from prijateli_tree.app.config import config
from prijateli_tree.app.utils.constants import KEY_ENV


config = config[os.getenv(KEY_ENV)]

engine = create_engine(
    config.SQLALCHEMY_DATABASE_URI,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, Identity(start=1, cycle=True), primary_key=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=sql_func.now(),
    )
    created_by = Column(
        Integer,
        ForeignKey("users.id", name="users_created_by_fkey"),
        nullable=True,
    )
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=True, unique=True)
    hashed_password = Column(String, nullable=True)
    birth_date = Column(Date, nullable=True)
    qualtrics_id = Column(String, nullable=True)
    role = Column(String, nullable=False)
    grade_level = Column(Integer, nullable=True)
    uuid = Column(
        UUID(as_uuid=True),
        unique=True,
        server_default=text("gen_random_uuid()"),
    )
    language_id = Column(
        Integer,
        ForeignKey("languages.id", name="users_languages_id_fkey"),
        nullable=False,
    )
    language = relationship("Language", back_populates="users")
    denars = relationship("Denars", back_populates="user")
    high_school_id = Column(
        Integer,
        ForeignKey("high_schools.id", name="users_high_schools_id_fkey"),
        nullable=True,
    )
    high_school = relationship("HighSchool", back_populates="users")
    random_group = relationship("RandomGroups", back_populates="users")
    
    @property
    def name_str(self):
        return f"{self.first_name.title()} {self.last_name.title()} ({self.language.abbr.upper()})"

    __table_args__ = (
        CheckConstraint(
            "role in ('super-admin', 'admin', 'student')",
            name="role_options",
        ),
    )


class RandomGroups(Base):
    __tablename__ = "random_groups"
    id = Column(Integer, Identity(start=1, cycle=True), primary_key=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=sql_func.now(),
    )
    group_id = Column(String, nullable=False)
    user_id = Column(
        Integer,
        ForeignKey("users.id", name="user_fkey"),
        nullable=False,
    )
    users = relationship("User", back_populates="random_group")


class HighSchool(Base):
    __tablename__ = "high_schools"
    id = Column(Integer, Identity(start=1, cycle=True), primary_key=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=sql_func.now(),
    )
    name = Column(String, nullable=False, unique=True)
    users = relationship("User", back_populates="high_school")


class Language(Base):
    __tablename__ = "languages"
    id = Column(Integer, Identity(start=1, cycle=True), primary_key=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=sql_func.now(),
    )
    name = Column(String, nullable=False, unique=True)
    abbr = Column(String(2), nullable=False, unique=True)
    users = relationship("User", back_populates="language")


class Denars(Base):
    __tablename__ = "denars"
    id = Column(Integer, Identity(start=1, cycle=True), primary_key=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=sql_func.now(),
    )
    created_by_session_id = Column(
        Integer,
        ForeignKey(
            "game_sessions.id", name="denars_created_by_session_id_fkey"
        ),
        nullable=True,
    )
    created_by_user_id = Column(
        Integer,
        ForeignKey("users.id", name="denars_created_by_user_id_fkey"),
        nullable=True,
    )
    # Used for external auditing
    external_id = Column(String, nullable=True, unique=True)
    amount = Column(Integer, nullable=False)
    user = relationship("User", back_populates="denars")

    __table_args__ = (
        CheckConstraint(
            "created_by_session_id IS NOT NULL OR created_by_user_id IS NOT NULL",
            name="creation_check",
        ),
    )


class GameType(Base):
    __tablename__ = "game_types"
    id = Column(Integer, Identity(start=1, cycle=True), primary_key=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=sql_func.now(),
    )
    network = Column(String, nullable=False)
    # Will be the representation of the bag, something like RRRRBB, BBBBRR, etc.
    bag = Column(String, nullable=False)
    games = relationship("Game", back_populates="game_type")
    names_hidden = Column(Boolean, nullable=False, server_default="false")

    __table_args__ = (
        CheckConstraint(
            "network in ('integrated', 'segregated', 'self-selected')",
            name="network_options",
        ),
    )


class Game(Base):
    __tablename__ = "games"
    id = Column(Integer, Identity(start=1, cycle=True), primary_key=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=sql_func.now(),
    )
    created_by = Column(
        Integer,
        ForeignKey("users.id", name="sessions_created_by_fkey"),
        nullable=False,
    )
    game_session_id = Column(
        Integer,
        ForeignKey("game_sessions.id", name="games_game_session_id_fkey"),
        nullable=False,
    )
    game_type_id = Column(
        Integer,
        ForeignKey("game_types.id", name="games_game_type_id_fkey"),
        nullable=False,
    )
    next_game_id = Column(
        Integer,
        ForeignKey("games.id", name="games_next_game_id_fkey"),
        nullable=True,
    )
    rounds = Column(Integer, nullable=False)
    practice = Column(Boolean, default=False, nullable=False)
    game_type = relationship(
        "GameType", foreign_keys="Game.game_type_id", back_populates="games"
    )
    winning_score = Column(Integer, nullable=False)
    is_network_visible = Column(Boolean, nullable=True, server_default="false")
    players = relationship("GamePlayer", back_populates="game")
    session = relationship("GameSession", back_populates="games")


class GamePlayer(Base):
    __tablename__ = "game_players"
    id = Column(Integer, Identity(start=1, cycle=True), primary_key=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=sql_func.now(),
    )
    created_by = Column(
        Integer,
        ForeignKey("users.id", name="game_players_created_by_fkey"),
        nullable=False,
    )
    game_id = Column(
        Integer,
        ForeignKey("games.id", name="game_players_game_id_fkey"),
        nullable=False,
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", name="game_players_player_id_fkey"),
        nullable=False,
    )
    session_player_id = Column(
        Integer,
        ForeignKey("session_players.id", name="session_players_player_id_fkey"),
        nullable=False,
    )
    position = Column(Integer, nullable=False)
    initial_ball = Column(String(1), nullable=False)
    ready = Column(Boolean, nullable=False, default=False)
    completed_game = Column(Boolean, nullable=False, default=False)
    user = relationship("User", foreign_keys="GamePlayer.user_id")
    game = relationship(
        "Game",
        back_populates="players",
    )
    answers = relationship(
        "GameAnswer",
        back_populates="player",
    )

    @property
    def language(self, db: Session = next(get_db())):
        user = db.query(User).filter_by(id=self.user_id).one()
        return db.query(Language).filter_by(id=user.language_id).one()


class GameAnswer(Base):
    __tablename__ = "game_answers"
    id = Column(Integer, Identity(start=1, cycle=True), primary_key=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=sql_func.now(),
    )
    game_player_id = Column(
        Integer,
        ForeignKey("game_players.id", name="game_answers_game_players_fkey"),
        nullable=False,
    )
    player_answer = Column(String(1), nullable=False)
    correct_answer = Column(String(1), nullable=False)
    round = Column(Integer, nullable=False)
    player = relationship(
        "GamePlayer",
        back_populates="answers",
    )
    __table_args__ = (
        UniqueConstraint(
            "game_player_id", "round", name="game_player_id_round_key"
        ),
    )


class Survey(Base):
    __tablename__ = "surveys"
    id = Column(Integer, Identity(start=1, cycle=True), primary_key=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=sql_func.now(),
    )
    created_by = Column(
        Integer,
        ForeignKey("users.id", name="surveys_created_by_fkey"),
        nullable=False,
    )
    url = Column(String, nullable=False)


class PlayerSurveyAnswer(Base):
    __tablename__ = "player_survey_answers"
    id = Column(Integer, Identity(start=1, cycle=True), primary_key=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=sql_func.now(),
    )
    session_player_id = Column(
        Integer,
        ForeignKey(
            "session_players.id",
            name="player_survey_answers_session_player_id_fkey",
        ),
        nullable=False,
    )
    survey_id = Column(
        Integer,
        ForeignKey("surveys.id", name="player_survey_answers_survey_id_fkey"),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "session_player_id", "survey_id", name="uix_session_survey_answer"
        ),
        {},
    )


class GameSession(Base):
    __tablename__ = "game_sessions"
    id = Column(Integer, Identity(start=1, cycle=True), primary_key=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=sql_func.now(),
    )
    created_by = Column(
        Integer,
        ForeignKey("users.id", name="users_created_by_fkey"),
        nullable=True,
    )
    # 16 was used as the default, but it can really be any number.
    num_games = Column(Integer, nullable=False, server_default=text("16"))
    session_key = Column(String)
    finished = Column(
        Boolean, nullable=False, server_default=expression.false()
    )

    games = relationship(
        "Game",
        back_populates="session",
    )
    players = relationship("GameSessionPlayer", back_populates="session")


class GameSessionPlayer(Base):
    __tablename__ = "session_players"
    id = Column(Integer, Identity(start=1, cycle=True), primary_key=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=sql_func.now(),
    )
    created_by = Column(
        Integer,
        ForeignKey("users.id", name="users_created_by_fkey"),
        nullable=True,
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", name="session_players_user_id_fkey"),
        nullable=False,
    )
    session_id = Column(
        Integer,
        ForeignKey("game_sessions.id", name="session_players_session_id_fkey"),
        nullable=False,
    )
    ready = Column(Boolean, nullable=False, server_default=expression.false())
    points = Column(Integer, nullable=False, server_default=text("0"))
    correct_answers = Column(Integer, nullable=False, server_default=text("0"))

    user = relationship("User", foreign_keys="GameSessionPlayer.user_id")
    session = relationship("GameSession", back_populates="players")

    @property
    def language(self, db: Session = next(get_db())):
        user = db.query(User).filter_by(id=self.user_id).one()
        return db.query(Language).filter_by(id=user.language_id).one()


class PlayerNetwork(Base):
    __tablename__ = "player_networks"
    id = Column(Integer, Identity(start=1, cycle=True), primary_key=True)
    game_id = Column(
        Integer,
        ForeignKey("games.id", name="game_players_game_id_fkey"),
        nullable=False,
    )
    player_id = Column(
        Integer,
        ForeignKey("game_players.id", name="game_players_player_id_fkey"),
        nullable=False,
    )
    neighbor_id = Column(
        Integer,
        ForeignKey("game_players.id", name="game_players_neighbor_id_fkey"),
        nullable=False,
    )

    player = relationship("GamePlayer", foreign_keys="PlayerNetwork.player_id")
    neighbor = relationship(
        "GamePlayer", foreign_keys="PlayerNetwork.neighbor_id"
    )
