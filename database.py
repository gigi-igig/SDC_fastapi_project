from sqlmodel import Session, create_engine
from sqlalchemy.orm import sessionmaker
from app.configs.config import settings

# PostgreSQL 設定
DATABASE_URL = f"postgresql://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"


# 創建引擎
engine = create_engine(DATABASE_URL)

# 會話管理函數
def get_session():
    with Session(engine) as session:
        yield session
