import logging
from typing import Dict, List

from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from app.config import settings
from app.core.security import get_password_hash

logger = logging.getLogger(__name__)


# Данные для начального заполнения базы
INITIAL_PETS = [
    {
        "name": "Мухтар",
        "type": "собака",
        "breed": "Алабай",
        "color": "серый",
        "age": 2.5,
        "is_available": True,
        "price": 25000.0,
        "secret_notes": "Отличная родословная, чемпион выставок"
    },
    {
        "name": "Барсик",
        "type": "кошка",
        "breed": "Шотландская вислоухая",
        "color": "серый",
        "age": 1.2,
        "is_available": True,
        "price": 15000.0,
        "secret_notes": "Родился в питомнике, есть ветеринарный паспорт"
    },
    {
        "name": "Кеша",
        "type": "попугай",
        "breed": "Волнистый",
        "color": "зеленый",
        "age": 0.7,
        "is_available": True,
        "price": 5000.0,
        "secret_notes": "Ручной, умеет говорить простые фразы"
    },
    {
        "name": "Рекс",
        "type": "собака",
        "breed": "Немецкая овчарка",
        "color": "черно-подпалый",
        "age": 3.0,
        "is_available": False,
        "price": 30000.0,
        "secret_notes": "Служебная собака, прошел курс дрессировки"
    },
    {
        "name": "Пушок",
        "type": "кошка",
        "breed": "Персидская",
        "color": "белый",
        "age": 2.0,
        "is_available": True,
        "price": 18000.0,
        "secret_notes": "Требует тщательного ухода за шерстью"
    }
]


async def init_db(db: AsyncSession) -> None:
    """
    Инициализация базы данных начальными данными.
    """
    # Создаем суперпользователя, если он не существует
    user = await crud.user.get_by_email(db, email=settings.FIRST_SUPERUSER)
    if not user:
        user_in = schemas.UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        await crud.user.create(db, obj_in=user_in)
        logger.info("Создан суперпользователь")
    
    # Добавляем начальные данные о питомцах
    for pet_data in INITIAL_PETS:
        # Проверяем, существует ли уже питомец с таким именем и породой
        existing_pet = await crud.pet.get_by_unique_attributes(
            db, 
            name=pet_data["name"],
            type=pet_data["type"],
            breed=pet_data["breed"]
        )
        if not existing_pet:
            pet_in = schemas.PetCreate(**pet_data)
            await crud.pet.create(db, obj_in=pet_in)
            logger.info(f"Создан питомец: {pet_data['name']}")
    
    logger.info("База данных инициализирована")