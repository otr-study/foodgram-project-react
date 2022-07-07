import json

from django.core.management.base import BaseCommand
from ingredients.models import Ingredient


class Command(BaseCommand):
    help = "Loads ingredients from json file."

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str)

    def handle(self, *args, **options):
        file_path = options["file_path"]
        with open(file_path, 'r') as file:
            items = json.loads(file.read())
            objects = [Ingredient(**item) for item in items]
            if objects:
                Ingredient.objects.bulk_create(objects)
