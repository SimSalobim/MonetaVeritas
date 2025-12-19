# usercollections/tests/test_with_mocks.py
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.messages.storage import default_storage
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware

from usercollections.views import add_item_to_collection
from catalog.models import Coin, Banknote

User = get_user_model()


class UserCollectionsViewsWithMocksTest(TestCase):
    """Тесты представлений с использованием моков"""

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_add_item_to_collection_with_mock_coin(self):
        """Тест добавления предмета в коллекцию с моками"""
        # Arrange
        # Создаем мок для Coin
        mock_coin = Mock(spec=Coin)
        mock_coin.id = 1
        mock_coin.name = "Монета-мок"
        mock_coin.is_published = True
        mock_coin.author = self.user

        # Мокаем get_object_or_404 для Coin
        with patch('usercollections.views.get_object_or_404') as mock_get_object:
            mock_get_object.return_value = mock_coin

            # Мокаем форму
            mock_form = Mock()
            mock_form.is_valid.return_value = True
            mock_form.save.return_value = Mock(
                user=None,
                coin=None,
                save=Mock()
            )

            with patch('usercollections.views.AddToCollectionForm') as mock_form_class:
                mock_form_class.return_value = mock_form

                # Создаем запрос
                request = self.factory.post('/fake-url/', {
                    'notes': 'Заметки',
                    'next': '/my-collection/'
                })
                request.user = self.user

                # Добавляем сессии и сообщения
                middleware = SessionMiddleware(lambda x: None)
                middleware.process_request(request)
                request.session.save()

                message_middleware = MessageMiddleware(lambda x: None)
                message_middleware.process_request(request)

                # Act
                response = add_item_to_collection(request, 'coin', 1)

                # Assert
                self.assertEqual(response.status_code, 302)
                mock_get_object.assert_called_once()
                mock_form_class.assert_called_once_with({'notes': 'Заметки'})
                mock_form.is_valid.assert_called_once()
                mock_form.save.assert_called_once_with(commit=False)

                # Проверяем, что сохраненный объект имеет правильные атрибуты
                saved_item = mock_form.save.return_value
                self.assertEqual(saved_item.user, self.user)
                self.assertEqual(saved_item.coin, mock_coin)
                saved_item.save.assert_called_once()

    def test_add_item_to_collection_form_invalid(self):
        """Тест добавления предмета с невалидной формой"""
        # Arrange
        # Мокаем get_object_or_404
        mock_coin = Mock()
        mock_coin.id = 1
        mock_coin.name = "Монета"
        mock_coin.is_published = True

        with patch('usercollections.views.get_object_or_404') as mock_get_object:
            mock_get_object.return_value = mock_coin

            # Мокаем невалидную форму
            mock_form = Mock()
            mock_form.is_valid.return_value = False

            with patch('usercollections.views.AddToCollectionForm') as mock_form_class:
                mock_form_class.return_value = mock_form

                # Создаем запрос
                request = self.factory.post('/fake-url/')
                request.user = self.user

                # Добавляем сессии
                middleware = SessionMiddleware(lambda x: None)
                middleware.process_request(request)
                request.session.save()

                # Act
                response = add_item_to_collection(request, 'coin', 1)

                # Assert
                self.assertEqual(response.status_code, 200)
                mock_form_class.assert_called_once()
                mock_form.is_valid.assert_called_once()

            def test_add_item_to_collection_invalid_item_type(self):
                """Тест добавления предмета с неверным типом"""
                # Arrange
                request = self.factory.get('/fake-url/')
                request.user = self.user

                # Мокаем messages
                with patch('usercollections.views.messages') as mock_messages:
                    mock_messages.error = Mock()

                    # Act
                    response = add_item_to_collection(request, 'invalid_type', 1)

                    # Assert
                    self.assertEqual(response.status_code, 302)
                    mock_messages.error.assert_called_once_with(
                        request,
                        'Неверный тип предмета.'
                    )

            def test_add_item_to_collection_integrity_error(self):
                """Тест обработки IntegrityError при добавлении дубликата"""
                # Arrange
                mock_coin = Mock()
                mock_coin.id = 1
                mock_coin.name = "Монета"
                mock_coin.is_published = True
                mock_coin.author = self.user

                with patch('usercollections.views.get_object_or_404') as mock_get_object:
                    mock_get_object.return_value = mock_coin

                    # Мокаем форму, которая вызовет IntegrityError при сохранении
                    mock_form = Mock()
                    mock_form.is_valid.return_value = True

                    # Создаем мок для сохранения, который вызывает IntegrityError
                    mock_save = Mock(side_effect=Exception('IntegrityError'))

                    mock_form.save.return_value = Mock(
                        user=None,
                        coin=None,
                        save=mock_save
                    )

                    with patch('usercollections.views.AddToCollectionForm') as mock_form_class:
                        mock_form_class.return_value = mock_form

                        # Мокаем IntegrityError
                        with patch('usercollections.views.IntegrityError', Exception):
                            # Мокаем messages
                            with patch('usercollections.views.messages') as mock_messages:
                                mock_messages.warning = Mock()

                                # Создаем запрос
                                request = self.factory.post('/fake-url/', {
                                    'notes': 'Заметки',
                                    'next': '/my-collection/'
                                })
                                request.user = self.user

                                # Добавляем сессии
                                middleware = SessionMiddleware(lambda x: None)
                                middleware.process_request(request)
                                request.session.save()

                                # Act
                                response = add_item_to_collection(request, 'coin', 1)

                                # Assert
                                self.assertEqual(response.status_code, 200)
                                mock_messages.warning.assert_called_once_with(
                                    request,
                                    'Этот предмет уже есть в вашей коллекции.'
                                )