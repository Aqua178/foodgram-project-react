import os

from django.conf import settings
from django.core.management import BaseCommand

from recipes.models import Ingredient, Tag

from ._db_load import data_creator

DATA_TO_MODEL_MAPPING = (
    ('ingredients.csv', Ingredient,),
    ('tags.csv', Tag,),
)


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            os.chdir(settings.DATA_DIR)
            for filename, model in DATA_TO_MODEL_MAPPING:
                data_creator(filename, model)
        except Exception as error:
            print(error)
