from django.conf.urls import patterns, url

from .views import show_rule

urlpatterns = [
    url(r'(?P<url>[a-zA-Z0-9_-]+)', show_rule),
]
