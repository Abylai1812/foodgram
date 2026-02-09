# [![Main Foodgram workflow](https://github.com/Abylai1812/foodgram/actions/workflows/main.yml/badge.svg?branch=main)](https://github.com/Abylai1812/foodgram/actions/workflows/main.yml)
# Описание
Фудграм» — сайт, на котором пользователи будут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Зарегистрированным пользователям также будет доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.
Настроен запуск проекта Foodgram в контейнерах,автоматическое тестирование и деплой этого проекта на удалённый сервер.
Автоматизация настроено с помощью сервиса GitHub Actions.При пуше в ветку проект тестируется,в случае успешного прохождения тестов образы обновляется на Docker Hub,
на сервере запущены контейнеры из обновлённых образов.
# Технологический стек
**Backend:**
- Python
- Django
- Django REST Framework

**Frontend:**
- React

**База данных::**
- PostgreSQL

**Контейнеризация:**
- Docker
-Docker Compose

**CI/CD:**
- GitHub Actions

**Web server / reverse proxy:**
- Nginx
# Развёртывание проекта
1) Клонировать репозиторий и перейти в него в командной строке:
```bash
git clone https://github.com/Abylai1812/foodgram.git
cd foodgram
```
2) Запускаем проект локально
 - Переходим папку backend:
```bash
cd backend
```
 - Создать активировать виртуальное окружение и установить зависимости:
```bash
python -m venv venv
source venv/Scripts/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```
 - Выполнить миграции и загружаем фикстуры:
```bash
python manage.py migrate
python manage.py load_ingredients
python manage.py load_tags
```
 - Запустить backend:  
```bash
python manage.py runserver
```
 - В отдельном терминале запустить frontend:
```bash
cd frontend
npm install
npm start
```
3) Создаем файл .env в корне проекта.
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
4) Поднимаем контейнеры
```bash
cd infra
sudo docker compose -f docker-compose.production.yml up -d
```
5) Применяем миграции
```bash
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
```
6) Загрузить фикстуры
```bash
sudo docker compose -f docker-compose.production.yml exec backend python load_ingredients
sudo docker compose -f docker-compose.production.yml exec backend python load_tags
```
7) Проект доступен по адресу:
[foodgram.redirectme.net](https://foodgram.redirectme.net)
 - Доступ к API документации
[foodgram.redirectme.net/api/docs/](https://foodgram.redirectme.net/api/docs/)
 - Доступ к API серверу
[foodgram.redirectme.net/api/](https://foodgram.redirectme.net/api/)
- Доступ к админ
[foodgram.redirectme.net/admin/](https://foodgram.redirectme.net/admin/)
# Автор
Мошанов Абылай  

- GitHub: [Abylai1812](https://github.com/Abylai1812)  
- Docker Hub: [juniorabylai](https://hub.docker.com/juniorabylai)
