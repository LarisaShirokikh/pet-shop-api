from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base  

from app.config import settings

engine = create_async_engine(str(settings.SQLALCHEMY_DATABASE_URI), echo=True)
SessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autocommit=False, autoflush=False
)

Base = declarative_base()