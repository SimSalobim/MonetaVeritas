# catalog/views.py
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q

from .models import Coin, Banknote, News, Category, Country, Material, Mint
from .forms import CoinForm, BanknoteForm, NewsForm


# Главная страница каталога (упрощенная версия)
class CatalogListView(ListView):
    template_name = 'catalog/list.html'
    context_object_name = 'items'

    def get_queryset(self):
        coins = Coin.objects.filter(is_published=True, is_on_main=True)[:3]
        banknotes = Banknote.objects.filter(is_published=True, is_on_main=True)[:3]
        return {'coins': coins, 'banknotes': banknotes}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        context['coin_list'] = queryset['coins']
        context['banknote_list'] = queryset['banknotes']
        return context


# Детальное представление предмета
class CatalogDetailView(DetailView):
    template_name = 'catalog/detail.html'
    context_object_name = 'item'

    def get_object(self):
        pk = self.kwargs.get('pk')

        # Пытаемся найти монету
        coin = Coin.objects.filter(
            Q(is_published=True) |
            Q(author=self.request.user) if self.request.user.is_authenticated else Q(is_published=True),
            pk=pk
        ).first()

        if coin:
            return coin

        # Пытаемся найти банкноту
        banknote = Banknote.objects.filter(
            Q(is_published=True) |
            Q(author=self.request.user) if self.request.user.is_authenticated else Q(is_published=True),
            pk=pk
        ).first()

        if banknote:
            return banknote

        from django.http import Http404
        raise Http404("Объект не найден")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if isinstance(self.object, Coin):
            context['coin'] = self.object
        else:
            context['banknote'] = self.object
        return context


