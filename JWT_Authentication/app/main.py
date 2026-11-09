from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import create_tables_database
from app.routes import user_routes

@asynccontextmanager
async def lifeSpan(app: FastAPI):
    create_tables_database()
    yield

app = FastAPI(lifespan=lifeSpan)

app.include_router(user_routes.router)



