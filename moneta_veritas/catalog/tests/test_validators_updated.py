# catalog/tests/test_validators_updated.py
import os
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile

from catalog.validators import (
    validate_year,
    validate_denomination,
    validate_image_size,
    validate_image_extension,
    validate_positive_decimal,
    validate_positive_integer
)


class ValidatorsTest(TestCase):
    """Тесты для кастомных валидаторов"""

    def test_validate_year_with_valid_values(self):
        """Тест валидатора года с корректными значениями"""
        test_cases = [
            (2020, None),  # Корректный год
            (2025, None),  # Год на 5 лет вперед (допускается)
            (1900, None),  # Старый год
            (0, ValidationError),  # Ноль
            (-100, ValidationError),  # Отрицательный год
            (timezone.now().year + 6, ValidationError),  # Больше чем на 5 лет вперед
        ]

        for year, expected_error in test_cases:
            with self.subTest(year=year):
                if expected_error is None:
                    try:
                        validate_year(year)
                    except ValidationError:
                        self.fail(f"validate_year({year}) вызвал исключение неожиданно")
                else:
                    with self.assertRaises(expected_error):
                        validate_year(year)

    def test_validate_denomination_positive(self):
        """Тест валидатора номинала для положительных значений"""
        # Arrange & Act & Assert
        validate_denomination(1)  # Должно пройти без ошибок
        validate_denomination(1000)  # Должно пройти без ошибок

    def test_validate_denomination_negative(self):
        """Тест валидатора номинала для некорректных значений"""
        test_cases = [
            (0, "Номинал должен быть положительным"),
            (-1, "Номинал должен быть положительным"),
            (-100, "Номинал должен быть положительным"),
        ]

        for value, expected_message in test_cases:
            with self.subTest(value=value):
                with self.assertRaises(ValidationError) as cm:
                    validate_denomination(value)

                self.assertEqual(str(cm.exception), f"['{expected_message}']")

    def test_validate_image_size_within_limit(self):
        """Тест валидатора размера изображения в пределах лимита"""
        # Arrange
        small_image = BytesIO()
        Image.new('RGB', (100, 100)).save(small_image, 'JPEG')
        small_image.seek(0)

        uploaded_file = SimpleUploadedFile(
            "small.jpg",
            small_image.read(),
            content_type="image/jpeg"
        )

        # Act & Assert
        try:
            validate_image_size(uploaded_file)
        except ValidationError:
            self.fail("validate_image_size вызвал исключение для маленького файла")

    def test_validate_image_size_exceeds_limit(self):
        """Тест валидатора размера изображения превышающего лимит"""
        # Arrange
        # Создаем файл больше 5MB (5 * 1024 * 1024 + 1)
        large_content = b'x' * (5 * 1024 * 1024 + 1)
        large_file = SimpleUploadedFile(
            "large.jpg",
            large_content,
            content_type="image/jpeg"
        )

        # Act & Assert
        with self.assertRaises(ValidationError) as cm:
            validate_image_size(large_file)

        self.assertIn("Размер изображения не должен превышать 5MB", str(cm.exception))

    def test_validate_image_extension_valid(self):
        """Тест валидатора расширения изображения для корректных расширений"""
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']

        for ext in valid_extensions:
            with self.subTest(extension=ext):
                file = SimpleUploadedFile(
                    f"test{ext}",
                    b"fake content",
                    content_type=f"image/{ext.replace('.', '')}"
                )

                try:
                    validate_image_extension(file)
                except ValidationError:
                    self.fail(f"validate_image_extension вызвал исключение для {ext}")

    def test_validate_image_extension_invalid(self):
        """Тест валидатора расширения изображения для некорректных расширений"""
        invalid_extensions = ['.pdf', '.doc', '.txt', '.exe']

        for ext in invalid_extensions:
            with self.subTest(extension=ext):
                file = SimpleUploadedFile(
                    f"test{ext}",
                    b"fake content",
                    content_type="application/octet-stream"
                )

                with self.assertRaises(ValidationError) as cm:
                    validate_image_extension(file)

                self.assertIn("Неподдерживаемый формат файла", str(cm.exception))

    def test_validate_positive_decimal(self):
        """Тест валидатора положительных десятичных чисел"""
        # Корректные значения
        validate_positive_decimal(0.1)
        validate_positive_decimal(1.0)
        validate_positive_decimal(100.5)

        # Некорректные значения
        with self.assertRaises(ValidationError):
            validate_positive_decimal(0)

        with self.assertRaises(ValidationError):
            validate_positive_decimal(-1.5)

    def test_validate_positive_integer(self):
        """Тест валидатора положительных целых чисел"""
        # Корректные значения
        validate_positive_integer(1)
        validate_positive_integer(100)

        # Некорректные значения
        with self.assertRaises(ValidationError):
            validate_positive_integer(0)

        with self.assertRaises(ValidationError):
            validate_positive_integer(-10)