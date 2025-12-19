from django.test import TestCase

from django.test import TestCase
from django.core.exceptions import ValidationError
from catalog.models import Category, Country, Material, Mint, Coin, Banknote
from django.db import IntegrityError


class CategoryModelTest(TestCase):
    """Тесты для модели Category"""
    
    def test_string_representation(self):
        """Тест строкового представления"""
        # Arrange
        category = Category(title="Монеты России")
        
        # Act
        string_repr = str(category)
        
        # Assert
        self.assertEqual(string_repr, "Монеты России")
    
    def test_verbose_name_singular(self):
        """Тест verbose_name в единственном числе"""
        # Arrange & Act
        verbose_name = Category._meta.verbose_name
        
        # Assert
        self.assertEqual(verbose_name, 'категория')
    
    def test_verbose_name_plural(self):
        """Тест verbose_name во множественном числе"""
        # Arrange & Act
        verbose_name_plural = Category._meta.verbose_name_plural
        
        # Assert
        self.assertEqual(verbose_name_plural, 'Категории')
    
    def test_title_max_length(self):
        """Тест максимальной длины поля title"""
        # Arrange
        max_length = Category._meta.get_field('title').max_length
        
        # Assert
        self.assertEqual(max_length, 50)