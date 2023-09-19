"""Script that houses database models."""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()

STR_LEN = 80


class Player(Base):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True)
    name = Column(String(STR_LEN), nullable=False)
    language = Column(String(STR_LEN), nullable=False)
    points_received = Column(Integer, nullable=False, default=0)
