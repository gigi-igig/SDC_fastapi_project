from sqlmodel import Session, select
from model.Messages import MessageModel
from model.Interfaces import CreateMessageRequest

def create_message(data: CreateMessageRequest, db: Session) -> MessageModel:
    message = MessageModel(content=data.content, role=data.role, session_id=data.session_id)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

def get_messages_by_session(session_id: int, db: Session) -> list[MessageModel]:
    return db.exec(select(MessageModel).where(MessageModel.session_id == session_id)).all()

