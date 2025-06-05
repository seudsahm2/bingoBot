from django.apps import AppConfig
import asyncio
import os
import logging

logger = logging.getLogger(__name__)

class TelegramBingoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'telegram_bingo'

    def ready(self):
        if os.environ.get('RUN_MAIN') != 'true':
            logger.debug("Skipping bot initialization due to RUN_MAIN not set")
            return
        try:
            from .views import start_bot
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            loop.run_until_complete(start_bot())
        except Exception as e:
            logger.error(f"Failed to initialize bot in apps.py: {str(e)}")