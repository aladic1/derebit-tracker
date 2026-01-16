
Deribit Price Tracker API
Полнофункциональное приложение для отслеживания цен криптовалют с биржи Deribit. Собирает цены BTC и ETH каждую минуту, сохраняет в базу данных и предоставляет REST API для доступа к данным.

🚀 Быстрый старт (Docker Compose)
Требования
Docker 20.10+

Docker Compose 2.0+

Запуск за 3 шага:
Клонируйте репозиторий:

bash
git clone <repository-url>
cd deribit-tracker
Запустите приложение:

bash
docker-compose up --build
Откройте в браузере:

API документация: http://localhost:8000/docs

Приложение: http://localhost:8000

Health check: http://localhost:8000/health

📊 Основные возможности
Автоматический сбор данных: Цены BTC и ETH обновляются каждую минуту

REST API: 3 endpoint'а для доступа к данным

PostgreSQL: Надежное хранение исторических данных

Redis: Брокер сообщений для Celery

Docker: Полная контейнеризация

🛠️ Технологический стек
FastAPI - современный веб-фреймворк для Python

PostgreSQL - реляционная база данных

Redis - брокер сообщений и кэш

Celery - асинхронная очередь задач

SQLAlchemy - ORM для работы с БД

Aiohttp - асинхронный HTTP-клиент

Docker - контейнеризация приложения

📡 API Endpoints
1. Получить все данные по валюте
text
GET /api/v1/prices?ticker={ticker}
Параметры:

ticker (обязательный): BTC или ETH

limit (опциональный): количество записей (по умолчанию 100)

skip (опциональный): смещение для пагинации

Пример:

bash
curl "http://localhost:8000/api/v1/prices?ticker=BTC&limit=3"
2. Получить последнюю цену
text
GET /api/v1/prices/latest?ticker={ticker}
Параметры:

ticker (обязательный): BTC или ETH

Пример:

bash
curl "http://localhost:8000/api/v1/prices/latest?ticker=ETH"
3. Получить цены по дате
text
GET /api/v1/prices/date?ticker={ticker}&date={date}
Параметры:

ticker (обязательный): BTC или ETH

date (обязательный): дата в формате YYYY-MM-DD

Пример:

bash
curl "http://localhost:8000/api/v1/prices/date?ticker=BTC&date=2024-01-15"
🐳 Развертывание с Docker
Полная конфигурация Docker Compose
yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: deribit_user
      POSTGRES_PASSWORD: deribit_password
      POSTGRES_DB: deribit_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://deribit_user:deribit_password@postgres:5432/deribit_db
      REDIS_URL: redis://redis:6379/0
      CELERY_BROKER_URL: redis://redis:6379/0
      DERIBIT_API_URL: https://test.deribit.com/api/v2/public
    depends_on:
      - postgres
      - redis

  celery-worker:
    build: .
    command: celery -A celery_app worker --loglevel=info
    environment:
      DATABASE_URL: postgresql+asyncpg://deribit_user:deribit_password@postgres:5432/deribit_db
      REDIS_URL: redis://redis:6379/0
      CELERY_BROKER_URL: redis://redis:6379/0
    depends_on:
      - postgres
      - redis
      - app

  celery-beat:
    build: .
    command: celery -A celery_app beat --loglevel=info
    environment:
      DATABASE_URL: postgresql+asyncpg://deribit_user:deribit_password@postgres:5432/deribit_db
      REDIS_URL: redis://redis:6379/0
      CELERY_BROKER_URL: redis://redis:6379/0
    depends_on:
      - postgres
      - redis
      - app

volumes:
  postgres_data:
  redis_data:
💻 Локальная разработка (без Docker)
Требования
Python 3.11+

PostgreSQL 15+

Redis 7+

Установка
Клонируйте репозиторий:

bash
git clone <repository-url>
cd deribit-tracker
Создайте виртуальное окружение:

bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
Установите зависимости:

bash
pip install -r requirements.txt
Настройте окружение:

bash
cp .env.example .env
# Отредактируйте .env файл под ваши настройки
Запустите базу данных и Redis:

