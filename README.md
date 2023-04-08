[![Django-app workflow](https://github.com/MilaSys/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)](https://github.com/MilaSys/foodgram-project-react/actions/workflows/foodgram_workflow.yml)

[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat-square&logo=PostgreSQL)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat-square&logo=NGINX)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat-square&logo=gunicorn)](https://gunicorn.org/)
[![docker](https://img.shields.io/badge/-Docker-464646?style=flat-square&logo=docker)](https://www.docker.com/)
[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat-square&logo=GitHub%20actions)](https://github.com/features/actions)
[![Yandex.Cloud](https://img.shields.io/badge/-Yandex.Cloud-464646?style=flat-square&logo=Yandex.Cloud)](https://cloud.yandex.ru/)

# Дипломная работа - Foodgramm
Сервис доступен по адресу http://51.250.28.210/
## Доступ к админ панели:
  admin@admin.ru
  admin
## Стек: 
Django, django-filter djangorestframework-simplejwt, djangorestframework, PyJWT, pytest-django, pytest-pythonpath, asgiref, gunicorn, sqlparse

## Workflow

Для использования CI CD: 
в репозитории GitHub ActionsSettings/Secrets/Actions
прописать Secrets:


* DEBUG                          # режим откладки (False по умолчанию)
* ENGINE                         # ENGINE БД (django.db.backends.postgresql по умолчанию)
* DB_NAME                        # имя БД (postgres по умолчанию)
* POSTGRES_USER                  # логин для подключения к БД (postgres по умолчанию)
* POSTGRES_PASSWORD              # пароль для подключения к БД (установить свой)
* DB_HOST=db                     # название сервиса
* DB_PORT=5432                   # порт для подключения к БД


* DOCKER_USERNAME                # имя пользователя в DockerHub
* DOCKER_PASSWORD                # пароль пользователя в DockerHub
* HOST                           # ip_address сервера
* USER                           # имя пользователя
* SSH_KEY                        # приватный ssh-ключ
* PASSPHRASE                     # кодовая фраза (пароль) для ssh-ключа (если есть)

* TELEGRAM_TO                    # id аккаунта
* TELEGRAM_TOKEN                 # токен бота


## Подготовка удалённого сервера
* Войти на удалённый сервер, для этого необходимо знать адрес сервера, имя
пользователя и пароль. Адрес сервера указывается по IP-адресу или по доменному
имени:

ssh <username>@<ip_address>


* Остановить службу
nginx:

sudo systemctl stop nginx


* Установить Docker и Docker-compose:

sudo apt update
sudo apt upgrade -y
sudo apt install docker.io
sudo apt install docker-compose -y


* Скопировать файлы 
docker-compose.yaml
и
nginx.conf
из проекта (локально) на сервер в
home/<username>/docker-compose.yaml
и
home/<username>/default.conf
соответственно:
* перейти в директорию с файлом
docker-compose.yaml
и выполните:
 
scp docker-compose.yaml <username>@<ip_address>:/home/<username>/docker-compose.yaml
  
  * перейти в директорию с файлом
default.conf
и выполните:
 

scp default.conf <username>@<ip_address>:/home/<username>/default.conf
  

## После успешного запуска контейнеров:
Создать миграции:

docker-compose exec backend python manage.py makemigrations

выполнить миграции:

docker-compose exec backend python manage.py migrate

Создать суперюзера:

docker-compose exec backend python manage.py createsuperuser

Собрать статику:

docker-compose exec backend python manage.py collectstatic --no-input

Заполнить базу данных:

sudo docker-compose exec backend python manage.py load_ingredients

sudo docker-compose exec backend python manage.py load_tags



Автор: Людмила Сыщенко
