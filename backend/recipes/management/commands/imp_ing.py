import csv

from django.core.management import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Путь к CSV файлу')

    def handle(self, *args, **options):
        file_path = options['file_path']

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row in reader:
                    name, measurement_unit = row[:2]
                    Ingredient.objects.create(
                        name=name,
                        measurement_unit=measurement_unit
                    )
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f'Файл не найден: {file_path}'))
            return
        except Exception as e:
            self.stderr.write(self.style.ERROR(
                f'Произошла ошибка при обработке файла: {e}'
            ))
            return

        self.stdout.write(self.style.SUCCESS('Загрузка успешна'))
