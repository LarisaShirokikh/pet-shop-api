from datetime import datetime, timedelta
from typing import Any, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, schemas
from app.config import settings
from app.db.session import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/token"
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля по хешу."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Получение хеша пароля."""
    return pwd_context.hash(password)


def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    """Создание JWT токена."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


async def get_current_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> models.User:
    """Получение текущего пользователя по JWT токену."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось подтвердить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = schemas.TokenPayload(sub=int(user_id))
    except JWTError:
        raise credentials_exception
    user = await crud.user.get(db, id=token_data.sub)
    if not user:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """Проверка, что текущий пользователь активен."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Неактивный пользователь")
    return current_user


async def get_current_active_superuser(
    current_user: models.User = Depends(get_current_active_user),
) -> models.User:
    """Проверка, что текущий пользователь является суперпользователем."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Недостаточно прав"
        )
    return current_user