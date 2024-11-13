# Foodgram-project-react
[![Foodgram](https://github.com/aqua178/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)](https://github.com/aqua178//foodgram-project-react/actions/workflows/foodgram_workflow.yml)
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
DB_ENGINE= django.db.backends.postgresql # выборд БД 
DB_NAME= postgres # имя базы данных postgres
POSTGRES_USER= postgres # логин для подключения к базе данных
POSTGRES_PASSWORD= postgres # пароль для подключения к БД (установите свой)
DB_HOST= db # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД
SECRET_KEY= default-key # секретный ключ Django
DEBUG= False # Django Debug True/False
ALLOWED_HOSTS= .localhost # Разрешенные хосты - пример '1.1.1.1, example.com'
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

### Как развернуть проект на сервере:
Установите соединение с сервером:
```
ssh username@server_address
```
Обновите индекс пакетов APT:
```
sudo apt update
```
и обновите установленные в системе пакеты и установите обновления безопасности:
```
sudo apt upgrade -y
```
Создайте папку `nginx`:
```
mkdir nginx
```
Отредактируйте файл `nginx/default.conf` и в строке `server_name` впишите IP виртуальной машины (сервера).  
Скопируйте подготовленные файлы `docker-compose.yml` и `nginx/default.conf` из вашего проекта на сервер:
```
scp docker-compose.yaml <username>@<host>/home/<username>/docker-compose.yaml
sudo mkdir nginx
scp default.conf <username>@<host>/home/<username>/nginx/default.conf
```
Установите Docker и Docker-compose:
```
sudo apt install docker.io
```
```
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```
```
sudo chmod +x /usr/local/bin/docker-compose
```
Проверьте корректность установки Docker-compose:
```
sudo  docker-compose --version
```
На сервере создайте файл .env 
```
touch .env
```
и заполните переменные окружения
```
nano .env
```
или создайте этот файл локально и скопируйте файл по аналогии с предыдущим шагом:
```
ALLOWED_HOSTS=<ALLOWED_HOSTS>
SECRET_KEY=<SECRET_KEY>
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

### Развёрнутый проект:
http://158.160.99.202

### Тестовые пользователи
Логин: ```admin``` (суперюзер)  
Email: ```admin@email.com```  
Пароль: ```admin```

### Документация к API и примеры запросов доступны по ссылке в проекте:

```
http://127.0.0.1/api/docs/
```

### Автор:

[Aleksei Vladyka](https://github.com/aqua178/)
