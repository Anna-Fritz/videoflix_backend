import os
from .settings import *


# Separate Test-Datenbank (z.B. SQLite in-memory oder separate Postgres DB)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'app_test',
        'USER': 'app_user',
        'PASSWORD': 'secret',
        'HOST': 'db',
        'PORT': '5432',
    }
}

# Kein echtes Email-Versenden
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Reduziere Middleware/Logging, wenn gewünscht
# Beispiel: logging während Tests weniger output
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}

# Redis: spezieller Slot für Tests
REDIS_URL = 'redis://redis:6379/2'


CACHES = {
    "default":
        {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}
}

RQ_QUEUES = {
    'default': {
        'HOST': os.environ.get("REDIS_HOST", default="redis"),
        'PORT': os.environ.get("REDIS_PORT", default=6379),
        'DB': 2,  # Tests use DB 2
        'DEFAULT_TIMEOUT': 900,
        'REDIS_CLIENT_KWARGS': {},
    },
}


# Optional: debug-Modus für Tests an (kann helfen)
DEBUG = True

# Weitere Anpassungen, die du nur für Tests möchtest
# z.B. schnellere Passwörter, Mock-Services, etc.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]