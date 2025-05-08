from fastapi import FastAPI
from router import chat, session, message
from dependencies.DBSession import engine
from sqlmodel import SQLModel

# 創建資料表
SQLModel.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(chat.router)
app.include_router(session.router)
app.include_router(message.router)

@app.get("/routes")
def list_routes():
    return [{"path": route.path, "name": route.name} for route in app.routes]