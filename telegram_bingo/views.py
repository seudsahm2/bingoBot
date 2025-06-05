import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from telegram import Update
from telegram.ext import Application, CommandHandler
import os 
from dotenv import load_dotenv

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

# Initialize bot application
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# Register bot commands
application.add_handler(CommandHandler("start", start_command))
application.add_handler(CommandHandler("create", create_command))
application.add_handler(CommandHandler("join", join_command))
application.add_handler(CommandHandler("card", card_command))
application.add_handler(CommandHandler("mark", mark_command))

# Webhook view to receive Telegram updates
@csrf_exempt
def telegram_webhook(request):
    if request.method == 'POST':
        # Parse the update sent by Telegram
        update = Update.de_json(json.loads(request.body), application.bot)
        
        # Put the update in the queue to be handled
        application.update_queue.put_nowait(update)
        
        return JsonResponse({'status': 'ok'})
    
    # If not a POST request, return 405 error
    return JsonResponse({'status': 'method not allowed'}, status=405)
