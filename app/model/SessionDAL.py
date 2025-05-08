from sqlmodel import Session, select
from datetime import datetime
from model.error import DBItemNotFound

from model.Sessions import SessionModel
from model.Interfaces import CreateSessionRequest


def create_session(session_req: CreateSessionRequest, session: Session) -> SessionModel:
    session_db = SessionModel(
        title=session_req.title,
        created_at=datetime.utcnow()
    )
    session.add(session_db)
    session.commit()
    session.refresh(session_db)
    return session_db


def read_sessions(
    session: Session,
    offset: int = 0,
    limit: int = 100,
) -> list[SessionModel]:
    sessions = session.exec(select(SessionModel).offset(offset).limit(limit)).all()
    return list(sessions)


def read_single_session(session_id: int, session: Session) -> SessionModel:
    session_data = session.get(SessionModel, session_id)
    if session_data is None:
        raise DBItemNotFound
    return session_data


def update_session(session_id: int, session_req: CreateSessionRequest, session: Session) -> SessionModel:
    session_db = session.get(SessionModel, session_id)
    if session_db is None:
        raise DBItemNotFound

    update_data = session_req.model_dump(exclude_unset=True)
    session_db.sqlmodel_update(update_data)

    session.add(session_db)
    session.commit()
    session.refresh(session_db)
    return session_db


def delete_session(session_id: int, session: Session) -> SessionModel:
    session_db = session.get(SessionModel, session_id)
    if session_db is None:
        raise DBItemNotFound

    session.delete(session_db)
    session.commit()
    return session_db
