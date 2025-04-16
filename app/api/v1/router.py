from fastapi import APIRouter

from app.api.v1.endpoints import admin, auth, pets

api_router = APIRouter()

# Публичные эндпоинты
api_router.include_router(pets.router, prefix="/pets", tags=["pets"])

# Административные эндпоинты
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])

# Аутентификация
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])