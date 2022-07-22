[![Django-app workflow](https://github.com/otr-study/foodgram-project-react/actions/workflows/main.yml/badge.svg)](https://github.com/otr-study/foodgram-project-react/actions/workflows/main.yml)
# Foodgram
Бэкенд приложения «Продуктовый помощник»: сайт, на котором пользователи публикуют рецепты, добавляют чужие рецепты в избранное и подписываются на публикации других авторов. Сервис «Список покупок» позволяет пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд. 

## Стэк технологий:
- Python
- Django Rest Framework
- Postgres
- Docker
- Ngnix

## Как запустить проект:

- Склонируйте репозитрий на свой компьютер
- Создайте `.env` файл в директории `infra/`. Пример файла:
    - DB_ENGINE=django.db.backends.postgresql
    - DB_NAME=<имя базы данных>
    - POSTGRES_USER=<Имя пользователя БД>
    - POSTGRES_PASSWORD=<пароль для доступа к БД>
    - DB_HOST=<db>
    - DB_PORT=<5432>
- Из папки `infra/` соберите образ при помощи docker-compose
`$ docker-compose up -d --build`
- Примените миграции
`$ docker-compose exec web python manage.py migrate`
- Соберите статику
`$ docker-compose exec web python manage.py collectstatic --no-input`
- Для доступа к админке не забудьте создать суперюзера
`$ docker-compose exec web python manage.py createsuperuser`
- Для загруки ингридиентов примените команду
`$ docker-compose exec web python manage.py load_ingredients_json data/ingredients.json`

## Документация API

Документация c примерами использования API доступна по адресу: 
```
http://84.252.137.183/api/docs/
```

## Автор
[@otr-study](https://github.com/otr-study)