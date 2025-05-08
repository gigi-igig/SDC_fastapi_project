from sqlmodel import SQLModel, Field
from datetime import datetime

class SessionModel(SQLModel, table=True):
    __tablename__ = "sessions"

    id: int = Field(default=None, primary_key=True)
    title: str = Field(max_length=30)
    created_at: datetime = Field(default_factory=datetime.utcnow)
