from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.CatalogListView.as_view(), name='catalog_list'),
    path('<int:pk>/', views.CatalogDetailView.as_view(), name='catalog_detail'),
    
    # Монеты
    path('coins/', views.CoinListView.as_view(), name='coin_list'),
    path('coins/create/', views.CoinCreateView.as_view(), name='coin_create'),
    path('coins/<int:pk>/edit/', views.CoinUpdateView.as_view(), name='coin_edit'),
    path('coins/<int:pk>/delete/', views.CoinDeleteView.as_view(), name='coin_delete'),
    
    # Банкноты
    path('banknotes/', views.BanknoteListView.as_view(), name='banknote_list'),
    path('banknotes/create/', views.BanknoteCreateView.as_view(), name='banknote_create'),
    path('banknotes/<int:pk>/edit/', views.BanknoteUpdateView.as_view(), name='banknote_edit'),
    path('banknotes/<int:pk>/delete/', views.BanknoteDeleteView.as_view(), name='banknote_delete'),
    path('news/', views.NewsListView.as_view(), name='news_list'),
    path('news/<int:pk>/', views.NewsDetailView.as_view(), name='news_detail'),
    path('news/create/', views.NewsCreateView.as_view(), name='news_create'),
    path('news/<int:pk>/edit/', views.NewsUpdateView.as_view(), name='news_edit'),
    path('news/<int:pk>/delete/', views.NewsDeleteView.as_view(), name='news_delete'),
]