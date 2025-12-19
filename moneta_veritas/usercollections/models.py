# usercollections/models.py
from django.db import models
from django.contrib.auth import get_user_model
from catalog.models import Coin, Banknote

User = get_user_model()


class UserCollectionItem(models.Model):
    """Элемент коллекции пользователя"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='collection_items'
    )
    coin = models.ForeignKey(
        Coin,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Монета'
    )
    banknote = models.ForeignKey(
        Banknote,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Банкнота'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='Заметки',
        help_text='Личные заметки об этом предмете'
    )
    added_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления'
    )

    class Meta:
        verbose_name = 'элемент коллекции'
        verbose_name_plural = 'элементы коллекции'
        ordering = ['-added_at']
        constraints = [
            models.CheckConstraint(
                check=models.Q(coin__isnull=False) | models.Q(banknote__isnull=False),
                name='not_both_null'
            ),
            models.UniqueConstraint(
                fields=['user', 'coin'],
                condition=models.Q(coin__isnull=False),
                name='unique_user_coin'
            ),
            models.UniqueConstraint(
                fields=['user', 'banknote'],
                condition=models.Q(banknote__isnull=False),
                name='unique_user_banknote'
            )
        ]

    def __str__(self):
        if self.coin:
            return f"Монета '{self.coin.name}' в коллекции {self.user.username}"
        return f"Банкнота '{self.banknote.name}' в коллекции {self.user.username}"

    def get_item(self):
        """Возвращает связанный предмет (монету или банкноту)"""
        return self.coin or self.banknote

    def get_item_type(self):
        """Возвращает тип предмета"""
        return 'coin' if self.coin else 'banknote'

    def get_item_id(self):
        """Возвращает ID предмета"""
        return self.coin.id if self.coin else self.banknote.id