from configs.config import settings
from sqlmodel import SQLModel, create_engine, Session
from fastapi import Depends
from typing import Annotated


DATABASE_URL = (
    f"postgresql://{settings.postgres_user}:{settings.postgres_password}"
    f"@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"
)

engine = create_engine(DATABASE_URL)

def get_session():
    with Session(engine) as session:
        yield session

def init_db(custom_engine=None, drop_first=True):
    engine_to_use = custom_engine or engine
    if drop_first:
        SQLModel.metadata.drop_all(engine_to_use, checkfirst=True)
    SQLModel.metadata.create_all(engine_to_use, checkfirst=True)

SessionDep = Annotated[Session, Depends(get_session)]
