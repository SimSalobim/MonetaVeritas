from django.test import TestCase, Client
from django.urls import reverse
from catalog.models import Coin, Banknote, Country, Category


class HomepageViewTest(TestCase):
    """Тесты для представления главной страницы"""
    
    def setUp(self):
        self.client = Client()
        self.country = Country.objects.create(title="Россия")
        self.category = Category.objects.create(title="Тестовая категория")
        
        # Создаем опубликованные монеты для главной
        self.coin_on_main = Coin.objects.create(
            name="Монета на главной",
            country=self.country,
            category=self.category,
            denomination="1 рубль",
            year=2020,
            is_published=True,
            is_on_main=True
        )
        
        # Создаем опубликованную монету НЕ для главной
        self.coin_not_on_main = Coin.objects.create(
            name="Монета не на главной",
            country=self.country,
            category=self.category,
            denomination="2 рубля",
            year=2020,
            is_published=True,
            is_on_main=False
        )
        
        # Создаем неопубликованную монету
        self.coin_unpublished = Coin.objects.create(
            name="Неопубликованная монета",
            country=self.country,
            category=self.category,
            denomination="5 рублей",
            year=2020,
            is_published=False,
            is_on_main=True
        )
    
    def test_homepage_accessible(self):
        """Тест доступности главной страницы"""
        # Arrange
        url = reverse('homepage:index')
        
        # Act
        response = self.client.get(url)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'homepage/index.html')
    
    def test_homepage_shows_coins_on_main(self):
        """Тест, что главная страница показывает монеты с is_on_main=True"""
        # Arrange
        url = reverse('homepage:index')
        
        # Act
        response = self.client.get(url)
        
        # Assert
        self.assertContains(response, "Монета на главной")
        self.assertNotContains(response, "Монета не на главной")
        self.assertNotContains(response, "Неопубликованная монета")
    
    def test_homepage_shows_banknotes_on_main(self):
        """Тест, что главная страница показывает банкноты с is_on_main=True"""
        # Arrange
        banknote = Banknote.objects.create(
            name="Банкнота на главной",
            country=self.country,
            category=self.category,
            denomination="100 рублей",
            year=2020,
            is_published=True,
            is_on_main=True
        )
        url = reverse('homepage:index')
        
        # Act
        response = self.client.get(url)
        
        # Assert
        self.assertContains(response, "Банкнота на главной")
    
    def test_homepage_empty_state(self):
        """Тест главной страницы без предметов на главной"""
        # Arrange
        # Удаляем все объекты
        Coin.objects.all().delete()
        Banknote.objects.all().delete()
        url = reverse('homepage:index')
        
        # Act
        response = self.client.get(url)
        
        # Assert
        self.assertContains(response, "На главной странице пока нет коллекционных предметов.")