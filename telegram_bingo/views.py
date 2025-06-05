# telegram_bingo/views.py

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from telegram import Update
from telegram.ext import Application
import os 
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Initialize your bot application (ensure this is done only once)
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

@csrf_exempt
def telegram_webhook(request):
    if request.method == 'POST':
        print("Webhook received")
        update = Update.de_json(json.loads(request.body), application.bot)
        application.update_queue.put_nowait(update)
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'method not allowed'}, status=405)
