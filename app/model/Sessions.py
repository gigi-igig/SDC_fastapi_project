from sqlmodel import SQLModel, Field, Column, JSON
from datetime import datetime
from typing import List, Optional
from model.Interfaces import ChatResponse

class SessionModel(SQLModel, table=True):
    __tablename__ = "sessions"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=30)
    created_at: datetime = Field(default_factory=datetime.utcnow)
