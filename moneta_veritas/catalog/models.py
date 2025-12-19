from django.db import models
from django.contrib.auth import get_user_model
from .validators import validate_year, validate_image_size, validate_image_extension

User = get_user_model()


class Category(models.Model):
    title = models.CharField(max_length=50, verbose_name='Название')

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'
    
    def __str__(self):
        return self.title


class Country(models.Model):
    title = models.CharField(max_length=25, verbose_name='Название')

    class Meta:
        verbose_name = 'страна'
        verbose_name_plural = 'страны'
    
    def __str__(self):
        return self.title


class Material(models.Model):
    title = models.CharField(max_length=25, verbose_name='Название')

    class Meta:
        verbose_name = 'материал'
        verbose_name_plural = 'материалы'
    
    def __str__(self):
        return self.title


class Mint(models.Model):
    title = models.CharField(max_length=25, verbose_name='Название')
    country = models.ForeignKey(Country, on_delete=models.CASCADE, verbose_name='Страна')

    class Meta:
        verbose_name = 'монетный двор'
        verbose_name_plural = 'монетные дворы'
    
    def __str__(self):
        return self.title


class CollectibleItem(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Категория')
    description = models.TextField(blank=True, verbose_name='Описание')
    country = models.ForeignKey(Country, on_delete=models.CASCADE, verbose_name='Страна')
    year = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='Год',
        validators=[validate_year]
    )
    image = models.ImageField(
        'Фото',
        upload_to='collectible_images',
        blank=True,
        validators=[validate_image_size, validate_image_extension]
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор записи',
        on_delete=models.CASCADE,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    is_published = models.BooleanField(default=True, verbose_name='Опубликовано')
    is_on_main = models.BooleanField(default=False, verbose_name='На главной странице')
    
    class Meta:
        abstract = True
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class Coin(CollectibleItem):
    denomination = models.CharField(max_length=50, verbose_name='Номинал')
    currency = models.CharField(max_length=50, default='RUB', blank=True, null=True, 
                              help_text='Например RUB, USD, EUR')
    material = models.ForeignKey(Material, on_delete=models.SET_NULL, blank=True, null=True,
                               verbose_name='Материал')
    weight = models.DecimalField(
        max_digits=8,
        decimal_places=3,
        help_text="В граммах",
        blank=True,
        null=True,
        verbose_name='Вес'
    )
    mint = models.ForeignKey(Mint, on_delete=models.SET_NULL, blank=True, null=True,
                           verbose_name='Монетный двор')
    diameter = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Диаметр (мм)',
        help_text='Диаметр в миллиметрах'
    )

    class Meta:
        verbose_name = 'монета'
        verbose_name_plural = 'монеты'
    
    def __str__(self):
        return self.name


class Banknote(CollectibleItem):
    denomination = models.CharField(max_length=50, verbose_name='Номинал')
    currency = models.CharField(max_length=50, default='RUB', blank=True, null=True,
                              verbose_name='Валюта')
    serial_number = models.CharField(max_length=50, blank=True, null=True,
                                   verbose_name='Серийный номер')
    width = models.IntegerField(blank=True, null=True, verbose_name='Ширина (мм)')
    height = models.IntegerField(blank=True, null=True, verbose_name='Высота (мм)')

    class Meta:
        verbose_name = 'банкнота'
        verbose_name_plural = 'банкноты'
    
    def __str__(self):
        return self.name

class News(models.Model):
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    content = models.TextField(verbose_name='Содержание')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='news'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    is_published = models.BooleanField(default=True, verbose_name='Опубликовано')
    image = models.ImageField(
        'Изображение',
        upload_to='news_images',
        blank=True,
        validators=[validate_image_size, validate_image_extension]
    )

    class Meta:
        verbose_name = 'новость'
        verbose_name_plural = 'Новости'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('catalog:news_detail', args=[self.pk])