# Список монет с поиском и фильтрами
class CoinListView(ListView):
    model = Coin
    template_name = 'catalog/coin_list.html'
    context_object_name = 'coin_list'
    paginate_by = 12

    def get_queryset(self):
        queryset = super().get_queryset()

        # Базовая фильтрация по правам доступа
        if self.request.user.is_authenticated:
            queryset = queryset.filter(
                Q(is_published=True) |
                Q(author=self.request.user)
            )
        else:
            queryset = queryset.filter(is_published=True)

        # Поиск по тексту
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(denomination__icontains=search_query)
            )

        # Фильтр по стране
        country = self.request.GET.get('country')
        if country:
            queryset = queryset.filter(country_id=country)

        # Фильтр по валюте
        currency = self.request.GET.get('currency')
        if currency:
            queryset = queryset.filter(currency=currency)

        # Фильтр по году (от и до)
        year_from = self.request.GET.get('year_from')
        year_to = self.request.GET.get('year_to')
        if year_from:
            queryset = queryset.filter(year__gte=year_from)
        if year_to:
            queryset = queryset.filter(year__lte=year_to)

        # Фильтр по материалу
        material = self.request.GET.get('material')
        if material:
            queryset = queryset.filter(material_id=material)

        # Фильтр по монетному двору
        mint = self.request.GET.get('mint')
        if mint:
            queryset = queryset.filter(mint_id=mint)

        # Фильтр по диаметру
        diameter_from = self.request.GET.get('diameter_from')
        diameter_to = self.request.GET.get('diameter_to')
        if diameter_from:
            queryset = queryset.filter(diameter__gte=diameter_from)
        if diameter_to:
            queryset = queryset.filter(diameter__lte=diameter_to)

        # Сортировка
        sort_by = self.request.GET.get('sort', '-created_at')
        if sort_by in ['-created_at', 'created_at', 'name', '-name', 'year', '-year', 'denomination']:
            queryset = queryset.order_by(sort_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем данные для фильтров
        context['countries'] = Country.objects.all()
        context['materials'] = Material.objects.all()
        context['mints'] = Mint.objects.all()

        # Сохраняем параметры поиска
        context['search_params'] = {
            'q': self.request.GET.get('q', ''),
            'country': self.request.GET.get('country', ''),
            'currency': self.request.GET.get('currency', ''),
            'year_from': self.request.GET.get('year_from', ''),
            'year_to': self.request.GET.get('year_to', ''),
            'material': self.request.GET.get('material', ''),
            'mint': self.request.GET.get('mint', ''),
            'diameter_from': self.request.GET.get('diameter_from', ''),
            'diameter_to': self.request.GET.get('diameter_to', ''),
            'sort': self.request.GET.get('sort', '-created_at'),
        }
        return context


# Список банкнот с поиском и фильтрами
class BanknoteListView(ListView):
    model = Banknote
    template_name = 'catalog/banknote_list.html'
    context_object_name = 'banknote_list'
    paginate_by = 12

    def get_queryset(self):
        queryset = super().get_queryset()

        # Базовая фильтрация по правам доступа
        if self.request.user.is_authenticated:
            queryset = queryset.filter(
                Q(is_published=True) |
                Q(author=self.request.user)
            )
        else:
            queryset = queryset.filter(is_published=True)

        # Поиск по тексту
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(denomination__icontains=search_query) |
                Q(serial_number__icontains=search_query)
            )

        # Фильтр по стране
        country = self.request.GET.get('country')
        if country:
            queryset = queryset.filter(country_id=country)

        # Фильтр по валюте
        currency = self.request.GET.get('currency')
        if currency:
            queryset = queryset.filter(currency=currency)

        # Фильтр по году (от и до)
        year_from = self.request.GET.get('year_from')
        year_to = self.request.GET.get('year_to')
        if year_from:
            queryset = queryset.filter(year__gte=year_from)
        if year_to:
            queryset = queryset.filter(year__lte=year_to)

        # Фильтр по размеру (ширина)
        width_from = self.request.GET.get('width_from')
        width_to = self.request.GET.get('width_to')
        if width_from:
            queryset = queryset.filter(width__gte=width_from)
        if width_to:
            queryset = queryset.filter(width__lte=width_to)

        # Фильтр по размеру (высота)
        height_from = self.request.GET.get('height_from')
        height_to = self.request.GET.get('height_to')
        if height_from:
            queryset = queryset.filter(height__gte=height_from)
        if height_to:
            queryset = queryset.filter(height__lte=height_to)

        # Сортировка
        sort_by = self.request.GET.get('sort', '-created_at')
        if sort_by in ['-created_at', 'created_at', 'name', '-name', 'year', '-year', 'denomination']:
            queryset = queryset.order_by(sort_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['countries'] = Country.objects.all()

        context['search_params'] = {
            'q': self.request.GET.get('q', ''),
            'country': self.request.GET.get('country', ''),
            'currency': self.request.GET.get('currency', ''),
            'year_from': self.request.GET.get('year_from', ''),
            'year_to': self.request.GET.get('year_to', ''),
            'width_from': self.request.GET.get('width_from', ''),
            'width_to': self.request.GET.get('width_to', ''),
            'height_from': self.request.GET.get('height_from', ''),
            'height_to': self.request.GET.get('height_to', ''),
            'sort': self.request.GET.get('sort', '-created_at'),
        }
        return context


# Создание монеты
class CoinCreateView(LoginRequiredMixin, CreateView):
    model = Coin
    form_class = CoinForm
    template_name = 'catalog/coin_form.html'
    success_url = reverse_lazy('catalog:coin_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


# Создание банкноты
class BanknoteCreateView(LoginRequiredMixin, CreateView):
    model = Banknote
    form_class = BanknoteForm
    template_name = 'catalog/banknote_form.html'
    success_url = reverse_lazy('catalog:banknote_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


# Редактирование монеты
class CoinUpdateView(LoginRequiredMixin, UpdateView):
    model = Coin
    form_class = CoinForm
    template_name = 'catalog/coin_form.html'
    success_url = reverse_lazy('catalog:coin_list')

    def dispatch(self, request, *args, **kwargs):
        # Проверяем, что пользователь является автором
        obj = self.get_object()
        if obj.author != request.user:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("У вас нет прав для редактирования этого объекта")
        return super().dispatch(request, *args, **kwargs)


# Редактирование банкноты
class BanknoteUpdateView(LoginRequiredMixin, UpdateView):
    model = Banknote
    form_class = BanknoteForm
    template_name = 'catalog/banknote_form.html'
    success_url = reverse_lazy('catalog:banknote_list')

    def dispatch(self, request, *args, **kwargs):
        # Проверяем, что пользователь является автором
        obj = self.get_object()
        if obj.author != request.user:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("У вас нет прав для редактирования этого объекта")
        return super().dispatch(request, *args, **kwargs)


# Удаление монеты
class CoinDeleteView(LoginRequiredMixin, DeleteView):
    model = Coin
    template_name = 'catalog/coin_confirm_delete.html'
    success_url = reverse_lazy('catalog:coin_list')

    def dispatch(self, request, *args, **kwargs):
        # Проверяем, что пользователь является автором
        obj = self.get_object()
        if obj.author != request.user:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("У вас нет прав для удаления этого объекта")
        return super().dispatch(request, *args, **kwargs)


# Удаление банкноты
class BanknoteDeleteView(LoginRequiredMixin, DeleteView):
    model = Banknote
    template_name = 'catalog/banknote_confirm_delete.html'
    success_url = reverse_lazy('catalog:banknote_list')

    def dispatch(self, request, *args, **kwargs):
        # Проверяем, что пользователь является автором
        obj = self.get_object()
        if obj.author != request.user:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("У вас нет прав для удаления этого объекта")
        return super().dispatch(request, *args, **kwargs)


# Список новостей
class NewsListView(ListView):
    model = News
    template_name = 'catalog/news_list.html'
    context_object_name = 'news_list'
    paginate_by = 10

    def get_queryset(self):
        queryset = News.objects.filter(is_published=True)

        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query)
            )

        return queryset.order_by('-created_at')


# Детальная страница новости
class NewsDetailView(DetailView):
    model = News
    template_name = 'catalog/news_detail.html'
    context_object_name = 'news'

    def get_queryset(self):
        return News.objects.filter(is_published=True)


# Добавление новости
class NewsCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = News
    form_class = NewsForm
    template_name = 'catalog/news_form.html'
    success_url = reverse_lazy('catalog:news_list')

    def test_func(self):
        # Только staff пользователи могут добавлять новости
        return self.request.user.is_staff

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


# Редактирование новости
class NewsUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = News
    form_class = NewsForm
    template_name = 'catalog/news_form.html'
    success_url = reverse_lazy('catalog:news_list')

    def test_func(self):
        # Только staff пользователи или автор могут редактировать
        obj = self.get_object()
        return self.request.user.is_staff or obj.author == self.request.user


# Удаление новости
class NewsDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = News
    template_name = 'catalog/news_confirm_delete.html'
    success_url = reverse_lazy('catalog:news_list')

    def test_func(self):
        # Только staff пользователи могут удалять новости
        return self.request.user.is_staff