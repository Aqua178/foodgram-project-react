# Foodgram-project-react
[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat-square&logo=NGINX)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat-square&logo=gunicorn)](https://gunicorn.org/)
[![docker](https://img.shields.io/badge/-Docker-464646?style=flat-square&logo=docker)](https://www.docker.com/)
[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat-square&logo=GitHub%20actions)](https://github.com/features/actions)
[![Yandex.Cloud](https://img.shields.io/badge/-Yandex.Cloud-464646?style=flat-square&logo=Yandex.Cloud)](https://cloud.yandex.ru/)
[![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)](https://www.django-rest-framework.org/)
[![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
### Цель проекта: Продуктовый помощник

На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

### Используемый стек:

Django DRF Framework
PostgreSQL
Nginx
Docker
React

### Как запустить проект в Docker:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/Aqua178/foodgram-project-react.git
```

```
cd infra
```

Используемые в проекте переменные окружения infra/.env

```
DB_ENGINE= # выборд БД 
DB_NAME= # имя базы данных postgres
POSTGRES_USER= # логин для подключения к базе данных
POSTGRES_PASSWORD= # пароль для подключения к БД (установите свой)
DB_HOST= # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД
SECRET_KEY= # секретный ключ Django
DEBUG= # Django Debug True/False
ALLOWED_HOSTS= # Разрешенные хосты - пример '1.1.1.1, example.com'
```

```
cd infra
```

Запустить конейнеры:

```
docker-compose up -d
```

Проверить статус запущенных контейнеров:

```
docker ps
```

Выполнить миграции:

```
docker-compose exec backend python3 manage.py migrate
```

Загрузка ингредиентов в БД:

```
docker-compose exec backend python3 manage.py load_foodgram_data
```

Создать пользователя:

```
docker-compose exec backend python3 manage.py createsuperuser
```

Собрать static файлы:

```
docker-compose exec backend python3 manage.py collectstatic --no-input
```

### Документация к API и примеры запросов доступны по ссылке в проекте:

```
http://127.0.0.1/api/docs/
```

### Автор:

Aleksei Vladyka
