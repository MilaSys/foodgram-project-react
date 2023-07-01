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

# Foodgram - «Продуктовый помощник»
Cервис, где пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

Сервис доступен по адресу http://keysi8zp.beget.tech/

## Доступ к админ панели:
  admin@admin.ru
  admin

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

* SECRET_KEY                     # секретный ключ Django

Вы можете сгенерировать ```SECRET_KEY``` следующим образом. 
Из директории проекта _/backend/_ выполнить:
```python
python manage.py shell
from django.core.management.utils import get_random_secret_key  
get_random_secret_key()
```
Полученный ключ скопировать в ```.env``` локально и в Secrets.

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

## Регистрация и авторизация
В сервисе предусмотрена система регистрации и авторизации пользователей.
Обязательные поля для пользователя:
<li> Email
<li> Логин
<li> Имя
<li> Фамилия
<li> Пароль

## Права доступа к ресурсам сервиса
    - Гость (неавторизованный пользователь)
    - Авторизованный пользователь
    - Администратор
### неавторизованные пользователи могут:

    - создать аккаунт;
    - просматривать рецепты на главной;
    - просматривать отдельные страницы рецептов;
    - Просматривать страницы пользователей.
    - фильтровать рецепты по тегам;

### авторизованные пользователи могут:

    - входить в систему под своим логином и паролем;
    - выходить из системы (разлогиниваться);
    - менять свой пароль;
    - создавать/редактировать/удалять собственные рецепты;
    - просматривать рецепты на главной;
    - просматривать страницы пользователей;
    - просматривать отдельные страницы рецептов;
    - фильтровать рецепты по тегам;
    - работать с персональным списком избранного: добавлять в него рецепты или удалять их, просматривать свою страницу избранных рецептов;
    - работать с персональным списком покупок: добавлять/удалять любые рецепты, выгружать файл с количеством необходимых ингридиентов для рецептов из списка покупок;
    - подписываться на публикации авторов рецептов и отменять подписку, просматривать свою страницу подписок;

### администратор
Администратор обладает всеми правами авторизованного пользователя.
<br> Плюс к этому он может:

    - изменять пароль любого пользователя;
    - создавать/блокировать/удалять аккаунты пользователей;
    - редактировать/удалять любые рецепты;
    - добавлять/удалять/редактировать ингредиенты;
    - добавлять/удалять/редактировать теги.

# Админка
В интерфейс админ-зоны выведены следующие поля моделей и фильтры:
### Модели:
    Доступны все модели с возможностью редактирования и удаления записей.

### Модель пользователей:
    Фильтр по email и имени пользователя.

### Модель рецептов:
    В списке рецептов доступны название и авторы рецептов.
    Фильтры по автору, названию рецепта, тегам.
    На странице рецепта выведено общее число добавлений этого рецепта в избранное.

### Модель ингредиентов:
    В списке ингредиентов доступны название ингредиента и единицы измерения.
    Фильтр по названию.

# Ресурсы сервиса

### Рецепт
Рецепт описывается полями:

    Автор публикации (пользователь).
    Ингредиенты: продукты для приготовления блюда по рецепту с указанием количества и единиц измерения.
    Тег.
    Картинка рецепта.
    Название рецепта.
    Текстовое описание.
    Время приготовления в минутах.

### Тег
Тег описывается полями:

    Название.
    Цветовой HEX-код.
    Slug.

### Ингредиент
Ингредиент описывается полями:

    Название.
    Количество (только для рецепта).
    Единицы измерения.

### Список покупок.
Список покупок скачивается в текстовом формате.

## Фильтрация по тегам
При нажатии на название тега выводится список рецептов, отмеченных этим тегом. Фильтрация может проводится по нескольким тегам в комбинации «или»: если выбраны несколько тегов — в результате должны быть показаны рецепты, которые отмечены хотя бы одним из этих тегов.
При фильтрации на странице пользователя фильтруются только рецепты выбранного пользователя. Такой же принцип соблюдается при фильтрации списка избранного.

# Примеры запросов к API.

1) регистрация пользователя

POST-запрос: /api/users/
<br /> *Request sample:*
```python
{
    "email": "string",
    "username": "string",
    "first_name": "string",
    "last_name": "string",
    "password": "string"
}
```
*Response sample (201):*
```python
{
    "email": "string",
    "id": 0,
    "username": "string",
    "first_name": "string",
    "last_name": "string"
}
```
*Response sample (400):*
```python
{
    «field_name»: [
      «Название поля, в котором произошли ошибки. Таких полей может быть несколько»
    ]
}
```

2) Получение токена

POST-запрос: /api/auth/token/login/
<br /> *Request sample:*
```python
{
    «password»: «string»,
    «email»: «string»
}
```
*Response sample (201):*
```python
{
    «auth_token»: «string»
}
```

Увидеть полную спецификацию API вы сможете развернув проект локально http://localhost/api/docs/ или на вашем хосте.


Автор: Людмила Сыщенко

