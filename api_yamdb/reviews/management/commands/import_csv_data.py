import csv
import os

from django.core.management.base import BaseCommand, CommandError

from api_yamdb.settings import BASE_DIR
from reviews.models import (Category, Comments, Genre, Review, TitleGenre,
                            Title, User)


class Command(BaseCommand):
    help = 'Import initial data from file static/data/*.csv args sequensial'

    def add_arguments(self, parser):
        parser.add_argument('files', nargs='+', type=str)

    def handle(self, *args, **options):
        obj = {
            'users.csv': User,
            'category.csv': Category,
            'genre.csv': Genre,
            'titles.csv': Title,
            'genre_title.csv': TitleGenre,
            'review.csv': Review,
            'comments.csv': Comments
        }
        foreign_key = {
            'category': [Category, 'category'],
            'title_id': [Title, 'title'],
            'genre_id': [Genre, 'genre'],
            'author': [User, 'author'],
        }
        dir_data = os.path.join(BASE_DIR, "static/data")
        for file_csv in options['files']:
            if file_csv not in obj.keys():
                raise CommandError('Unknown file to import "%s"' % file_csv)
            try:
                full_fn = os.path.join(dir_data, file_csv)
                print(full_fn)
                with open(full_fn, 'r', newline='', encoding='utf-8') as csvf:
                    reader = csv.DictReader(csvf)
                    list_obj = list()
                    for dict_now in reader:
                        kwargs = dict()
                        for key, val in dict_now.items():
                            if key in foreign_key:
                                key_new = foreign_key[key][1]
                                val_new = foreign_key[key][0](id=val)
                                kwargs[key_new] = val_new
                            else:
                                kwargs[key] = val
                        list_obj.append(obj[file_csv](**kwargs))
                    obj[file_csv].objects.bulk_create(list_obj)
            except OSError:
                raise CommandError('File "%s" does not exist' % file_csv)
            self.stdout.write(
                self.style.SUCCESS('Successfully files "%s"' % file_csv)
            )
