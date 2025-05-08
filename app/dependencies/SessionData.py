from typing import Annotated
from fastapi import Depends, HTTPException

from dependencies.DBSession import SessionDep
from model.SessionDAL import (
    create_session as create_session_dal,
    read_sessions as read_sessions_dal,
    read_single_session,
    update_session as update_session_dal,
    delete_session as delete_session_dal,
)
from model.error import DBItemNotFound
from model.Interfaces import CreateSessionRequest
from model.Sessions import SessionModel
from utils.CommonQueryParam import RangeQueryParameter


class SessionService:
    def __init__(self, session: SessionDep):
        self.session = session

    def create_session(self, body: CreateSessionRequest) -> SessionModel:
        return create_session_dal(body, self.session)

    def read_sessions(self, range_query: RangeQueryParameter) -> list[SessionModel]:
        return read_sessions_dal(
            session=self.session,
            offset=range_query.offset,
            limit=range_query.limit,
        )

    def read_single_session(self, session_id: int) -> SessionModel:
        try:
            return read_single_session(session_id, self.session)
        except DBItemNotFound:
            raise HTTPException(status_code=404, detail="Session not found")

    def update_session(self, session_id: int, body: CreateSessionRequest) -> SessionModel:
        try:
            return update_session_dal(session_id, body, self.session)
        except DBItemNotFound:
            raise HTTPException(status_code=404, detail="Session not found")

    def delete_session(self, session_id: int) -> None:
        try:
            delete_session_dal(session_id, self.session)
        except DBItemNotFound:
            raise HTTPException(status_code=404, detail="Session not found")

def get_session_service(session: SessionDep) -> SessionService:
    return SessionService(session)

SessionServiceDep = Annotated[SessionService, Depends(get_session_service)]
