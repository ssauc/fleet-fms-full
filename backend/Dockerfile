FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir fastapi uvicorn[standard] pydantic-settings sqlalchemy[asyncio] asyncpg alembic passlib[bcrypt] python-jose[cryptography] celery redis python-multipart
COPY . /app
