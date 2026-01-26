# [![Main Foodgram workflow](https://github.com/Abylai1812/foodgram/actions/workflows/main.yml/badge.svg?branch=main)](https://github.com/Abylai1812/foodgram/actions/workflows/main.yml)
# Описание
Фудграм» — сайт, на котором пользователи будут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Зарегистрированным пользователям также будет доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.
Настроен запуск проекта Foodgram в контейнерах,автоматическое тестирование и деплой этого проекта на удалённый сервер.
Автоматизация настроено с помощью сервиса GitHub Actions.При пуше в ветку проект тестируется,в случае успешного прохождения тестов образы обновляется на Docker Hub,
на сервере запущены контейнеры из обновлённых образов.
# Технологический стек
Backend: Python, Django, Django REST Framework
Frontend: React
База данных: PostgreSQL
Контейнеризация: Docker, Docker Compose
CI/CD: GitHub Actions
Web server / reverse proxy: Nginx
# Развёртывание проекта
1) Клонировать репозиторий и перейти в него в командной строке:
```bash
git clone https://github.com/Abylai1812/foodgram.git
```
2) Создаем файл .env в корне проекта.
```bash
# Пример файла env
SECRET_KEY=ваш_секретный_ключ
ALLOWED_HOSTS=yourdomain.ru,localhost,127.0.0.1

# PostgreSQL
POSTGRES_USER=django_user
POSTGRES_PASSWORD=django_password
POSTGRES_DB=django_db
DB_HOST=db
DB_PORT=5432
```
3) Поднимаем контейнеры
```bash
sudo docker compose -f docker-compose.production.yml up -d
```
4) Применяем миграции
```bash
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
```
5) Домен:
```bash
https://foodgram.redirectme.net
```
# Автор
Мошанов Абылай
GitHub: https://github.com/Abylai1812
Dockerhub: https://hub.docker.com/juniorabylai

