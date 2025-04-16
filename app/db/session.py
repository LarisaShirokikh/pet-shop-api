from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import SessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Зависимость для получения сессии базы данных.
    """
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()