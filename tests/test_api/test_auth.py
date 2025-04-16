import pytest
from httpx import AsyncClient

from app.config import settings


@pytest.mark.asyncio
async def test_register_superuser(client: AsyncClient):
    """
    Тест регистрации тестового суперпользователя.
    """
    user_data = {
        "email": "test-superuser@example.com",
        "password": "testpassword123",
    }
    
    response = await client.post(
        f"{settings.API_V1_STR}/auth/register-test-superuser",
        json=user_data,
    )
    
    assert response.status_code == 200
    content = response.json()
    assert content["email"] == user_data["email"]
    assert content["is_superuser"] is True
    assert "id" in content
    
    # Проверяем, что повторная регистрация возвращает существующего пользователя
    response2 = await client.post(
        f"{settings.API_V1_STR}/auth/register-test-superuser",
        json=user_data,
    )
    
    assert response2.status_code == 200
    content2 = response2.json()
    assert content2["id"] == content["id"]


@pytest.mark.asyncio
async def test_login_access_token(client: AsyncClient):
    """
    Тест получения токена доступа.
    """
    # Сначала регистрируем пользователя
    user_data = {
        "email": "test-login@example.com",
        "password": "testpassword123",
    }
    
    await client.post(
        f"{settings.API_V1_STR}/auth/register-test-superuser",
        json=user_data,
    )
    
    # Пробуем получить токен
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"],
    }
    
    response = await client.post(
        f"{settings.API_V1_STR}/auth/token",
        data=login_data,
    )
    
    assert response.status_code == 200
    content = response.json()
    assert "access_token" in content
    assert content["token_type"] == "bearer"
    
    # Пробуем с неверным паролем
    bad_login_data = {
        "username": user_data["email"],
        "password": "wrongpassword",
    }
    
    response = await client.post(
        f"{settings.API_V1_STR}/auth/token",
        data=bad_login_data,
    )
    
    assert response.status_code == 400
    
    # Пробуем с несуществующим email
    bad_login_data = {
        "username": "nonexistent@example.com",
        "password": user_data["password"],
    }
    
    response = await client.post(
        f"{settings.API_V1_STR}/auth/token",
        data=bad_login_data,
    )
    
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_access_admin_endpoints(client: AsyncClient, superuser_token_headers):
    """
    Тест доступа к административным эндпоинтам с токеном.
    """
    # Проверяем доступ к административному эндпоинту с токеном
    response = await client.get(
        f"{settings.API_V1_STR}/admin/pets",
        headers=superuser_token_headers,
    )
    
    assert response.status_code == 200
    
    # Проверяем доступ без токена
    response = await client.get(
        f"{settings.API_V1_STR}/admin/pets",
    )
    
    assert response.status_code == 401  # Unauthorized