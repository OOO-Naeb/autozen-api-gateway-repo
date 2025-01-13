# Используем официальный образ Python в качестве базового
FROM python:3.12-slim

# Устанавливаем зависимости для сборки и установки пакетов
RUN apt-get update && \
    apt-get install -y curl build-essential && \
    rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Обновляем переменные окружения
ENV PATH="/root/.local/bin:$PATH"

# Отключаем создание виртуальных окружений в Poetry
RUN poetry config virtualenvs.create false

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY . .

# Устанавливаем зависимости проекта
RUN poetry install --no-root

# Открываем порт, на котором будет работать приложение
EXPOSE 8000

# Команда для запуска приложения
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
