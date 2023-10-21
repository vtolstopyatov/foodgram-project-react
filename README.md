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

## Шаблон для .env файла:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
LANG=en_US.utf8
DJANGO_KEY=django-insecure-co7)afx^mahqw57otvyz083y@8%tu$^y(kog+i2=+lfu%sb!tb
```
