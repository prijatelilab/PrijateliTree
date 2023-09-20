from datetime import date, datetime

from pydantic import BaseModel


class User(BaseModel):
    id: int
    created_at: datetime
    created_by: int
    first_name: str
    last_name: str
    email: str
    phone_number: str
    birthdate: date
    role: str
    language_id: int

    class Config:
        orm_mode = True


class Language(BaseModel):
    id: int
    created_at: datetime
    name: str
    abbr: str

    class Config:
        orm_mode = True


class Denirs(BaseModel):
    id: int
    created_at: datetime
    created_by_session_id: int
    created_by_user_id: int
    external_id: str
    amount: int

    class Config:
        orm_mode = True


class SessionType(BaseModel):
    id: int
    created_at: datetime
    created_by: int
    name: str
    bag: str

    class Config:
        orm_mode = True


class Session(BaseModel):
    id: int
    created_at: datetime
    created_by: int
    session_type_id: int
    rounds: int

    class Config:
        orm_mode = True


class Player(BaseModel):
    id: int
    created_at: datetime
    created_by: int
    session_id: int
    player_id: int
    name_hidden: bool

    class Config:
        orm_mode = True


class SessionAnswer(BaseModel):
    id: int
    created_at: datetime
    player_id: int
    session_id: int
    player_answer: str
    correct_answer: str
    round: int

    class Config:
        orm_mode = True


class Survey(BaseModel):
    id: int
    created_at: datetime
    created_by: int
    url: str

    class Config:
        orm_mode = True


class PlayerSurveyAnswer(BaseModel):
    created_at: datetime
    player_id: int
    survey_id: int

    class Config:
        orm_mode = True
