from django.core.exceptions import ValidationError
from django.utils import timezone
import os


def validate_year(value):
    """Валидация года выпуска"""
    current_year = timezone.now().year
    if value < 0:
        raise ValidationError('Год не может быть отрицательным')
    if value > current_year + 5:  # Допускаем будущие годы на 5 лет вперед
        raise ValidationError(f'Год не может быть больше {current_year + 5}')


def validate_image_size(value):
    """Валидация размера изображения (не более 5MB)"""
    limit = 5 * 1024 * 1024  # 5MB
    if value.size > limit:
        raise ValidationError('Размер изображения не должен превышать 5MB.')


def validate_image_extension(value):
    """Валидация расширения изображения"""
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in valid_extensions:
        raise ValidationError(
            f'Неподдерживаемый формат файла. '
            f'Допустимые форматы: {", ".join(valid_extensions)}'
        )


def validate_positive_decimal(value):
    """Валидация положительного десятичного числа"""
    if value <= 0:
        raise ValidationError('Значение должно быть положительным')


def validate_positive_integer(value):
    """Валидация положительного целого числа"""
    if value <= 0:
        raise ValidationError('Значение должно быть положительным')