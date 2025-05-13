from fastapi import Depends, HTTPException
from typing import Annotated, List, Dict
from dependencies.DBSession import SessionDep
from model.SessionDAL import (
    create_session as create_dal,
    read_sessions as read_all_dal,
    read_single_session as read_one_dal,
    update_session as update_dal,
    delete_session as delete_dal,
)
from model.error import DBItemNotFound
from model.Interfaces import CreateSessionRequest, ChatResponse
from model.Sessions import SessionModel
from utils.CommonQueryParam import RangeQueryParameter

class SessionService:
    def __init__(self, session: SessionDep):
        self.session = session

    def create_session(self, body: CreateSessionRequest) -> SessionModel:
        return create_dal(body, self.session)

    def read_sessions(self, range_query: RangeQueryParameter) -> List[SessionModel]:
        return read_all_dal(self.session, range_query.offset, range_query.limit)

    def read_single_session(self, session_id: int) -> SessionModel:
        try:
            return read_one_dal(session_id, self.session)
        except DBItemNotFound:
            raise HTTPException(status_code=404, detail="Session not found")

    def update_session(self, session_id: int, body: CreateSessionRequest) -> SessionModel:
        try:
            return update_dal(session_id, body, self.session)
        except DBItemNotFound:
            raise HTTPException(status_code=404, detail="Session not found")

    def delete_session(self, session_id: int) -> None:
        try:
            delete_dal(session_id, self.session)
        except DBItemNotFound:
            raise HTTPException(status_code=404, detail="Session not found")

    '''    
    def update_messages(self, session_id: int, messages: List[ChatResponse]):
        try:
            return update_m_dal(session_id, messages, self.session)
        except DBItemNotFound:
            raise HTTPException(status_code=404, detail="Session not found")
    '''

def get_session_service(session: SessionDep) -> SessionService:
    return SessionService(session)

SessionServiceDep = Annotated[SessionService, Depends(get_session_service)]
