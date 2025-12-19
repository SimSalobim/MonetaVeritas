# catalog/tests/test_forms_and_mixins.py
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from catalog.forms import CoinForm, BanknoteForm
from catalog.mixins import AuthorRequiredMixin, AuthorOrPublishedMixin
from catalog.models import Coin, Country, Category

User = get_user_model()


class FormsTest(TestCase):
    """Тесты для форм"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.country = Country.objects.create(title="Россия")
        self.category = Category.objects.create(title="Монеты")

        # Создаем тестовое изображение
        self.test_image = SimpleUploadedFile(
            "test.jpg",
            b"fake image content",
            content_type="image/jpeg"
        )

    def test_coin_form_valid_data(self):
        """Тест формы CoinForm с валидными данными"""
        # Arrange
        form_data = {
            'name': 'Тестовая монета',
            'country': self.country.id,
            'category': self.category.id,
            'year': 2020,
            'denomination': 1,
            'currency': 'RUB',
            'is_published': True,
            'is_on_main': False,
        }

        # Act
        form = CoinForm(data=form_data, files={'image': self.test_image})

        # Assert
        self.assertTrue(form.is_valid())

    def test_coin_form_invalid_year(self):
        """Тест формы CoinForm с невалидным годом"""
        # Arrange
        form_data = {
            'name': 'Тестовая монета',
            'country': self.country.id,
            'year': 3000,  # Невалидный год (больше чем на 5 лет вперед)
            'denomination': 1,
            'currency': 'RUB',
        }

        # Act
        form = CoinForm(data=form_data)

        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn('year', form.errors)

    def test_coin_form_missing_required_fields(self):
        """Тест формы CoinForm без обязательных полей"""
        # Arrange
        form_data = {
            'name': '',  # Пустое обязательное поле
            'denomination': -1,  # Отрицательный номинал
        }

        # Act
        form = CoinForm(data=form_data)

        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('denomination', form.errors)

    def test_banknote_form_valid_data(self):
        """Тест формы BanknoteForm с валидными данными"""
        # Arrange
        form_data = {
            'name': 'Тестовая банкнота',
            'country': self.country.id,
            'category': self.category.id,
            'year': 2020,
            'denomination': 100,
            'currency': 'RUB',
            'width': 150,
            'height': 65,
            'is_published': True,
            'is_on_main': False,
        }

        # Act
        form = BanknoteForm(data=form_data, files={'image': self.test_image})

        # Assert
        self.assertTrue(form.is_valid())

    def test_banknote_form_clean_year_method(self):
        """Тест метода clean_year формы BanknoteForm"""
        # Arrange
        form_data = {
            'name': 'Тестовая банкнота',
            'country': self.country.id,
            'year': -100,  # Отрицательный год
            'denomination': 100,
            'currency': 'RUB',
        }

        # Act
        form = BanknoteForm(data=form_data)

        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn('year', form.errors)


class MixinsTest(TestCase):
    """Тесты для кастомных миксинов"""

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123'
        )

        self.country = Country.objects.create(title="Россия")
        self.category = Category.objects.create(title="Монеты")

        # Создаем тестовые объекты
        self.published_coin = Coin.objects.create(
            name='Опубликованная монета',
            country=self.country,
            denomination=1,
            year=2020,
            is_published=True,
            author=self.user
        )

        self.unpublished_coin = Coin.objects.create(
            name='Неопубликованная монета',
            country=self.country,
            denomination=2,
            year=2020,
            is_published=False,
            author=self.user
        )

        self.other_user_coin = Coin.objects.create(
            name='Монета другого пользователя',
            country=self.country,
            denomination=5,
            year=2020,
            is_published=False,
            author=self.other_user
        )

    def test_author_required_mixin_with_author(self):
        """Тест миксина AuthorRequiredMixin для автора"""

        # Arrange
        class TestView(AuthorRequiredMixin):
            def get_object(self):
                return self.published_coin

        view = TestView()
        view.request = Mock(user=self.user)

        # Act
        result = view.test_func()

        # Assert
        self.assertTrue(result)

    def test_author_required_mixin_with_non_author(self):
        """Тест миксина AuthorRequiredMixin для не-автора"""

        # Arrange
        class TestView(AuthorRequiredMixin):
            def get_object(self):
                return self.published_coin

        view = TestView()
        view.request = Mock(user=self.other_user)

        # Act
        result = view.test_func()

        # Assert
        self.assertFalse(result)

    def test_author_or_published_mixin_authenticated_user(self):
        """Тест миксина AuthorOrPublishedMixin для авторизованного пользователя"""

        # Arrange
        class TestView(AuthorOrPublishedMixin):
            model = Coin

            def get_queryset(self):
                return Coin.objects.all()

        view = TestView()
        view.request = Mock(user=self.user, GET={})

        # Act
        queryset = view.get_queryset()

        # Assert
        # Должны видеть свои объекты и опубликованные чужие
        self.assertIn(self.published_coin, queryset)  # Свой опубликованный
        self.assertIn(self.unpublished_coin, queryset)  # Свой неопубликованный
        # Чужой неопубликованный не должен быть виден
        self.assertNotIn(self.other_user_coin, queryset)

    def test_author_or_published_mixin_anonymous_user(self):
        """Тест миксина AuthorOrPublishedMixin для анонимного пользователя"""

        # Arrange
        class TestView(AuthorOrPublishedMixin):
            model = Coin

            def get_queryset(self):
                return Coin.objects.all()

        view = TestView()
        view.request = Mock(user=Mock(is_authenticated=False), GET={})

        # Act
        queryset = view.get_queryset()

        # Assert
        # Должны видеть только опубликованные объекты
        self.assertIn(self.published_coin, queryset)
        self.assertNotIn(self.unpublished_coin, queryset)
        self.assertNotIn(self.other_user_coin, queryset)