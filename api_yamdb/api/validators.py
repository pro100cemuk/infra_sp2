import datetime as dt
from django.core.exceptions import ValidationError


def validate_username(value):
    if value == 'me':
        raise ValidationError(
            'Имя пользователя me не допустимо'
        )
    return value


def validate_year(value):
    current_year = dt.datetime.now().year
    if not 0 <= value <= current_year:
        raise ValidationError(
            'Проверьте год создания произведения (должен быть нашей эры).'
        )
    return value


def validate_score(value):
    if not 1 <= value <= 10:
        raise ValidationError(
            'Оценкой может быть целое число в диапазоне от 1 до 10.'
        )
    return value
