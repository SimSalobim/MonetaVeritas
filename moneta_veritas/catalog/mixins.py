from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404


class AuthorRequiredMixin(UserPassesTestMixin):
    """Миксин для проверки авторства"""
    
    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user
    
    def handle_no_permission(self):
        raise PermissionDenied("У вас нет прав для выполнения этого действия.")


class AuthorOrPublishedMixin:
    """Миксин для отображения только опубликованных или своих объектов"""
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_authenticated:
            # Показываем все свои объекты и опубликованные чужие
            return queryset.filter(
                models.Q(is_published=True) | 
                models.Q(author=self.request.user)
            )
        # Для неавторизованных - только опубликованные
        return queryset.filter(is_published=True)