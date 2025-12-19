# catalog/tests/test_builders_updated.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from catalog.models import Category, Country, Material, Mint, Coin, Banknote

User = get_user_model()


class CoinBuilder:
    """Builder для создания тестовых объектов Coin (обновленная версия)"""

    def init(self):
        self.name = "Тестовая монета"
        self.description = "Описание тестовой монеты"
        self.year = 2020
        self.denomination = 1  # Теперь integer
        self.currency = "RUB"
        self.weight = 10.5
        self.diameter = 25.0
        self.is_published = True
        self.is_on_main = False

    def with_name(self, name):
        self.name = name
        return self

    def with_year(self, year):
        self.year = year
        return self

    def with_denomination(self, denomination):
        self.denomination = denomination
        return self

    def with_weight(self, weight):
        self.weight = weight
        return self

    def with_diameter(self, diameter):
        self.diameter = diameter
        return self

    def unpublished(self):
        self.is_published = False
        return self

    def on_main(self):
        self.is_on_main = True
        return self

    def not_on_main(self):
        self.is_on_main = False
        return self

    def build(self, author=None, category=None, country=None, material=None, mint=None):
        """Создает объект Coin с заданными параметрами"""
        if not country:
            country, _ = Country.objects.get_or_create(title="Россия")

        coin = Coin(
            name=self.name,
            description=self.description,
            year=self.year,
            denomination=self.denomination,
            currency=self.currency,
            weight=self.weight,
            diameter=self.diameter,
            is_published=self.is_published,
            is_on_main=self.is_on_main,
            country=country,
        )

        if author:
            coin.author = author
        if category:
            coin.category = category
        if material:
            coin.material = material
        if mint:
            coin.mint = mint

        return coin


class BanknoteBuilder:
    """Builder для создания тестовых объектов Banknote"""

    def init(self):
        self.name = "Тестовая банкнота"
        self.description = "Описание тестовой банкноты"
        self.year = 2020
        self.denomination = 100  # Теперь integer
        self.currency = "RUB"
        self.width = 150
        self.height = 65
        self.is_published = True
        self.is_on_main = False

    def with_name(self, name):
        self.name = name
        return self

    def with_denomination(self, denomination):
        self.denomination = denomination
        return self

    def with_dimensions(self, width, height):
        self.width = width
        self.height = height
        return self

    def unpublished(self):
        self.is_published = False
        return self

    def on_main(self):
        self.is_on_main = True
        return self

    def build(self, author=None, category=None, country=None):
        """Создает объект Banknote с заданными параметрами"""
        if not country:
            country, _ = Country.objects.get_or_create(title="Россия")

        banknote = Banknote(
            name=self.name,
            description=self.description,
            year=self.year,
            denomination=self.denomination,
            currency=self.currency,
            width=self.width,
            height=self.height,
            is_published=self.is_published,
            is_on_main=self.is_on_main,
            country=country,
        )

        if author:
            banknote.author = author
        if category:
            banknote.category = category

        return banknote


class ModelBuildersTest(TestCase):
    """Тесты с использованием Test Data Builder"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.country = Country.objects.create(title="Россия")
        self.category = Category.objects.create(title="Памятные")
        self.material = Material.objects.create(title="Серебро")
        self.mint = Mint.objects.create(title="СПМД", country=self.country)

    def test_coin_builder_creates_valid_coin(self):
        """Тест создания валидной монеты через builder"""
        # Arrange
        builder = CoinBuilder()

        # Act
        coin = builder.build(
            author=self.user,
            category=self.category,
            country=self.country,
            material=self.material,
            mint=self.mint
        )
        coin.save()

        # Assert
        self.assertEqual(coin.name, "Тестовая монета")
        self.assertEqual(coin.author, self.user)
        self.assertEqual(coin.denomination, 1)
        self.assertEqual(coin.weight, 10.5)
        self.assertTrue(coin.is_published)
        self.assertFalse(coin.is_on_main)

    def test_coin_builder_with_custom_values(self):
        """Тест создания монеты с кастомными значениями"""
        # Arrange
        builder = CoinBuilder() \
            .with_name("Юбилейная монета") \
            .with_denomination(10) \
            .with_weight(15.5) \
            .with_diameter(30.0) \
            .on_main()

        # Act
        coin = builder.build(author=self.user, country=self.country)
        coin.save()

        # Assert
        self.assertEqual(coin.name, "Юбилейная монета")
        self.assertEqual(coin.denomination, 10)
        self.assertEqual(coin.weight, 15.5)
        self.assertEqual(coin.diameter, 30.0)
        self.assertTrue(coin.is_on_main)

    def test_banknote_builder_creates_valid_banknote(self):
        """Тест создания валидной банкноты через builder"""
        # Arrange
        builder = BanknoteBuilder()

        # Act
        banknote = builder.build(
            author=self.user,
            category=self.category,
            country=self.country
        )
        banknote.save()

        # Assert
        self.assertEqual(banknote.name, "Тестовая банкнота")
        self.assertEqual(banknote.author, self.user)
        self.assertEqual(banknote.denomination, 100)
        self.assertEqual(banknote.width, 150)
        self.assertEqual(banknote.height, 65)

    def test_banknote_builder_with_custom_dimensions(self):
        """Тест создания банкноты с кастомными размерами"""
        # Arrange
        builder = BanknoteBuilder() \
            .with_name("Долларовая банкнота") \
            .with_denomination(50) \
            .with_dimensions(156, 67)

        # Act
        banknote = builder.build(author=self.user, country=self.country)
        banknote.save()

        # Assert
        self.assertEqual(banknote.name, "Долларовая банкнота")
        self.assertEqual(banknote.denomination, 50)
        self.assertEqual(banknote.width, 156)
        self.assertEqual(banknote.height, 67)