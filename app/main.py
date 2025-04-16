from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncConnection

from app.api.v1.router import api_router
from app.config import settings
from app.db.base import Base, engine
from app.db.init_db import init_db
from app.db.session import SessionLocal


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Lifespan стартовал. Проверка базы данных...")

    try:
        async with engine.begin() as conn:
            result = await conn.execute(
                text("SELECT to_regclass('public.pets');")
            )
            pets_table_exists = result.scalar() is not None

            if not pets_table_exists:
                logger.info("Таблицы не найдены. Создаём...")
                await conn.run_sync(Base.metadata.create_all)

                async with SessionLocal() as session:
                    await init_db(session)
                logger.info("База данных успешно инициализирована.")
            else:
                logger.info("Таблицы уже существуют. Пропускаем инициализацию.")
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при инициализации базы данных: {e}")

    yield  

    logger.info("Lifespan завершён.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)


if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


app.include_router(api_router, prefix=settings.API_V1_STR)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        description=settings.DESCRIPTION,
        routes=app.routes,
    )
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

@app.get("/", tags=["health"])
async def health_check():
    """
    Проверка работоспособности API.
    """
    return {"status": "ok", "message": "Pet Shop API работает!"}