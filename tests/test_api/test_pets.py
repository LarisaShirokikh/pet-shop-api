import pytest
from httpx import AsyncClient

from app.config import settings


@pytest.mark.asyncio
async def test_create_pet(client: AsyncClient, superuser_token_headers):
    """
    Тест создания питомца через административный эндпоинт.
    """
    pet_data = {
        "name": "Тестовый питомец",
        "type": "собака",
        "breed": "Дворняжка",
        "color": "коричневый",
        "age": 1.5,
        "is_available": True,
        "price": 1000.0,
        "secret_notes": "Тестовые секретные заметки"
    }
    
    response = await client.post(
        f"{settings.API_V1_STR}/admin/pets",
        headers=superuser_token_headers,
        json=pet_data,
    )
    
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == pet_data["name"]
    assert content["type"] == pet_data["type"]
    assert content["breed"] == pet_data["breed"]
    assert content["color"] == pet_data["color"]
    assert content["age"] == pet_data["age"]
    assert content["is_available"] == pet_data["is_available"]
    assert content["price"] == pet_data["price"]
    assert content["secret_notes"] == pet_data["secret_notes"]
    assert "id" in content
    
    # Сохраняем ID для использования в других тестах
    pet_id = content["id"]
    return pet_id


@pytest.mark.asyncio
async def test_read_pet(client: AsyncClient, superuser_token_headers):
    """
    Тест чтения данных питомца.
    """
    # Сначала создаем питомца для теста
    pet_id = await test_create_pet(client, superuser_token_headers)
    
    # Пробуем получить через публичный эндпоинт
    response = await client.get(
        f"{settings.API_V1_STR}/pets/details/{pet_id}",
    )
    
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == pet_id
    assert "secret_notes" not in content  # Проверяем, что секретные поля не доступны
    
    # Пробуем получить через административный эндпоинт
    response = await client.get(
        f"{settings.API_V1_STR}/admin/pets/{pet_id}",
        headers=superuser_token_headers,
    )
    
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == pet_id
    assert "secret_notes" in content  # Проверяем наличие секретных полей для админа


@pytest.mark.asyncio
async def test_update_pet(client: AsyncClient, superuser_token_headers):
    """
    Тест обновления данных питомца.
    """
    # Сначала создаем питомца для теста
    pet_id = await test_create_pet(client, superuser_token_headers)
    
    # Обновляем данные
    update_data = {
        "name": "Обновленный питомец",
        "age": 2.0,
        "price": 1500.0
    }
    
    response = await client.put(
        f"{settings.API_V1_STR}/admin/pets/{pet_id}",
        headers=superuser_token_headers,
        json=update_data,
    )
    
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == pet_id
    assert content["name"] == update_data["name"]
    assert content["age"] == update_data["age"]
    assert content["price"] == update_data["price"]


@pytest.mark.asyncio
async def test_delete_pet(client: AsyncClient, superuser_token_headers):
    """
    Тест удаления питомца.
    """
    # Сначала создаем питомца для теста
    pet_id = await test_create_pet(client, superuser_token_headers)
    
    # Удаляем
    response = await client.delete(
        f"{settings.API_V1_STR}/admin/pets/{pet_id}",
        headers=superuser_token_headers,
    )
    
    assert response.status_code == 200
    
    # Проверяем, что питомец не найден
    response = await client.get(
        f"{settings.API_V1_STR}/pets/details/{pet_id}",
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_search_pets(client: AsyncClient):
    """
    Тест поиска питомцев через публичный эндпоинт.
    """
    # Предполагаем, что у нас есть несколько питомцев в базе
    # (создаем их в предыдущих тестах)
    
    # Поиск по типу
    response = await client.get(
        f"{settings.API_V1_STR}/pets/find?type=собака",
    )
    
    assert response.status_code == 200
    content = response.json()
    assert isinstance(content, list)
    
    # Поиск с несколькими фильтрами
    response = await client.get(
        f"{settings.API_V1_STR}/pets/find?type=собака&min_age=1.0&max_age=3.0&is_available=true",
    )
    
    assert response.status_code == 200
    content = response.json()
    
    # Проверяем, что все результаты удовлетворяют критериям поиска
    for pet in content:
        assert pet["type"] == "собака"
        assert pet["age"] >= 1.0
        assert pet["age"] <= 3.0
        assert pet["is_available"] is True