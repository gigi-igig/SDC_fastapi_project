from typing import Annotated
from fastapi import Depends, HTTPException

from dependencies.DBSession import SessionDep
from model.MessageDAL import create_message, get_messages_by_session
from model.Interfaces import CreateMessageRequest
from model.error import DBItemNotFound

class MessageService:
    def __init__(self, session: SessionDep):
        self.session = session

    def add_message(self, data: CreateMessageRequest):
        return create_message(data, self.session)

    def get_messages(self, session_id: int):
        return get_messages_by_session(session_id, self.session)

def get_message_service(session: SessionDep) -> MessageService:
    return MessageService(session)

MessageServiceDep = Annotated[MessageService, Depends(get_message_service)]

