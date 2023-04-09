from django.core.management.base import BaseCommand
from recipes.models import Ingredients
import json


class Command(BaseCommand):

    def handle(self, *args, **options):

        with open('ingredients.json', 'rb') as f:
            data = json.load(f)
            count_all = 0
            count = 0
            for i in data:
                count_all += 1
                name = i.get('name')
                measurement_unit = i.get('measurement_unit')
                if (
                    name
                    and measurement_unit
                    and Ingredients.objects.filter(name=name).count() == 0
                ):
                    count += 1
                    ingredients = Ingredients()
                    ingredients.name = name
                    ingredients.measurement_unit = measurement_unit
                    ingredients.save()

        print(f'Добавлено {count} из {count_all} ингредиентов')
