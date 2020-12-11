import csv

from django.core.management.base import BaseCommand  # , CommandError

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Load Ingredients data to database'

    def handle(self, *args, **options):
        with open('recipes/fixtures/ingredients.csv', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                title, unit = row
                Ingredient.objects.get_or_create(title=title, unit=unit)
                # get_or_create сначала проверяет есть ли такой элемент в БД
