from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Literal
from datetime import datetime
import re

# 回傳 message 格式（可複用）
class ChatResponse(BaseModel):
    role: Literal["user", "assistant"]  # 限制 role 欄位為 'user' 或 'assistant'
    content: str
    
    def to_dict(self) -> dict:
        return {"role": self.role, "content": self.content}
    
# 輸入 payload 結構
class ChatRequest(BaseModel):
    model: str
    messages: List[ChatResponse]
    stream: bool = True  # 改為強制的布林值，預設為 True
    ''' 驗證 model 欄位的合法性
    @field_validator('model')
    @classmethod
    def validate_model(cls, v):
        valid_models = ["phi3", "other_model"]  # 這裡加入你的有效模型名稱
        if v not in valid_models:
            raise ValueError(f"Model '{v}' is not valid.")
        return v
    '''
    
class SessionResponse(BaseModel):
    id: int
    title: str

class SessionData(SessionResponse):
    created_at: str

class CreateSessionRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=30)

    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        if not re.match(r"^[A-Za-z0-9]+$", v):
            raise ValueError("Title must contain only letters and numbers.")
        return v
    
class CreateMessageRequest(BaseModel):
    content: str
    role: Optional[str] = "user"
    session_id: int

    def to_create_request(self, session_id: int):
        return CreateMessageRequest(
            content=self.content,
            role=self.role,
            session_id=session_id
        )

class MessageResponse(ChatResponse):
    id: int
