from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


# Базовая схема пользователя
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False


# Схема для создания пользователя
class UserCreate(UserBase):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)


# Схема для обновления пользователя
class UserUpdate(UserBase):
    password: Optional[str] = Field(None, min_length=8, max_length=100)


# Схема для данных из базы
class UserInDBBase(UserBase):
    id: int
    email: EmailStr
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Полная схема пользователя (для ответов API)
class User(UserInDBBase):
    pass


# Схема пользователя с хешем пароля (только для внутреннего использования)
class UserInDB(UserInDBBase):
    hashed_password: str


# Схема токена доступа
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Схема полезной нагрузки токена
class TokenPayload(BaseModel):
    sub: Optional[int] = None