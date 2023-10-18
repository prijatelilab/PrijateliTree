"""This script defines the schemas for our API"""
from pydantic import BaseModel
from datetime import datetime


class User(BaseModel):
    id: int
    created_at: datetime
    created_by: int
    first_name: str
    last_name: str
    email: str
    phone_number: str
    birth_date: datetime
    role: str
    language_id: int
    language: Language
    denirs: Denirs


class Language(BaseModel):
    id: int
    created_at: datetime
    name: str
    abbr: str
    users: User


class Denirs(BaseModel):
    id: int
    created_at: datetime
    created_by_game_id: int
    created_by_user_id: int
    external_id: str
    user: User


class GameType(BaseModel):
    id: int
    created_at: datetime
    network: str
    bag: str
    games: Game


class Game(BaseModel):
    id: int
    created_at: datetime
    created_by: int
    game_type_id: int
    rounds: int
    practice: bool
    game_type: GameType
    players: Player


class Player(BaseModel):
    id: int
    created_at: datetime
    created_by: int
    game_id: int
    user_id: int
    position: int
    name_hidden: bool
    session: Game
    answers: GameAnswer


class GameAnswer(BaseModel):
    id: int
    created_at: datetime
    game_player_id: int
    player_answer: str
    correct_answer: str
    round: int
    player: Player


class Survey(BaseModel):
    id: int
    created_at: datetime
    created_by: int
    url: str


class PlayerSurveyAnswer(BaseModel):
    id: int
    created_at: datetime
    player_id: int
    survey_id: int
