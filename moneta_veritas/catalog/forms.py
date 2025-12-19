# catalog/forms.py
from django import forms
from .models import Coin, Banknote, News  # Добавили импорт News
from .validators import validate_year


class CoinForm(forms.ModelForm):
    """Форма для создания и редактирования монет"""

    class Meta:
        model = Coin
        fields = [
            'name',
            'category',
            'description',
            'country',
            'year',
            'image',
            'denomination',
            'currency',
            'material',
            'weight',
            'diameter',
            'mint',
            'is_published',
            'is_on_main'
        ]

    def clean_year(self):
        year = self.cleaned_data.get('year')
        if year:
            validate_year(year)
        return year


class BanknoteForm(forms.ModelForm):
    """Форма для создания и редактирования банкнот"""

    class Meta:
        model = Banknote
        fields = [
            'name',
            'category',
            'description',
            'country',
            'year',
            'image',
            'denomination',
            'currency',
            'serial_number',
            'width',
            'height',
            'is_published',
            'is_on_main'
        ]

    def clean_year(self):
        year = self.cleaned_data.get('year')
        if year:
            validate_year(year)
        return year


class NewsForm(forms.ModelForm):
    """Форма для создания и редактирования новостей"""

    class Meta:
        model = News
        fields = ['title', 'content', 'image', 'is_published']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 6}),
        }