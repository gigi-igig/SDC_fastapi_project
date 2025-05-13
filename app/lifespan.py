from contextlib import asynccontextmanager
from fastapi import FastAPI

from dependencies.DBSession import init_db


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    # on startup
    init_db(drop_first=False)
    yield
    # on shutdown