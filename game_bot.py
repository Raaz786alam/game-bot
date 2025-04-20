import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Game data
characters = {
    "luffy": "He's the captain of the Straw Hat Pirates and loves meat.",
    "zoro": "He's a swordsman who never knows direction.",
    "nami": "She's the navigator and loves money.",
    "sanji": "He's the cook with powerful kicks and flirts a lot.",
    "chopper": "He's a talking reindeer doctor. So cute!",
}

# Store current character and score per user
current_character = {}
user_scores = {}

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏴‍☠️ Welcome to One Piece Game Bot!\n"
        "Use /guess to play the game.\n"
        "Use /score to check your score."
    )

# /guess command
async def guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    character = random.choice(list(characters.keys()))
    current_character[user_id] = character
    clue = characters[character]
    await update.message.reply_text(f"🕵️ Guess this character:\n{clue}")

# /score command
async def score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    score = user_scores.get(user_id, 0)
    await update.message.reply_text(f"🏆 Your current score: {score}")

# Handle text guesses
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_guess = update.message.text.lower()

    if user_id in current_character:
        correct_answer = current_character[user_id]
        if user_guess == correct_answer:
            user_scores[user_id] = user_scores.get(user_id, 0) + 1
            await update.message.reply_text(
                f"✅ Correct! That's {correct_answer.capitalize()}! ☠️\n+1 Point!"
            )
            del current_character[user_id]
        else:
            await update.message.reply_text("❌ Wrong! Try again...")
    else:
        await update.message.reply_text("⚠️ Use /guess to start a new game!")

# Bot setup
app = ApplicationBuilder().token("8133887481:AAEbVA8x4aGooguDm5pwaLwrriY-NJthF4s").build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("guess", guess))
app.add_handler(CommandHandler("score", score))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()
