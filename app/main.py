from fastapi import FastAPI
from routers import chat, session, message
from dependencies.DBSession import engine
from sqlmodel import SQLModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from lifespan import app_lifespan
import logging

logging.basicConfig(level=logging.INFO)

# 創建資料表
SQLModel.metadata.create_all(bind=engine)

app = FastAPI(lifespan = app_lifespan)

app.include_router(chat.router)
app.include_router(session.router)
app.include_router(message.router)


app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()
    
@app.get("/routes")
def list_routes():
    return [{"path": route.path, "name": route.name} for route in app.routes]