import json

from django.core.management.base import BaseCommand

from tags.models import Tag


class Command(BaseCommand):
    help = "Loads tags from json file."

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str)

    def handle(self, *args, **options):
        file_path = options["file_path"]
        with open(file_path, 'r') as file:
            items = json.loads(file.read())
            objects = [Tag(**item) for item in items]
            if objects:
                Tag.objects.bulk_create(objects)
