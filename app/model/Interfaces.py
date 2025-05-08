from pydantic import BaseModel, Field, validator
from typing import List, Optional, Literal
from datetime import datetime
import re

# 回傳 message 格式（可複用）
class ChatResponse(BaseModel):
    role: str
    content: str

# 輸入 payload 結構
class ChatRequest(BaseModel):
    model: str
    messages: List[ChatResponse]
    stream: Optional[bool] = True

class SessionResponse(BaseModel):
    id: int
    title: str

class SessionData(SessionResponse):
    created_at: str

class CreateSessionRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=30)

    @validator("title")
    def validate_title(cls, v):
        if not re.match(r"^[A-Za-z0-9]+$", v):
            raise ValueError("Title must contain only letters and numbers.")
        return v
    
class CreateMessageRequest(BaseModel):
    content: str
    role: Optional[str] = "user"
    session_id: int

class MessageResponse(BaseModel):
    id: int
    content: str
    role: str