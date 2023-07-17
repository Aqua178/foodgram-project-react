from csv import reader

from django.db import transaction


@transaction.atomic
def data_creator(filename, model):
    print(f'Открываем {filename}')
    with open(f'{filename}', encoding='utf-8') as file:
        cf = reader(file)
        print(f'Готовим данные для модели {model.__name__}')
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
        print(f'Данные из файла {filename} успешно '
              f'загружены в модель {model.__name__}')
