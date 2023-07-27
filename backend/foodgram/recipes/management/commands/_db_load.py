import logging

from csv import reader

from django.db import transaction

logging.basicConfig(level=logging.INFO)


@transaction.atomic
def data_creator(filename, model):
    logging.info('Открываем {}'.format(filename))
    with open(f'{filename}', encoding='utf-8') as file:
        cf = reader(file)
        logging.info('Готовим данные для модели {}'.format(model.__name__))
        if filename == 'ingredients.csv':
            for name, measurement_unit in cf:
                model.objects.get_or_create(
                    name=name,
                    measurement_unit=measurement_unit
                )
        if filename == 'tags.csv':
            for name, color, slug in cf:
                model.objects.get_or_create(
                    name=name,
                    color=color,
                    slug=slug
                )
        logging.info('Данные из файла {} успешно загружены в модель {}'.format(
            filename,
            model.__name__
        ))
