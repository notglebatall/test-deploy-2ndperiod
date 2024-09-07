# Используем базовый образ Python 3.12
FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Обновление списка пакетов и установка необходимых инструментов
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    gnupg2

# Установка Google Chrome (из официального репозитория)
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable

# Указание версии ChromeDriver для установки (должна соответствовать версии Google Chrome)
ARG CHROMEDRIVER_VERSION=116.0.5845.96

# Скачивание и установка ChromeDriver
RUN wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip" && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    rm /tmp/chromedriver.zip && \
    chmod +x /usr/local/bin/chromedriver

# Копируем файл requirements.txt в контейнер
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все содержимое текущей директории в контейнер
COPY . .

# Указываем команду по умолчанию для запуска контейнера
CMD ["python", "main.py"]
