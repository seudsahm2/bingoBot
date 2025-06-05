import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from telegram import Update
from telegram.ext import Application, CommandHandler
import os
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Initialize bot application (will be started in apps.py)
application = None

# Import command functions
from Bot.commands import (
    start_command,
    join_command,
    card_command,
    create_command,
    mark_command
)

logger = logging.getLogger(__name__)

async def start_bot():
    global application
    if application is None:
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("create", create_command))
        application.add_handler(CommandHandler("join", join_command))
        application.add_handler(CommandHandler("card", card_command))
        application.add_handler(CommandHandler("mark", mark_command))
        await application.initialize()
        await application.start()
        logger.info("Bot started successfully")

@csrf_exempt
async def telegram_webhook(request):
    logger.info("Received webhook request")
    if request.method == 'POST':
        logger.info("Processing POST request")
        try:
            # Get the request body as bytes
            body = request.body
            logger.debug(f"Request body: {body.decode('utf-8')}")
            # Parse bytes to JSON
            update = Update.de_json(json.loads(body.decode('utf-8')), application.bot)
            logger.info("Update created")
            if update is None:
                logger.error("Failed to create update from request body")
                return JsonResponse({'status': 'error', 'message': 'Invalid update'}, status=400)
            await application.process_update(update)
            logger.info("Update processed")
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        logger.info("Method not allowed")
        return JsonResponse({'status': 'method not allowed'}, status=405)