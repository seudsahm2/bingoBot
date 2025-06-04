# main.py

import sys
import os
import asyncio
import nest_asyncio
from telegram.ext import ApplicationBuilder, CommandHandler
from telegram.request import HTTPXRequest
from dotenv import load_dotenv
load_dotenv()

# Add project root to sys.path


from Bot.commands import start_command, join_command, card_command, create_command,mark_command  # Include create_command

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
games = {}  # You can remove this line if you're managing games inside Bot/commands.py

async def main():
    request = HTTPXRequest(connect_timeout=25.0, read_timeout=25.0) 
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).request(request).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("create", create_command))  # Register /create command
    app.add_handler(CommandHandler("join", join_command))
    app.add_handler(CommandHandler("card", card_command))
    app.add_handler(CommandHandler("mark", mark_command))

    print("Bot is running...")
    await app.run_polling()

if __name__ == "__main__":
    nest_asyncio.apply()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
