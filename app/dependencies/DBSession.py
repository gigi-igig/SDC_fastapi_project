from configs.config import settings
from sqlmodel import SQLModel, create_engine, Session
from fastapi import Depends
from typing import Annotated

# private: 資料庫 URL 設置，從設定檔讀取資料庫連接參數
__DATABASE_URL = (
    f"postgresql://{settings.postgres_user}:{settings.postgres_password}"
    f"@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"
)

# 建立引擎來連接資料庫
engine = create_engine(__DATABASE_URL)

# 定義取得資料庫會話的函數
def get_session():
    """生成一個資料庫會話"""
    with Session(engine) as session:
        yield session

def init_db(custom_engine=None, dropFirst=True):
    """
    初始化資料庫，創建所有定義的資料表。根據需要可以選擇是否刪除已存在的資料表。
    :param custom_engine: 若提供，使用此資料庫引擎。若為 None，則使用默認的 `engine`
    :param dropFirst: 是否刪除現有的資料表並重新創建
    """
    engine_to_use = custom_engine if custom_engine else engine

    if dropFirst:
        # 如果 dropFirst 是 True，先刪除資料表
        SQLModel.metadata.drop_all(engine_to_use)
    
    # 創建所有未存在的資料表
    SQLModel.metadata.create_all(engine_to_use, checkfirst=True)


# 定義資料庫會話依賴項，便於 FastAPI 使用
SessionDep = Annotated[Session, Depends(get_session)]
