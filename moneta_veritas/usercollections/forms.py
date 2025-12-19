# usercollections/forms.py
from django import forms
from .models import UserCollectionItem


class AddToCollectionForm(forms.ModelForm):
    """Форма для добавления предмета в коллекцию"""
    class Meta:
        model = UserCollectionItem
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Добавьте заметки об этом предмете (необязательно)'
            })
        }


class CollectionItemForm(forms.ModelForm):
    """Форма для редактирования элемента коллекции"""
    class Meta:
        model = UserCollectionItem
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 4})
        }