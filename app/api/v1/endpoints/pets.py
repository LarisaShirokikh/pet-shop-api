from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from app.db.session import get_db

router = APIRouter()


@router.get("/find", response_model=List[schemas.Pet])
async def find_pets(
    name: Optional[str] = None,
    type: Optional[str] = None,
    breed: Optional[str] = None,
    color: Optional[str] = None,
    min_age: Optional[float] = None,
    max_age: Optional[float] = None,
    is_available: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Поиск питомцев с фильтрами по всем полям.
    """
    # Создаем объект с параметрами поиска
    search_params = schemas.PetSearchParams(
        name=name,
        type=type,
        breed=breed,
        color=color,
        min_age=min_age,
        max_age=max_age,
        is_available=is_available,
    )
    
    # Выполняем поиск
    pets = await crud.pet.search(
        db=db, params=search_params, skip=skip, limit=limit
    )
    return pets


@router.get("/details/{pet_id}", response_model=schemas.Pet)
async def get_pet_details(
    pet_id: int,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Получить детальную информацию о питомце по его ID.
    """
    pet = await crud.pet.get(db=db, id=pet_id)
    if not pet:
        raise HTTPException(
            status_code=404,
            detail="Питомец не найден"
        )
    return pet