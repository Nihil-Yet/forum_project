# Используем официальный Python-образ
FROM python:3.13.2

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем зависимости и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем приложение
COPY ./app /app

# Открываем порт
EXPOSE 8000

# Команда запуска
CMD ["uvicorn", "mainApp:app", "--host", "0.0.0.0", "--port", "8000"]