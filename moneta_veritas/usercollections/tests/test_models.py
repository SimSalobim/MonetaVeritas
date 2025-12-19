# usercollections/tests/test_models.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from catalog.models import Coin, Banknote, Country, Category
from usercollections.models import UserCollectionItem

User = get_user_model()


class UserCollectionItemModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='collector',
            password='testpass123',
            email='collector@example.com'
        )

        self.other_user = User.objects.create_user(
            username='other_collector',
            password='testpass123'
        )

        # Создаем страну и категорию
        self.country = Country.objects.create(title="Россия")
        self.category = Category.objects.create(title="Монеты")

        self.coin = Coin.objects.create(
            name="Тестовая монета",
            country=self.country,
            category=self.category,
            denomination=1,
            year=2020,
            is_published=True,
            author=self.user
        )

        self.banknote = Banknote.objects.create(
            name="Тестовая банкнота",
            country=self.country,
            category=self.category,
            denomination=100,
            year=2020,
            is_published=True,
            author=self.user
        )

    def test_create_collection_item_with_coin(self):
        collection_item = UserCollectionItem.objects.create(
            user=self.user,
            coin=self.coin,
            notes="Моя любимая монета"
        )
        self.assertEqual(collection_item.user, self.user)
        self.assertEqual(collection_item.coin, self.coin)
        self.assertIsNone(collection_item.banknote)
        self.assertEqual(collection_item.notes, "Моя любимая монета")
        self.assertIsNotNone(collection_item.added_at)

    def test_create_collection_item_with_banknote(self):
        collection_item = UserCollectionItem.objects.create(
            user=self.user,
            banknote=self.banknote,
            notes="Редкая банкнота"
        )

        # Assert
        self.assertEqual(collection_item.user, self.user)
        self.assertEqual(collection_item.banknote, self.banknote)
        self.assertIsNone(collection_item.coin)
        self.assertEqual(collection_item.notes, "Редкая банкнота")

    def test_string_representation_coin(self):
        collection_item = UserCollectionItem.objects.create(
            user=self.user,
            coin=self.coin
        )
        string_repr = str(collection_item)
        expected = f"Монета '{self.coin.name}' в коллекции {self.user.username}"
        self.assertEqual(string_repr, expected)

    def test_string_representation_banknote(self):
        collection_item = UserCollectionItem.objects.create(
            user=self.user,
            banknote=self.banknote
        )
        string_repr = str(collection_item)
        expected = f"Банкнота '{self.banknote.name}' в коллекции {self.user.username}"
        self.assertEqual(string_repr, expected)

    def test_get_item_method_coin(self):

        collection_item = UserCollectionItem.objects.create(
            user=self.user,
            coin=self.coin
        )

        item = collection_item.get_item()
        self.assertEqual(item, self.coin)

    def test_get_item_method_banknote(self):

        collection_item = UserCollectionItem.objects.create(
            user=self.user,
            banknote=self.banknote
        )
        item = collection_item.get_item()

        self.assertEqual(item, self.banknote)

    def test_get_item_type_coin(self):
        collection_item = UserCollectionItem.objects.create(
            user=self.user,
            coin=self.coin
        )

        item_type = collection_item.get_item_type()
        self.assertEqual(item_type, 'coin')

    def test_get_item_type_banknote(self):
        collection_item = UserCollectionItem.objects.create(
            user=self.user,
            banknote=self.banknote
        )

        item_type = collection_item.get_item_type()
        self.assertEqual(item_type, 'banknote')

    def test_get_item_id_coin(self):
        collection_item = UserCollectionItem.objects.create(
            user=self.user,
            coin=self.coin
        )


        item_id = collection_item.get_item_id()
        self.assertEqual(item_id, self.coin.id)

    def test_get_item_id_banknote(self):
        collection_item = UserCollectionItem.objects.create(
            user=self.user,
            banknote=self.banknote
        )


        item_id = collection_item.get_item_id()
        self.assertEqual(item_id, self.banknote.id)

    def test_unique_constraint_user_coin(self):

        UserCollectionItem.objects.create(
            user=self.user,
            coin=self.coin
        )

        with self.assertRaises(IntegrityError):
            UserCollectionItem.objects.create(
                user=self.user,
                coin=self.coin
            )

    def test_unique_constraint_user_banknote(self):

        UserCollectionItem.objects.create(
            user=self.user,
            banknote=self.banknote
        )

        with self.assertRaises(IntegrityError):
            UserCollectionItem.objects.create(
                user=self.user,
                banknote=self.banknote
            )

    def test_different_users_can_have_same_coin(self):

        UserCollectionItem.objects.create(
            user=self.user,
            coin=self.coin
        )

        other_item = UserCollectionItem.objects.create(
            user=self.other_user,
            coin=self.coin
        )

        self.assertEqual(other_item.user, self.other_user)
        self.assertEqual(other_item.coin, self.coin)

    def test_check_constraint_not_both_null(self):

        with self.assertRaises(IntegrityError):
            UserCollectionItem.objects.create(
                user=self.user
                # coin и banknote не указаны
            )