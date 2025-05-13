from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List

from model.Interfaces import CreateMessageRequest, MessageResponse
from dependencies.MessageData import MessageServiceDep
from dependencies.SessionData import SessionServiceDep  # 確認 session 存在用

router = APIRouter(prefix="/messages")

@router.post("/", response_model=MessageResponse, status_code=201)
def add_message(
    body: CreateMessageRequest,
    message_service: MessageServiceDep,
    session_service: SessionServiceDep
):
    # 驗證 session 是否存在
    if session_service.read_single_session(body.session_id) is None:
        raise HTTPException(status_code=404, detail="Session ID not found.")
    
    msg = message_service.add_message(body)
    return msg

@router.get("/", response_model=List[MessageResponse])
def list_messages(
    message_service: MessageServiceDep,
    session_service: SessionServiceDep,
    session_id: int = Query(..., description="ID of the session"),
):
    # 驗證 session 是否存在
    if session_service.read_single_session(session_id) is None:
        raise HTTPException(status_code=404, detail="Session ID not found.")
    
    return message_service.get_messages(session_id)
