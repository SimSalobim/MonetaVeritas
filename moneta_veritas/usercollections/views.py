# usercollections/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import IntegrityError
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from catalog.models import Coin, Banknote
from .models import UserCollectionItem
from .forms import AddToCollectionForm, CollectionItemForm


class MyCollectionView(LoginRequiredMixin, ListView):
    """Просмотр своей коллекции"""
    template_name = 'usercollections/my_collection.html'
    context_object_name = 'collection_items'
    paginate_by = 12

    def get_queryset(self):
        return UserCollectionItem.objects.filter(
            user=self.request.user
        ).select_related('coin', 'banknote').order_by('-added_at')


class AddToCollectionView(LoginRequiredMixin, TemplateView):
    """Каталог для добавления в коллекцию"""
    template_name = 'usercollections/add_to_collection.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем предметы, которых еще нет в коллекции пользователя
        user_collection_ids = UserCollectionItem.objects.filter(
            user=self.request.user
        ).values_list('coin_id', 'banknote_id')

        coin_ids = [c[0] for c in user_collection_ids if c[0] is not None]
        banknote_ids = [b[1] for b in user_collection_ids if b[1] is not None]

        # Фильтруем опубликованные предметы и те, которых еще нет в коллекции
        coins = Coin.objects.filter(
            Q(is_published=True) |
            Q(author=self.request.user)
        ).exclude(id__in=coin_ids).order_by('-created_at')

        banknotes = Banknote.objects.filter(
            Q(is_published=True) |
            Q(author=self.request.user)
        ).exclude(id__in=banknote_ids).order_by('-created_at')

        # Пагинация для монет
        coin_page = self.request.GET.get('coin_page', 1)
        coin_paginator = Paginator(coins, 6)

        try:
            coin_list = coin_paginator.page(coin_page)
        except PageNotAnInteger:
            coin_list = coin_paginator.page(1)
        except EmptyPage:
            coin_list = coin_paginator.page(coin_paginator.num_pages)

        # Пагинация для банкнот
        banknote_page = self.request.GET.get('banknote_page', 1)
        banknote_paginator = Paginator(banknotes, 6)

        try:
            banknote_list = banknote_paginator.page(banknote_page)
        except PageNotAnInteger:
            banknote_list = banknote_paginator.page(1)
        except EmptyPage:
            banknote_list = banknote_paginator.page(banknote_paginator.num_pages)

        context['coin_list'] = coin_list
        context['coin_paginator'] = coin_paginator
        context['banknote_list'] = banknote_list
        context['banknote_paginator'] = banknote_paginator
        context['form'] = AddToCollectionForm()

        return context


def add_item_to_collection(request, item_type, item_id):
    """Добавление конкретного предмета в коллекцию"""
    if not request.user.is_authenticated:
        messages.error(request, 'Для добавления в коллекцию необходимо войти в систему.')
        return redirect('login')

    if item_type == 'coin':
        item = get_object_or_404(
            Coin.objects.filter(
                Q(is_published=True) |
                Q(author=request.user)
            ),
            pk=item_id
        )
    elif item_type == 'banknote':
        item = get_object_or_404(
            Banknote.objects.filter(
                Q(is_published=True) |
                Q(author=request.user)
            ),
            pk=item_id
        )
    else:
        messages.error(request, 'Неверный тип предмета.')
        return redirect('catalog:catalog_list')

    if request.method == 'POST':
        form = AddToCollectionForm(request.POST)
        if form.is_valid():
            try:
                collection_item = form.save(commit=False)
                collection_item.user = request.user

                if item_type == 'coin':
                    collection_item.coin = item
                else:
                    collection_item.banknote = item

                collection_item.save()
                messages.success(request, f'"{item.name}" добавлено в вашу коллекцию!')

                # Перенаправляем в зависимости от источника
                next_url = request.POST.get('next', 'usercollections:my_collection')
                return redirect(next_url)

            except IntegrityError:
                messages.warning(request, 'Этот предмет уже есть в вашей коллекции.')
    else:
        form = AddToCollectionForm()

    return render(request, 'usercollections/add_item.html', {
        'item': item,
        'item_type': item_type,
        'form': form,
        'next': request.GET.get('next', 'usercollections:my_collection')
    })


class RemoveFromCollectionView(LoginRequiredMixin, DeleteView):
    """Удаление предмета из коллекции"""
    model = UserCollectionItem
    template_name = 'usercollections/remove_from_collection.html'
    success_url = reverse_lazy('usercollections:my_collection')

    def dispatch(self, request, *args, **kwargs):
        # Проверяем, что пользователь является владельцем коллекции
        obj = self.get_object()
        if obj.user != request.user:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("У вас нет прав для удаления этого предмета из коллекции.")
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        item = self.get_object()
        item_name = item.coin.name if item.coin else item.banknote.name
        messages.success(request, f'"{item_name}" удалено из вашей коллекции.')
        return super().delete(request, *args, **kwargs)


class EditCollectionItemView(LoginRequiredMixin, UpdateView):
    """Редактирование заметок в коллекции"""
    model = UserCollectionItem
    form_class = CollectionItemForm
    template_name = 'usercollections/edit_item.html'
    success_url = reverse_lazy('usercollections:my_collection')

    def dispatch(self, request, *args, **kwargs):
        # Проверяем, что пользователь является владельцем коллекции
        obj = self.get_object()
        if obj.user != request.user:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("У вас нет прав для редактирования этого предмета.")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Заметки успешно обновлены.')
        return super().form_valid(form)