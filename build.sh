#!/bin/bash
# build.sh — выполняется при каждом деплое на Render

echo "Устанавливаем зависимости..."
pip install -r requirements.txt

echo "Собираем статические файлы..."
python meme/manage.py collectstatic --noinput

echo "Применяем миграции..."
python meme/manage.py migrate --noinput

echo "Сборка завершена!"