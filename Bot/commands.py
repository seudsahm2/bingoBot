# commands.py




#   i was trying to fix  whn a user picks prviously picked number.
#   i fixed it but did not check it. chck that
#   i tried to implemeent a gameoveer cases but i think only the simple case is implmented
#   but even i did not check that so chck it. if works check the othr cases also. 
#   if not implmnted then implement it. refeer back the prompt chatgpt give me then ask that
#   i want to implment users can direecttly play from the private chat
#   but as the game is in group chat so i need to forward the meessages to the group automatically
#   this is becuase it is good if thee user directly plays whilee seeing thee card
#   otherwise the game will not be that fun and players frustrate going here nad there to mark and to see thir card



from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TimedOut
import random
from Bingo.game import BingoGame,bingo_sessions


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

    # Determine a reply method that works based on the type of update
    async def reply(text, parse_mode=None):
        if update.message:
            await update.message.reply_text(text, parse_mode=parse_mode)
        elif update.callback_query:
            await update.callback_query.answer()
            await update.callback_query.edit_message_text(text, parse_mode=parse_mode)
        else:
            print("⚠️ Could not reply: update.message and update.callback_query are both None.")

    # Validate the provided argument
    if len(context.args) != 1 or not context.args[0].isdigit():
        await reply("❌ Usage: /mark <number>")
        return

    number = int(context.args[0])

    # Get the active Bingo game session
    game = bingo_sessions.get(chat_id)
    if not game:
        await reply("🚫 No active game in this chat. Use /create to start one.")
        return

    # Submit the number and get result
    success, message, won = game.submit_number(user_id, number)

    await reply(message)

    # If marking was successful, update all player cards
    if success:
        for pid in game.players:
            card_text = game.get_card_text(pid)
            try:
                await safe_send_message(
                    context.bot,
                    pid,
                    f"📋 Updated Bingo Card:\n<pre>{card_text}</pre>",
                    parse_mode="HTML"
                )
            except Exception as e:
                print(f"❌ Failed to send card to user {pid}: {e}")

        # If the player won
        if won:
            winner_mention = f"<a href='tg://user?id={user_id}'>Player</a>"
            await reply(f"🎉 BINGO! {winner_mention} has won the game!", parse_mode="HTML")
        else:
            next_player = game.get_current_player()
            await reply(f"👉 It's now <a href='tg://user?id={next_player}'>player's</a> turn.", parse_mode="HTML")

    if game.game_over:
        del bingo_sessions[chat_id]
        await reply("🏁 The game is over. Use /create to start a new game.")

    
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