from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from app.config import settings
from app.core.security import create_access_token
from app.db.session import get_db

router = APIRouter()


@router.post("/token", response_model=schemas.Token)
async def login_access_token(
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 совместимый токен для входа, получает JWT токен для доступа
    """
    user = await crud.user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=400, detail="Неверный email или пароль"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=400, detail="Неактивный пользователь"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/register-test-superuser", response_model=schemas.User, tags=["tests"])
async def register_test_superuser(
    user_in: schemas.UserCreate,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Регистрация тестового суперпользователя.
    Этот эндпоинт используется только для тестов и не должен быть доступен в производственной среде.
    """
    user = await crud.user.get_by_email(db, email=user_in.email)
    if user:
        return user
    
    user_in_superuser = schemas.UserCreate(
        email=user_in.email,
        password=user_in.password,
        is_superuser=True,
    )
    user = await crud.user.create(db, obj_in=user_in_superuser)
    return user