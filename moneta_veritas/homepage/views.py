from django.shortcuts import render
from catalog.models import Coin, Banknote
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic import TemplateView
from catalog.models import Coin, Banknote, News


class IndexView(TemplateView):
    template_name = 'homepage/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Берем последние 3 монеты и банкноты для главной страницы
        coins = Coin.objects.filter(is_published=True, is_on_main=True).order_by('-created_at')[:3]
        banknotes = Banknote.objects.filter(is_published=True, is_on_main=True).order_by('-created_at')[:3]

        # Берем последние 5 новостей
        news = News.objects.filter(is_published=True).order_by('-created_at')[:5]

        context['coin_list'] = coins
        context['banknote_list'] = banknotes
        context['news_list'] = news

        return context

def index(request):
    template = 'homepage/index.html'
    coin_list = Coin.objects.filter(is_published=True, is_on_main=True)[:6]
    banknote_list = Banknote.objects.filter(is_published=True, is_on_main=True)[:6]
    
    context = {
        'coin_list': coin_list,
        'banknote_list': banknote_list
    }
    return render(request, template, context)


class SignUp(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'
