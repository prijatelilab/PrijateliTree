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
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func as sql_func


Base = declarative_base()


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
    phone_number = Column(String, nullable=True, unique=True)
    birth_date = Column(Date, nullable=True)
    role = Column(String, nullable=False)
    language_id = Column(
        Integer,
        ForeignKey("languages.id", name="users_languages_id_fkey"),
        nullable=False,
    )
    language = relationship("Language", back_populates="users")
    denirs = relationship("Denirs", back_populates="user")

    __table_args__ = (
        CheckConstraint(
            "role in ('super-admin', 'admin', 'student')",
            name="role_options",
        ),
    )


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


class Denirs(Base):
    __tablename__ = "denirs"
    id = Column(Integer, Identity(start=1, cycle=True), primary_key=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=sql_func.now(),
    )
    created_by_session_id = Column(
        Integer,
        ForeignKey("sessions.id", name="denirs_created_by_session_id_fkey"),
        nullable=True,
    )
    created_by_user_id = Column(
        Integer,
        ForeignKey("users.id", name="denirs_created_by_user_id_fkey"),
        nullable=True,
    )
    # Used for external auditing
    external_id = Column(String, nullable=True, unique=True)
    amount = Column(Integer, nullable=False)
    user = relationship("User", back_populates="denirs")

    __table_args__ = (
        CheckConstraint(
            "created_by_session_id IS NOT NULL OR created_by_user_id IS NOT NULL",
            name="created_by_check",
        ),
    )


class SessionType(Base):
    __tablename__ = "session_types"
    id = Column(Integer, Identity(start=1, cycle=True), primary_key=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=sql_func.now(),
    )
    network = Column(String, nullable=False, unique=True)
    # Will be the representation of the bag, something like RRRRBB, BBBBRR, etc.
    bag = Column(String, nullable=False)
    sessions = relationship("Session", back_populates="session_type")

    __table_args__ = (
        CheckConstraint(
            "network in ('integrated', 'segregated', 'self-selected')",
            name="network_options",
        ),
    )


class Session(Base):
    __tablename__ = "sessions"
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
    session_type_id = Column(
        Integer,
        ForeignKey("users.id", name="sessions_session_type_id_fkey"),
        nullable=False,
    )
    rounds = Column(Integer, nullable=False)
    practice = Column(Boolean, default=False, nullable=False)
    session_type = relationship("SessionType", back_populates="sessions")
    players = relationship("Player", back_populates="session")


class Player(Base):
    __tablename__ = "session_players"
    id = Column(Integer, Identity(start=1, cycle=True), primary_key=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=sql_func.now(),
    )
    created_by = Column(
        Integer,
        ForeignKey("users.id", name="session_players_created_by_fkey"),
        nullable=False,
    )
    session_id = Column(
        Integer,
        ForeignKey("sessions.id", name="session_players_session_id_fkey"),
        nullable=False,
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", name="session_players_player_id_fkey"),
        nullable=False,
    )
    position = Column(Integer, nullable=False)
    name_hidden = Column(Boolean, nullable=False)
    session = relationship(
        "Session",
        foreign_keys="[Player.user_id, Player.session_id]",
        back_populates="players",
    )
    answers = relationship(
        "SessionAnswer",
        foreign_keys="[Player.user_id, Player.session_id]",
        back_populates="player",
    )


class SessionAnswer(Base):
    __tablename__ = "session_answers"
    id = Column(Integer, Identity(start=1, cycle=True), primary_key=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=sql_func.now(),
    )
    session_player_id = Column(
        Integer,
        ForeignKey("session_players.id", name="session_answers_session_players_fkey"),
        nullable=False,
    )
    player_answer = Column(String(1), nullable=False)
    correct_answer = Column(String(1), nullable=False)
    round = Column(Integer, nullable=False)
    player = relationship("Player", back_populates="answers")


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
    player_id = Column(
        Integer,
        ForeignKey("player.id", name="player_survey_answers_player_id_fkey"),
        nullable=False,
    )
    survey_id = Column(
        Integer,
        ForeignKey("surveys.id", name="player_survey_answers_survey_id_fkey"),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "player_id", "survey_id", "session_id", name="uix_session_answer"
        ),
        {},
    )
