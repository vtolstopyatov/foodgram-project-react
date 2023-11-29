![example workflow](https://github.com/vtolstopyatov/foodgram-project-react/actions/workflows//foodgram_workflow.yml/badge.svg)
# Описание:
Cайт Foodgram, «Продуктовый помощник».

На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

# Посмотреть:
* Адрес сайта — http://aboba.pro
* Имя пользователя — `adm@adm.adm`
* Пароль — `adm`

# Запустить:
- Скопировать репозиторий
- В папке «infra» запустить контейнер:
```docker-compose up```
- Создать .env файл
- Заполнить БД ингредиентами:
```docker-compose exec web python manage.py load_data```
- Создать суперпользователя:
```docker-compose exec web python manage.py createsuperuser```

## Использованые фреймворки и библиотеки:
- [Django](https://www.djangoproject.com/)
- [Django REST framework](https://www.django-rest-framework.org/)
- [django-filter](https://django-filter.readthedocs.io/en/stable/)
- [Djoser](https://djoser.readthedocs.io/)
- [Gunicorn](https://gunicorn.org/)

## Автор:
- [Владимир Толстопятов](https://github.com/vtolstopyatov)