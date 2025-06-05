from django.apps import AppConfig
import asyncio
import os

class TelegramBingoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'telegram_bingo'

    def ready(self):
        if os.environ.get('RUN_MAIN') != 'true':
            return
        from .views import start_bot
        loop = asyncio.get_event_loop()
        loop.run_until_complete(start_bot())