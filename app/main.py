from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.controllers import auth_controller, chat_controller
from app.models.base import engine, Base

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

# Include routers
app.include_router(
    auth_controller.router,
    prefix=f"{settings.API_V1_STR}/auth",
    tags=["authentication"]
)

app.include_router(
    chat_controller.router,
    prefix=f"{settings.API_V1_STR}/chat",
    tags=["chat"]
)


@app.on_event("startup")
async def startup_event():
    # Initialize database tables
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@app.get("/")
async def root():
    return {"message": "Chat API is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
