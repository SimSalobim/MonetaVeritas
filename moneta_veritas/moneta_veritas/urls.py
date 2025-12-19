# moneta_veritas/urls.py
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from homepage import views
import mimetypes

if settings.DEBUG:
    import debug_toolbar

mimetypes.add_type("application/javascript", ".js", True)

urlpatterns = [
    path('', include('homepage.urls', namespace='homepage')),
    path('about/', include('about.urls', namespace='about')),
    path('catalog/', include('catalog.urls', namespace='catalog')),
    path('my-collection/', include('usercollections.urls', namespace='usercollections')),  # Новый путь
    path('auth/', include('django.contrib.auth.urls')),
    path('auth/signup/', views.SignUp.as_view(), name='signup'),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)