# Pet Shop API

Проект API для магазина домашних животных на FastAPI.

## Особенности

- 🐍 Python 3.10+
- 🚀 [FastAPI](https://fastapi.tiangolo.com/) для высокопроизводительного API с автоматической документацией
- 🗄️ [SQLAlchemy](https://www.sqlalchemy.org/) 2.0 с асинхронной поддержкой
- 🔐 JWT аутентификация
- 🔍 фильтрация и поиск
- 📦 [Pydantic](https://pydantic-docs.helpmanual.io/) для валидации данных
- 🐳 Docker и Docker Compose для простого развертывания
- 🔄 Миграции базы данных с помощью Alembic
- 📊 PostgreSQL для хранения данных
- 🧪 Готовность к тестированию с pytest

## Структура проекта


Проект организован по принципу "чистой архитектуры" и разделен на слои:
<details>
<summary>Показать структуру</summary>

```
pet_shop/
│
├── alembic/                 # Для миграций базы данных
│   └── versions/
│
├── app/
│   ├── __init__.py
│   ├── main.py              # Точка входа в приложение
│   ├── config.py            # Конфигурация приложения
│   ├── dependencies.py      # Зависимости (DI)
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── endpoints/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── pets.py   # Публичные эндпоинты
│   │   │   │   └── admin.py  # Административные эндпоинты
│   │   │   └── router.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── security.py      # JWT и аутентификация
│   │   └── exceptions.py    # Обработка исключений
│   │
│   ├── crud/
│   │   ├── __init__.py
│   │   ├── base.py         # Базовый CRUD
│   │   └── pet.py          # CRUD для питомцев
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── session.py      # Сессия БД
│   │   └── base.py         # Базовая модель БД
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── pet.py          # Модель питомца
│   │   └── user.py         # Модель пользователя
│   │
│   └── schemas/
│       ├── __init__.py
│       ├── pet.py          # Pydantic схемы для питомцев
│       └── user.py         # Pydantic схемы для пользователей
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_api/
│   │   ├── __init__.py
│   │   ├── test_pets.py
│   │   └── test_admin.py
│   └── test_crud/
│       ├── __init__.py
│       └── test_pet.py
│
├── .env                    # Переменные окружения
├── .gitignore
├── pyproject.toml          # Зависимости и метаданные
├── alembic.ini             # Конфигурация Alembic
└── README.md
```
</details>

## API Эндпоинты

### Публичные эндпоинты (без авторизации)
- `GET /api/v1/pets/find` - Поиск питомцев с фильтрами
- `GET /api/v1/pets/details/{pet_id}` - Просмотр деталей питомца

### Административные эндпоинты (с авторизацией)
- `POST /api/v1/admin/pets` - Создание питомца
- `PUT /api/v1/admin/pets/{pet_id}` - Редактирование питомца
- `DELETE /api/v1/admin/pets/{pet_id}` - Удаление питомца
- `GET /api/v1/admin/pets` - Поиск питомцев с фильтрами (с секретными полями)
- `GET /api/v1/admin/pets/{pet_id}` - Просмотр деталей питомца (с секретными полями)

### Аутентификация
- `POST /api/v1/auth/token` - Получение JWT токена

## Запуск проекта

### Предварительные требования
- Установленные [Docker](https://www.docker.com/) и [Docker Compose](https://docs.docker.com/compose/)
- Python и Poetry для локального запуска (опционально)

> ✅ **Примечание:** Для удобства проверки тестового задания:
> - база данных создаётся автоматически
> - применяются все миграции Alembic
> - создается суперпользователь на основе `.env`
> - в базу загружаются первичные тестовые данные

### Шаги для запуска

1. Клонировать репозиторий:
```bash
git clone https://github.com/larisashirokikh/pet-shop-api.git
cd pet-shop-api
```

2. Создать файл .env :
```bash
cp .env.example .env
```

# Настройки базы данных
POSTGRES_SERVER=db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=pet_shop

# Настройки приложения
SECRET_KEY=my-super-secret-key-should-be-at-least-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Superuser
FIRST_SUPERUSER=admin@mail.ru
FIRST_SUPERUSER_PASSWORD=admin123

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]

3. Запустить контейнеры с помощью Docker Compose:
```bash
docker-compose up -d
```

4. API будет доступно по адресу http://localhost:8000
5. Документация Swagger доступна по адресу http://localhost:8000/docs
6. PgAdmin для управления базой данных доступен по адресу http://localhost:5050

## Использование API

### Аутентификация

Для доступа к административным эндпоинтам необходимо получить JWT токен:

```bash
curl -X POST "http://localhost:8000/api/v1/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@mail.ru.com&password=admin123"
```

Затем использовать полученный токен в заголовке Authorization для запросов к защищенным эндпоинтам:

```bash
curl -X GET "http://localhost:8000/api/v1/admin/pets" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Пример поиска питомцев

```bash
# Поиск всех доступных собак
curl -X GET "http://localhost:8000/api/v1/pets/find?type=собака&is_available=true"
```

## Разработка

### Запуск тестов

```bash
docker-compose exec api pytest
```

### Применение миграций

```bash
docker-compose exec api alembic upgrade head
```

### Создание новой миграции

```bash
docker-compose exec api alembic revision --autogenerate -m "описание изменений"
```

## Лицензия

MIT