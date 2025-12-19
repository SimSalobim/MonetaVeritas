# catalog/tests/test_views.py
from django.test import TestCase, Client
from django.urls import reverse
from catalog.models import Coin, Banknote, Country, Category


class CatalogViewTest(TestCase):
    """Тесты для представлений каталога"""
    
    def setUp(self):
        self.client = Client()
        self.country = Country.objects.create(title="Россия")
        self.category = Category.objects.create(title="Тестовая категория")
        
        # Создаем тестовые данные
        self.published_coin = Coin.objects.create(
            name="Опубликованная монета",
            country=self.country,
            category=self.category,
            denomination="1 рубль",
            year=2020,
            is_published=True
        )
        
        self.unpublished_coin = Coin.objects.create(
            name="Неопубликованная монета",
            country=self.country,
            category=self.category,
            denomination="2 рубля",
            year=2020,
            is_published=False
        )
        
        self.published_banknote = Banknote.objects.create(
            name="Опубликованная банкнота",
            country=self.country,
            category=self.category,
            denomination="100 рублей",
            year=2020,
            is_published=True
        )
    
    def test_catalog_list_view(self):
        """Тест представления списка каталога"""
        # Arrange
        url = reverse('catalog:catalog_list')
        
        # Act
        response = self.client.get(url)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/list.html')
        self.assertContains(response, "Опубликованная монета")
        self.assertContains(response, "Опубликованная банкнота")
        self.assertNotContains(response, "Неопубликованная монета")
    
    def test_catalog_detail_view_coin(self):
        """Тест детального представления монеты"""
        # Arrange
        url = reverse('catalog:catalog_detail', args=[self.published_coin.pk])
        
        # Act
        response = self.client.get(url)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/detail.html')
        self.assertContains(response, "Опубликованная монета")
        self.assertContains(response, "1 рубль")
    
    def test_catalog_detail_view_banknote(self):
        """Тест детального представления банкноты"""
        # Arrange
        url = reverse('catalog:catalog_detail', args=[self.published_banknote.pk])
        
        # Act
        response = self.client.get(url)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/detail.html')
        self.assertContains(response, "Опубликованная банкнота")
        self.assertContains(response, "100 рублей")
    
    def test_catalog_detail_view_unpublished_item(self):
        """Тест детального представления неопубликованного предмета"""
        # Arrange
        url = reverse('catalog:catalog_detail', args=[self.unpublished_coin.pk])
        
        # Act
        response = self.client.get(url)
        
        # Assert
        self.assertEqual(response.status_code, 404)
    
    def test_catalog_detail_view_nonexistent_item(self):
        """Тест детального представления несуществующего предмета"""
        # Arrange
        url = reverse('catalog:catalog_detail', args=[999])
        
        # Act
        response = self.client.get(url)
        
        # Assert
        self.assertEqual(response.status_code, 404)