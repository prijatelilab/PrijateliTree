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
