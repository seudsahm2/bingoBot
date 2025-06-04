# commands.py

from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TimedOut
import random
from bingo.game import BingoGame,bingo_sessions


# Command: /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to Bingo Bot!\n\n"
        "Use /create in a group chat to start a new game.\n"
        "Use /join to get your card after game is created.\n"
        "Use /card to see your Bingo card anytime."
    )

# Command: /create (group-only)
async def create_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat

    if chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("❌ /create must be used in a group chat.")
        return

    chat_id = chat.id

    if chat_id in bingo_sessions:
        await update.message.reply_text("⚠️ A Bingo game is already active in this group.")
        return

    bingo_sessions[chat_id] = BingoGame()
    await update.message.reply_text("🎉 New Bingo game created for this group!\nAsk your friends to /join!")

# Command: /join (group-only)
async def join_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    # Must be a group
    if update.effective_chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("You must use this command in a group to join a game.")
        return

    # Create a session if not exists
    if chat_id not in bingo_sessions:
        await update.message.reply_text("No game session found in this group. Use /create to start one.")
        return

    game = bingo_sessions[chat_id]
    joined = game.add_player(user_id)

    if joined:
        await update.message.reply_text(f"{update.effective_user.first_name} joined the game!")
        # Send the card privately
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"<pre>{game.get_card_text(user_id)}</pre>",
                parse_mode="HTML"
            )
        except:
            await update.message.reply_text(
                f"{update.effective_user.first_name}, I couldn't send you your card in private. Please start me in private and try again."
            )
    else:
        await update.message.reply_text("You already joined the game. Use /card in private chat to see your card.")

# Command: /card (show user's card from group game)
async def card_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        await update.message.reply_text("Use /card in private chat to see your card.")
        return

    user_id = update.effective_user.id
    found = False
    for game in bingo_sessions.values():
        if user_id in game.players:
            await update.message.reply_text(
                f"<pre>{game.get_card_text(user_id)}</pre>", parse_mode="HTML"
            )
            found = True
            break

    if not found:
        await update.message.reply_text("You haven't joined any game yet.")


async def mark_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    # Check if number argument is provided
    if len(context.args) != 1 or not context.args[0].isdigit():
        await update.message.reply_text("Usage: /mark <number>")
        return

    number = int(context.args[0])

    # Retrieve the game session for this chat
    game = bingo_sessions.get(chat_id)
    if not game:
        await update.message.reply_text("No active game in this chat. Use /create to start.")
        return

    success, message, won = game.submit_number(user_id, number)
    await update.message.reply_text(message)

    if success:
        # Show updated cards for all players privately (You must implement sending cards privately)
        for pid in game.players:
            card_text = game.get_card_text(pid)
            try:
                await safe_send_message(context.bot,pid, f"Updated Bingo Card:\n<pre>{card_text}</pre>", parse_mode="HTML")
            except Exception as e:
                print(f"Failed to send card to user {pid}: {e}")

        # Announce who's turn is next in the group
        if won:
            winner_mention = f"<a href='tg://user?id={user_id}'>Player</a>"
            await update.message.reply_text(f"BINGO! {winner_mention} has won the game! 🎉", parse_mode="HTML")
            # Optionally end the game or reset here
        else:
            next_player = game.get_current_player()
            await update.message.reply_text(f"It's now <a href='tg://user?id={next_player}'>player's</a> turn.", parse_mode="HTML")
            
    
async def safe_send_message(bot, chat_id, text, **kwargs):
    max_retries = 3  # number of retries
    for attempt in range(max_retries):
        try:
            await bot.send_message(chat_id, text, **kwargs)  # try sending message
            break  # if successful, exit the loop
        except TimedOut:
            if attempt < max_retries - 1:
                await asyncio.sleep(2)  # wait 2 seconds before retrying
            else:
                print(f"Failed to send message to user {chat_id} after {max_retries} attempts due to timeout.")