# telegram_bingo/apps.py
from django.apps import AppConfig
import asyncio
from .views import application

class TelegramBingoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'telegram_bingo'

    def ready(self):
        # Start Telegram bot async
        asyncio.ensure_future(start_bot())

async def start_bot():
    await application.initialize()
    await application.start()
    await application.updater.start()
