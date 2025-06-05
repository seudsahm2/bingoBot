# telegram_bingo/apps.py
from django.apps import AppConfig
from telegram.ext import Application
from telegram.request import HTTPXRequest
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

class TelegramBingoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'telegram_bingo'

    def ready(self):
        # Avoid running in Django's autoreload mode (development only)
        if os.environ.get('RUN_MAIN') != 'true':
            return

        from .views import application, start_bot

        # Run the bot startup in a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(start_bot())