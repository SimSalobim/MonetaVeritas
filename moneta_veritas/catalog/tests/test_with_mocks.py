# catalog/tests/test_with_mocks.py
from unittest.mock import Mock, patch
from django.test import TestCase
from django.http import Http404
from catalog.views import catalog_detail


class CatalogDetailViewWithMocksTest(TestCase):
    """Тесты представления catalog_detail с использованием моков"""
    
    def test_catalog_detail_with_mock_coin(self):
        """Тест с моком для Coin.objects.filter"""
        # Arrange
        mock_coin = Mock()
        mock_coin.pk = 1
        mock_coin.name = "Монета-мок"
        mock_coin.is_published = True
        
        # Создаем мок для Coin.objects.filter().first()
        mock_filter = Mock()
        mock_filter.first = Mock(return_value=mock_coin)
        
        # Act & Assert
        with patch('catalog.views.Coin.objects.filter', return_value=mock_filter):
            # Мокаем также Banknote.objects.filter чтобы вернуть None
            with patch('catalog.views.Banknote.objects.filter', return_value=Mock(first=Mock(return_value=None))):
                # Мокаем render
                mock_render = Mock(return_value=Mock(status_code=200))
                with patch('catalog.views.render', mock_render):
                    # Создаем мок request
                    mock_request = Mock()
                    
                    # Вызываем представление
                    response = catalog_detail(mock_request, pk=1)
                    
                    # Проверяем, что render был вызван с правильными аргументами
                    mock_render.assert_called_once()
                    args, kwargs = mock_render.call_args
                    self.assertEqual(kwargs['template'], 'catalog/detail.html')
                    self.assertEqual(kwargs['context']['coin'], mock_coin)
    
    def test_catalog_detail_with_mock_404(self):
        """Тест 404 ошибки с моками"""
        # Arrange
        # Мокаем Coin.objects.filter().first() чтобы вернуть None
        mock_filter_coin = Mock()
        mock_filter_coin.first = Mock(return_value=None)
        
        # Мокаем Banknote.objects.filter().first() чтобы вернуть None
        mock_filter_banknote = Mock()
        mock_filter_banknote.first = Mock(return_value=None)
        
        # Act & Assert
        with patch('catalog.views.Coin.objects.filter', return_value=mock_filter_coin):
            with patch('catalog.views.Banknote.objects.filter', return_value=mock_filter_banknote):
                mock_request = Mock()
                
                # Проверяем, что вызывается Http404
                with self.assertRaises(Http404):
                    catalog_detail(mock_request, pk=999)