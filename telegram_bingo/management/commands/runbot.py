# Bot/management/commands/runbot.py

import os
import sys
import asyncio
import nest_asyncio
from dotenv import load_dotenv
from django.core.management.base import BaseCommand  # Required for custom command

class Command(BaseCommand):
    help = 'Runs the Telegram bot'

    def handle(self, *args, **kwargs):
        load_dotenv()

        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        sys.path.append(BASE_DIR)
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Bingo.settings")

        import django
        django.setup()

        from telegram.ext import ApplicationBuilder, CommandHandler
        from telegram.request import HTTPXRequest
        from Bot.commands import start_command, join_command, card_command, create_command, mark_command

        TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

        async def main():
            request = HTTPXRequest(connect_timeout=25.0, read_timeout=25.0)
            app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).request(request).build()

            app.add_handler(CommandHandler("start", start_command))
            app.add_handler(CommandHandler("create", create_command))
            app.add_handler(CommandHandler("join", join_command))
            app.add_handler(CommandHandler("card", card_command))
            app.add_handler(CommandHandler("mark", mark_command))

            print("Bot is running...")
            await app.run_polling()

        nest_asyncio.apply()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
