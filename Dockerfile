# Используем базовый образ Python 3.12
FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл requirements.txt в контейнер
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все содержимое текущей директории в контейнер
COPY . .

# Указываем команду по умолчанию для запуска контейнера
CMD ["python", "main.py"]