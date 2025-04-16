FROM python:3.11-slim

# Устанавливаем базовые зависимости
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    gnupg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Установка Poetry
RUN pip install --no-cache-dir poetry

# Копируем только файлы, необходимые для установки зависимостей
COPY pyproject.toml /app/

# Генерируем файл poetry.lock, если его нет
RUN poetry config virtualenvs.create false \
    && poetry lock \
    && poetry install --no-interaction --no-ansi --no-root


COPY . .


# Команда запуска приложения
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]