bash
# PostgreSQL (через Docker)
docker run -d --name postgres \
  -e POSTGRES_USER=deribit_user \
  -e POSTGRES_PASSWORD=deribit_password \
  -e POSTGRES_DB=deribit_db \
  -p 5432:5432 \
  postgres:15-alpine

# Redis (через Docker)
docker run -d --name redis \
  -p 6379:6379 \
  redis:alpine
Примените миграции:

bash
alembic upgrade head
Запустите приложение:

Терминал 1 - FastAPI:

bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
Терминал 2 - Celery Worker:

bash
celery -A celery_app worker --loglevel=info --pool=solo
Терминал 3 - Celery Beat:

bash
celery -A celery_app beat --loglevel=info --schedule=/tmp/celerybeat-schedule
🧪 Тестирование
Запуск тестов
bash
# Установите тестовые зависимости
pip install pytest pytest-asyncio pytest-cov

# Запустите тесты
pytest tests/ -v

# С покрытием кода
pytest tests/ -v --cov=app --cov-report=html
Структура тестов
text
tests/
├── test_api.py          # Тесты API endpoints
├── test_services.py     # Тесты бизнес-логики
└── conftest.py         # Фикстуры для тестов
📁 Структура проекта
text
deribit-tracker/
├── app/
│   ├── api/              # FastAPI endpoints и зависимости
│   ├── core/             # Конфигурация, база данных, Celery
│   ├── models/           # SQLAlchemy модели
│   ├── schemas/          # Pydantic схемы для валидации
│   ├── services/         # Бизнес-логика и клиент Deribit
│   ├── tasks/            # Celery задачи
│   └── main.py          # Точка входа приложения
├── tests/               # Unit тесты
├── migrations/          # Alembic миграции базы данных
├── docker/             # Docker конфигурация
├── docker-compose.yml  # Полное развертывание
├── requirements.txt    # Зависимости Python
├── celery_app.py       # Конфигурация Celery
└── README.md          # Документация
⚙️ Конфигурация
Переменные окружения (.env)
env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/deribit_db
SYNC_DATABASE_URL=postgresql://user:password@localhost:5432/deribit_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Deribit API
DERIBIT_API_URL=https://test.deribit.com/api/v2/public
DERIBIT_BASE_URL=https://test.deribit.com

# Application
DEBUG=true
LOG_LEVEL=INFO
ALLOWED_TICKERS=BTC,ETH
HOST=0.0.0.0
PORT=8000
Использование продуктивного API Deribit
Для получения реальных рыночных данных замените в .env:

env
DERIBIT_API_URL=https://www.deribit.com/api/v2/public
DERIBIT_BASE_URL=https://www.deribit.com
🔧 Устранение неполадок
Проблема: Не запускается база данных
bash
# Проверьте что PostgreSQL запущен
docker ps | grep postgres

# Проверьте логи
docker logs postgres
Проблема: Celery не видит задачи
bash
# Перезапустите worker с явным указанием модулей
celery -A celery_app worker --loglevel=info --pool=solo --include=app.tasks.fetch_prices
Проблема: Ошибки миграций
bash
# Создайте новую миграцию
alembic revision --autogenerate -m "Fix migrations"

# Примените миграции
alembic upgrade head
Проблема: Не хватает памяти
bash
# Увеличьте лимиты в docker-compose.yml
services:
  postgres:
    mem_limit: 512m
  redis:
    mem_limit: 256m
📈 Мониторинг
Проверка состояния системы
bash
# Проверить что все сервисы запущены
docker-compose ps

# Проверить логи приложения
docker-compose logs app

# Проверить логи Celery
docker-compose logs celery-worker

# Проверить базу данных
docker exec -it deribit-tracker-postgres-1 psql -U deribit_user -d deribit_db -c "SELECT COUNT(*) FROM prices;"
API Health Checks
bash
# Основной health check
curl http://localhost:8000/health

# Проверка базы данных через API
curl http://localhost:8000/api/v1/prices?ticker=BTC&limit=1