import json

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    '''Загружает ингредиенты в БД из ingredients.json файла.'''

    def handle(self, *args, **options):

        with open('data/ingredients.json', 'rb') as f:
            data = json.load(f)
        count_all = len(data)
        objs = set()
        for i in data:
            name = i.get('name')
            measurement_unit = i.get('measurement_unit')
            if not Ingredient.objects.filter(
                name=name,
                measurement_unit=measurement_unit,
            ).exists():
                objs.add((name, measurement_unit))
        count = len(objs)
        uniq_objs = [
            Ingredient(name=n, measurement_unit=m) for n, m in objs
        ]
        Ingredient.objects.bulk_create(uniq_objs)
        print(f'Добавлено {count} из {count_all} ингредиентов')
