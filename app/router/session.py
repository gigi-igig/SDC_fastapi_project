from fastapi import APIRouter, Depends, HTTPException, Query, Response
from typing import List, Annotated

from model.Interfaces import CreateSessionRequest, SessionResponse, SessionData
from dependencies.SessionData import SessionServiceDep  # 導入 service
from utils.CommonQueryParam import RangeQueryParameter

router = APIRouter(prefix="/sessions")

@router.post("/", response_model=SessionData, status_code=201)
def create_session(
    body: CreateSessionRequest,
    service: SessionServiceDep,
):
    session_obj = service.create_session(body)
    return SessionData(
        id=session_obj.id,
        title=session_obj.title,
        created_at=session_obj.created_at.isoformat() + "Z",
    )

@router.get("/", response_model=List[SessionResponse])
def list_sessions(
    service: SessionServiceDep,
    range_query: Annotated[RangeQueryParameter, Depends()],
):
    sessions = service.read_sessions(range_query)
    return sessions


@router.get("/{id}", response_model=SessionResponse)
def get_session(id: int, service: SessionServiceDep):
    session_obj = service.read_single_session(id)
    return session_obj


@router.put("/{id}", response_model=SessionData)
def update_session(id: int, body: CreateSessionRequest, service: SessionServiceDep):
    session_obj = service.update_session(id, body)
    return SessionData(
        id=session_obj.id,
        title=session_obj.title,
        created_at=session_obj.created_at.isoformat() + "Z",
    )

@router.delete("/{id}", status_code=204)
def delete_session(id: int, service: SessionServiceDep):
    service.delete_session(id)
    return Response(status_code=204)
