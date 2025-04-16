from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text
from sqlalchemy.sql import func

from app.db.base import Base


class Pet(Base):
    __tablename__ = "pets"

    id = Column(Integer, primary_key=True, index=True)
    
    # Основные поля
    name = Column(String(255), nullable=False, index=True)
    type = Column(String(100), nullable=False, index=True)
    breed = Column(String(255), nullable=False, index=True)
    color = Column(String(100), nullable=False, index=True)
    age = Column(Float, nullable=False, index=True)
    
    # Секретное поле для администраторов
    secret_notes = Column(Text, nullable=True)
    
    # Служебные поля
    is_available = Column(Boolean, default=True, index=True)
    price = Column(Float, nullable=True)
    
    # Аудит
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )