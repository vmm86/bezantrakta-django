"""
WSGI config for `bezantrakta` project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""
import os

from django.core.wsgi import get_wsgi_application

# Fix django closing connection to MemCachier after every request (#11331)
# from django.core.cache.backends.memcached import BaseMemcachedCache
# BaseMemcachedCache.close = lambda self, **kwargs: None

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

application = get_wsgi_application()
