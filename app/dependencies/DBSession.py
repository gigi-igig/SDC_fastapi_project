from configs.config import settings
from sqlmodel import SQLModel, create_engine, Session
from fastapi import Depends
from typing import Annotated

# private

__DATABASE_URL = (
    f"postgresql://{settings.postgres_user}:{settings.postgres_password}"
    f"@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"
)

engine = create_engine(__DATABASE_URL)


def get_session():
    with Session(engine) as session:
        yield session


# public

def init_db():
    # must import model before creating tables
    import model.Sessions
    SQLModel.metadata.create_all(engine, checkfirst=True)


SessionDep = Annotated[Session, Depends(get_session)]