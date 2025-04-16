from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator, ConfigDict


# Базовая схема питомца
class PetBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    type: str = Field(..., min_length=1, max_length=100)
    breed: str = Field(..., min_length=1, max_length=255)
    color: str = Field(..., min_length=1, max_length=100)
    age: float = Field(..., ge=0.0)
    is_available: bool = True
    price: Optional[float] = Field(None, ge=0.0)


# Схема для создания питомца (администраторы)
class PetCreate(PetBase):
    secret_notes: Optional[str] = None


# Схема для обновления питомца (администраторы)
class PetUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    type: Optional[str] = Field(None, min_length=1, max_length=100)
    breed: Optional[str] = Field(None, min_length=1, max_length=255)
    color: Optional[str] = Field(None, min_length=1, max_length=100)
    age: Optional[float] = Field(None, ge=0.0)
    is_available: Optional[bool] = None
    price: Optional[float] = Field(None, ge=0.0)
    secret_notes: Optional[str] = None


# Схема питомца из БД (базовая)
class PetInDBBase(PetBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Публичная схема питомца (без секретных полей)
class Pet(PetInDBBase):
    pass


# Схема питомца для администраторов (с секретными полями)
class PetAdmin(PetInDBBase):
    secret_notes: Optional[str] = None


# Схема для поиска питомцев
class PetSearchParams(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    breed: Optional[str] = None
    color: Optional[str] = None
    min_age: Optional[float] = Field(None, ge=0.0)
    max_age: Optional[float] = Field(None, ge=0.0)
    is_available: Optional[bool] = None
    
    @field_validator('max_age')
    @classmethod
    def check_max_age(cls, v, values):
        if v is not None and values.data.get('min_age') is not None:
            if v < values.data.get('min_age'):
                raise ValueError('max_age должен быть больше или равен min_age')
        return v