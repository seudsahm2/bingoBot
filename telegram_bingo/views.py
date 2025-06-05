# telegram_bingo/views.py
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from telegram import Update
from telegram.ext import Application, CommandHandler
import os
from dotenv import load_dotenv
import asyncio
import logging
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# Add your command handlers here
from Bot.commands import (
    start_command,
    join_command,
    card_command,
    create_command,
    mark_command
)
application.add_handler(CommandHandler("start", start_command))
application.add_handler(CommandHandler("create", create_command))
application.add_handler(CommandHandler("join", join_command))
application.add_handler(CommandHandler("card", card_command))
application.add_handler(CommandHandler("mark", mark_command))

logger = logging.getLogger(__name__)

@csrf_exempt
async def telegram_webhook(request):
    logger.info("Received webhook request")
    if request.method == 'POST':
        logger.info("Processing POST request")
        body = await request.body()
        logger.info("Request body received")
        update = Update.de_json(json.loads(body.decode('utf-8')), application.bot)
        logger.info("Update created")
        await application.process_update(update)
        logger.info("Update processed")
        return JsonResponse({'status': 'ok'})
    else:
        logger.info("Method not allowed")
        return JsonResponse({'status': 'method not allowed'}, status=405)