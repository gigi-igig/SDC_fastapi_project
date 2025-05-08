from sqlmodel import SQLModel, Field, Relationship
from typing import Optional

class MessageModel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str
    role: str = "user"
    session_id: int
