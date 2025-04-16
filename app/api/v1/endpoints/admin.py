from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, schemas
from app.core.security import get_current_active_superuser
from app.db.session import get_db

router = APIRouter()


@router.post("/pets", response_model=schemas.PetAdmin)
async def create_pet(
    pet_in: schemas.PetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    Создать нового питомца (только для администраторов).
    """
    pet = await crud.pet.create(db=db, obj_in=pet_in)
    return pet


@router.put("/pets/{pet_id}", response_model=schemas.PetAdmin)
async def update_pet(
    pet_id: int,
    pet_in: schemas.PetUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    Обновить данные питомца (только для администраторов).
    """
    pet = await crud.pet.get(db=db, id=pet_id)
    if not pet:
        raise HTTPException(
            status_code=404,
            detail="Питомец не найден"
        )
    pet = await crud.pet.update(db=db, db_obj=pet, obj_in=pet_in)
    return pet


@router.delete("/pets/{pet_id}", response_model=schemas.PetAdmin)
async def delete_pet(
    pet_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    Удалить питомца (только для администраторов).
    """
    pet = await crud.pet.get(db=db, id=pet_id)
    if not pet:
        raise HTTPException(
            status_code=404,
            detail="Питомец не найден"
        )
    pet = await crud.pet.remove(db=db, id=pet_id)
    return pet


@router.get("/pets", response_model=List[schemas.PetAdmin])
async def read_pets(
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
    current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    Получить список питомцев с возможностью фильтрации (только для администраторов).
    """
    search_params = schemas.PetSearchParams(
        name=name,
        type=type,
        breed=breed,
        color=color,
        min_age=min_age,
        max_age=max_age,
        is_available=is_available,
    )
    
    pets = await crud.pet.search(
        db=db, params=search_params, skip=skip, limit=limit
    )
    return pets


@router.get("/pets/{pet_id}", response_model=schemas.PetAdmin)
async def read_pet(
    pet_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """
    Получить детальную информацию о питомце, включая секретные поля (только для администраторов).
    """
    pet = await crud.pet.get(db=db, id=pet_id)
    if not pet:
        raise HTTPException(
            status_code=404,
            detail="Питомец не найден"
        )
    return pet