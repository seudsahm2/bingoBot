# telegram_bingo/views.py
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from telegram import Update
from telegram.ext import Application, CommandHandler
import os
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

# Get bot token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Import command functions
from Bot.commands import (
    start_command,
    join_command,
    card_command,
    create_command,
    mark_command
)

# Initialize bot application (do not start it here)
application = None

async def start_bot():
    global application
    if application is None:
        request = HTTPXRequest(connect_timeout=25.0, read_timeout=25.0)
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).request(request).build()

        # Register bot commands
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("create", create_command))
        application.add_handler(CommandHandler("join", join_command))
        application.add_handler(CommandHandler("card", card_command))
        application.add_handler(CommandHandler("mark", mark_command))

        # Start the application
        await application.initialize()
        await application.start()
        print("Bot started successfully")

# Webhook view to receive Telegram updates
@csrf_exempt
def telegram_webhook(request):
    print(f"Received request: {request.method} {request.body}")
    if request.method == 'POST':
        if application is None:
            return JsonResponse({'status': 'bot not initialized'}, status=500)
        
        try:
            # Parse the update sent by Telegram
            update = Update.de_json(json.loads(request.body), application.bot)
            
            # Process the update
            asyncio.create_task(application.process_update(update))
            
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            print(f"Error processing update: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    # If not a POST request, return 405 error
    return JsonResponse({'status': 'method not allowed'}, status=405)