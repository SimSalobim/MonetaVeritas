# usercollections/tests/test_views.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.core.files.uploadedfile import SimpleUploadedFile

from catalog.models import Coin, Banknote, Country, Category
from usercollections.models import UserCollectionItem

User = get_user_model()


class UserCollectionsViewsTest(TestCase):
    """Тесты для представлений пользовательских коллекций"""

    def setUp(self):
        self.client = Client()

        # Создаем пользователей
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123'
        )

        # Создаем страну и категорию
        self.country = Country.objects.create(title="Россия")
        self.category = Category.objects.create(title="Монеты")

        # Создаем монеты и банкноты
        self.coin1 = Coin.objects.create(
            name="Монета 1",
            country=self.country,
            category=self.category,
            denomination=1,
            year=2020,
            is_published=True,
            author=self.user
        )

        self.coin2 = Coin.objects.create(
            name="Монета 2",
            country=self.country,
            category=self.category,
            denomination=2,
            year=2020,
            is_published=True,
            author=self.user
        )

        self.unpublished_coin = Coin.objects.create(
            name="Неопубликованная монета",
            country=self.country,
            category=self.category,
            denomination=5,
            year=2020,
            is_published=False,
            author=self.user
        )

        self.banknote1 = Banknote.objects.create(
            name="Банкнота 1",
            country=self.country,
            category=self.category,
            denomination=100,
            year=2020,
            is_published=True,
            author=self.user
        )

        # Добавляем некоторые предметы в коллекцию пользователя
        self.collection_item1 = UserCollectionItem.objects.create(
            user=self.user,
            coin=self.coin1,
            notes="Первая монета в коллекции"
        )

        self.collection_item2 = UserCollectionItem.objects.create(
            user=self.user,
            banknote=self.banknote1,
            notes="Первая банкнота"
        )

    def test_my_collection_view_requires_login(self):
        """Тест, что просмотр коллекции требует авторизации"""
        # Arrange
        url = reverse('usercollections:my_collection')

        # Act
        response = self.client.get(url)

        # Assert
        self.assertEqual(response.status_code, 302)  # Редирект на логин
        self.assertIn('/login/', response.url)

    def test_my_collection_view_authenticated(self):
        """Тест просмотра коллекции авторизованным пользователем"""
        # Arrange
        self.client.login(username='testuser', password='testpass123')
        url = reverse('usercollections:my_collection')

        # Act
        response = self.client.get(url)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'usercollections/my_collection.html')
        self.assertContains(response, "Монета 1")
        self.assertContains(response, "Банкнота 1")
        self.assertContains(response, "Первая монета в коллекции")

    def test_add_to_collection_view_requires_login(self):
        """Тест, что добавление в коллекцию требует авторизации"""
        # Arrange
        url = reverse('usercollections:add_item', args=['coin', self.coin2.id])

        # Act
        response = self.client.get(url)

        # Assert
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_add_item_to_collection_coin(self):
        """Тест добавления монеты в коллекцию"""
        # Arrange
        self.client.login(username='testuser', password='testpass123')
        url = reverse('usercollections:add_item', args=['coin', self.coin2.id])

        # Act
        response = self.client.post(url, {
            'notes': 'Новая монета в коллекции',
            'next': reverse('usercollections:my_collection')
        })

        # Assert
        self.assertEqual(response.status_code, 302)  # Редирект
        self.assertTrue(
            UserCollectionItem.objects.filter(
                user=self.user,
                coin=self.coin2,
                notes='Новая монета в коллекции'
            ).exists()
        )

        # Проверяем сообщение об успехе
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertIn('добавлено в вашу коллекцию', str(messages_list[0]))

    def test_add_duplicate_item_to_collection(self):
        """Тест попытки добавления дубликата в коллекцию"""
        # Arrange
        self.client.login(username='testuser', password='testpass123')
        url = reverse('usercollections:add_item', args=['coin', self.coin1.id])

        # Act
        response = self.client.post(url, {
            'notes': 'Попытка добавить дубликат',
            'next': reverse('usercollections:my_collection')
        })

        # Assert
        self.assertEqual(response.status_code, 200)  # Остаемся на странице
        self.assertContains(response, "Этот предмет уже есть в вашей коллекции")

        # Проверяем, что дубликат не создался
        items_count = UserCollectionItem.objects.filter(
            user=self.user,
            coin=self.coin1
        ).count()
        self.assertEqual(items_count, 1)

    def test_add_unpublished_item_by_author(self):
        """Тест добавления неопубликованного предмета его автором"""
        # Arrange
        self.client.login(username='testuser', password='testpass123')
        url = reverse('usercollections:add_item', args=['coin', self.unpublished_coin.id])

        # Act
        response = self.client.post(url, {
            'notes': 'Моя неопубликованная монета',
            'next': reverse('usercollections:my_collection')
        })

        # Assert
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            UserCollectionItem.objects.filter(
                user=self.user,
                coin=self.unpublished_coin
            ).exists()
        )

    def test_remove_from_collection_view(self):
        """Тест удаления предмета из коллекции"""
        # Arrange
        self.client.login(username='testuser', password='testpass123')
        url = reverse('usercollections:remove_item', args=[self.collection_item1.id])

        # Act
        response = self.client.post(url)

        # Assert
        self.assertEqual(response.status_code, 302)  # Редирект
        self.assertFalse(
            UserCollectionItem.objects.filter(id=self.collection_item1.id).exists()
        )

        # Проверяем сообщение об успехе
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertIn('удалено из вашей коллекции', str(messages_list[0]))

    def test_remove_other_user_collection_item(self):
        """Тест попытки удаления чужого предмета из коллекции"""
        # Arrange
        # Создаем предмет коллекции для другого пользователя
        other_item = UserCollectionItem.objects.create(
            user=self.other_user,
            coin=self.coin2
        )

        self.client.login(username='testuser', password='testpass123')
        url = reverse('usercollections:remove_item', args=[other_item.id])

        # Act
        response = self.client.get(url)

        # Assert
        self.assertEqual(response.status_code, 403)  # Доступ запрещен

    def test_edit_collection_item(self):
        """Тест редактирования заметок в коллекции"""
        # Arrange
        self.client.login(username='testuser', password='testpass123')
        url = reverse('usercollections:edit_item', args=[self.collection_item1.id])

        # Act
        response = self.client.post(url, {
            'notes': 'Обновленные заметки о монете'
        })

        # Assert
        self.assertEqual(response.status_code, 302)  # Редирект

        # Обновляем объект из базы
        self.collection_item1.refresh_from_db()
        self.assertEqual(self.collection_item1.notes, 'Обновленные заметки о монете')

        # Проверяем сообщение об успехе
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertIn('Заметки успешно обновлены', str(messages_list[0]))

    def test_add_to_collection_catalog_view(self):
        """Тест страницы каталога для добавления в коллекцию"""
        # Arrange
        self.client.login(username='testuser', password='testpass123')
        url = reverse('usercollections:add_to_collection')

        # Act
        response = self.client.get(url)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'usercollections/add_to_collection.html')

        # Проверяем, что отображаются предметы, которых еще нет в коллекции
        self.assertContains(response, "Монета 2")  # Не в коллекции
        self.assertNotContains(response, "Монета 1")  # Уже в коллекции