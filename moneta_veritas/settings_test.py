# moneta_veritas/settings_test.py
"""
Настройки для запуска тестов
"""
import tempfile
from .settings import *

# Используем базу в памяти для скорости
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Отключаем debug toolbar
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'debug_toolbar']
MIDDLEWARE = [mw for mw in MIDDLEWARE if mw != 'debug_toolbar.middleware.DebugToolbarMiddleware']

# Ускоряем тесты
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Отключаем отправку почты
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Используем временную папку для медиа файлов
MEDIA_ROOT = tempfile.mkdtemp()

# Отключаем валидацию паролей для тестов
AUTH_PASSWORD_VALIDATORS = []

# Уменьшаем время выполнения тестов
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Отключаем кэширование для тестов
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}