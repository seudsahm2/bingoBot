# telegram_bingo/urls.py

from django.urls import path
from .views import telegram_webhook

urlpatterns = [
    path('webhook/', telegram_webhook),
]
