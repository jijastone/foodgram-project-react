# Foodgram

## Описание
«Фудграм» — сайт, на котором пользователи будут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также будет доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Установка

1. Клонируйте проект:

```
git clone git@github.com:jijastone/foodgram-project-react.git
```

2. Перейдите в директорию `infra`:

```
cd infra
```

2. Создайте файл с переменными окружения:

```
touch .env
```

```
POSTGRES_USER=django_user
POSTGRES_PASSWORD=mysecretpassword
POSTGRES_DB=django
DB_HOST=db
DB_PORT=5432
SECRET_KEY = 'django-insecure-cg6*%6d51ef8f#4!r3*$vmxm4)abgjw8mo!4y-q*uq1!4$-89$'
DEBUG = False
ALLOWED_HOSTS = 'flaski76.ddns.net'
```

3. Запустите Docker Compose:

```
docker-compose up -d --build
```

4. Выполните по очереди команды:

```
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py collectstatic --no-input
```

5. Загрузите список ингредиентов:

```
docker-compose exec backend python manage.py load_data
```

## Проект доступен по ссылке

```
https://flaski76.ddns.net/
```

## Технологии
- Docker
- Django
- Djoser
- Python
- PostgreSQL
- Gunicorn
- Javascript

## Документация
После запуска документация доступна по адресу http://<your_server>/api/docs/redoc.html

## Примеры запросов и ответов

`GET` Запрос на адрес ```http://flaski76.ddns.net/api/users/```
```
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "email": "heroku@gmail.com",
            "id": 1,
            "username": "karloson1234",
            "first_name": "a",
            "last_name": "a",
            "is_subscribed": false
        }
    
```
`GET` Запрос на адрес ```http://flaski76.ddns.net/api/tags/```
```
[
    {
        "id": 3,
        "name": "3",
        "color": "#ffff00",
        "slug": "3"
    },
    {
        "id": 2,
        "name": "2",
        "color": "#fffff0",
        "slug": "2"
    },
    {
        "id": 1,
        "name": "1",
        "color": "#ffffff",
        "slug": "1"
    }
]
```

`GET` запрос на адрес ```http://flaski76.ddns.net/api/recipes/``` возращает:

```
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 18,
            "tags": [
                {
                    "id": 3,
                    "name": "3",
                    "color": "#ffff00",
                    "slug": "3"
                }
            ],
            "author": {
                "email": "heroku@gmail.com",
                "id": 1,
                "username": "karloson1234",
                "first_name": "a",
                "last_name": "a",
                "is_subscribed": false
            },
            "name": "драники",
            "image": "http://flaski76.ddns.net/media/static/recipe/dd60c73e-e6f1-4f90-ae82-c7b8e4172411.png",
            "text": "завтрак",
            "cooking_time": 3,
            "ingredients": [
                {
                    "id": 1,
                    "name": "картошка",
                    "measurement_unit": "шт",
                    "amount": 2
                }
            ],
            "is_favorited": false,
            "is_in_shopping_cart": false
        },
        {
            "id": 4,
            "tags": [
                {
                    "id": 3,
                    "name": "3",
                    "color": "#ffff00",
                    "slug": "3"
                },
                {
                    "id": 2,
                    "name": "2",
                    "color": "#fffff0",
                    "slug": "2"
                },
                {
                    "id": 1,
                    "name": "1",
                    "color": "#ffffff",
                    "slug": "1"
                }
            ],
            "author": {
                "email": "heroku@gmail.com",
                "id": 1,
                "username": "karloson1234",
                "first_name": "a",
                "last_name": "a",
                "is_subscribed": false
            },
            "name": "123",
            "image": "http://flaski76.ddns.net/media/static/recipe/025776ad-a998-41aa-a062-f2967cd5ce28.png",
            "text": "12",
            "cooking_time": 12,
            "ingredients": [
                {
                    "id": 2,
                    "name": "апельсин",
                    "measurement_unit": "шт",
                    "amount": 1
                }
            ],
            "is_favorited": false,
            "is_in_shopping_cart": false
        }
    ]
}
```

## Автор

**Копанев Михаил**
