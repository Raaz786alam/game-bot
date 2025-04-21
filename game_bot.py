import telebot
import random
import sqlite3
from datetime import datetime, timedelta
from telebot import types

# Use your bot token here
TOKEN = "8133887481:AAEbVA8x4aGooguDm5pwaLwrriY-NJthF4s"
bot = telebot.TeleBot(TOKEN)

# /start command handler
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    item1 = types.KeyboardButton("/start")
    item2 = types.KeyboardButton("/weekly")
    item3 = types.KeyboardButton("/bounty")
    item4 = types.KeyboardButton("/xp")
    item5 = types.KeyboardButton("/top")
    item6 = types.KeyboardButton("/bet")
    markup.add(item1, item2, item3, item4, item5, item6)

    bot.send_message(message.chat.id, "Hello! Welcome to the game. Choose a command to proceed:", reply_markup=markup)

# /help command handler to show available commands
@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(
        message.chat.id,
        "Here are the available commands:\n"
        "/start - Start the game\n"
        "/weekly - Claim your weekly bonus\n"
        "/bounty - Check your bounty\n"
        "/xp - Check your XP\n"
        "/top - View the leaderboard\n"
        "/bet - Start a betting game"
    )

# Setup database connection
conn = sqlite3.connect('game_data.db', check_same_thread=False)
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    bounty INTEGER,
    vault INTEGER,
    xp INTEGER,
    level INTEGER,
    weekly_claimed BOOLEAN,
    last_login DATETIME
)''')
conn.commit()

# Function to get user data from database
def get_user_data(user_id):
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    if not user:
        cursor.execute('INSERT INTO users (user_id, bounty, vault, xp, level, weekly_claimed, last_login) VALUES (?, ?, ?, ?, ?, ?, ?)', 
                       (user_id, 10000, 2000, 0, 1, False, datetime.now()))
        conn.commit()
        return {'user_id': user_id, 'bounty': 10000, 'vault': 2000, 'xp': 0, 'level': 1, 'weekly_claimed': False, 'last_login': datetime.now()}
    return {
        'user_id': user[0],
        'username': user[1],
        'bounty': user[2],
        'vault': user[3],
        'xp': user[4],
        'level': user[5],
        'weekly_claimed': user[6],
        'last_login': user[7]
    }

# Function to update user data
def update_user_data(user_id, field, value):
    cursor.execute(f'UPDATE users SET {field} = ? WHERE user_id = ?', (value, user_id))
    conn.commit()

# /bounty command
@bot.message_handler(commands=['bounty'])
def bounty(message):
    user_id = message.from_user.id
    user = get_user_data(user_id)
    
    bot.reply_to(message, f"Current bounty: ฿{user['bounty']}\n"
                          f"Vault amount: ฿{user['vault']}/20,000,000")

# /weekly command
@bot.message_handler(commands=['weekly'])
def weekly(message):
    user_id = message.from_user.id
    user = get_user_data(user_id)
    
    if user['weekly_claimed']:
        bot.reply_to(message, "You have already claimed your weekly bounty!")
    else:
        weekly_bonus = 300000
        user['bounty'] += weekly_bonus
        update_user_data(user_id, 'bounty', user['bounty'])
        update_user_data(user_id, 'weekly_claimed', True)
        bot.reply_to(message, f"🎁 You have claimed your weekly bonus of ฿{weekly_bonus}!")

# /xp command
@bot.message_handler(commands=['xp'])
def xp(message):
    user_id = message.from_user.id
    user = get_user_data(user_id)
    
    xp_needed = 50 - user['xp']  # Example: each level needs 50 XP to level up
    bot.reply_to(message, f"You're a 🔰 Pirate Apprentice at level {user['level']} with {user['xp']} XP. "
                          f"[■■■■□□□□□□] ({xp_needed} XP needed for next level.)")

# /bet command
@bot.message_handler(commands=['bet'])
def bet(message):
    user_id = message.from_user.id
    user = get_user_data(user_id)
    
    try:
        amount = int(message.text.split()[1])
        if amount > user['bounty']:
            bot.reply_to(message, "You don't have enough bounty to place that bet!")
            return
        
        choice = message.text.split()[2].lower()
        if choice not in ['heads', 'tails']:
            bot.reply_to(message, "Please choose either 'heads' or 'tails'.")
            return
        
        # Randomly select between heads or tails
        outcome = random.choice(['heads', 'tails'])
        
        if choice == outcome:
            user['bounty'] += amount
            update_user_data(user_id, 'bounty', user['bounty'])
            bot.reply_to(message, f"The coin landed on {outcome}! You won ฿{amount}!")
        else:
            user['bounty'] -= amount
            update_user_data(user_id, 'bounty', user['bounty'])
            bot.reply_to(message, f"The coin landed on {outcome}! You lost ฿{amount}.")
    
    except IndexError:
        bot.reply_to(message, "Please enter the amount and choice (e.g. /bet 10000 heads).")
    except ValueError:
        bot.reply_to(message, "Please enter a valid amount for the bet.")


# /top command
@bot.message_handler(commands=['top'])
def top(message):
    cursor.execute('SELECT * FROM users ORDER BY bounty DESC LIMIT 10')
    top_players = cursor.fetchall()
    leaderboard = "☠️ Top Pirates On Telegram ☠️ (By Bounty)\n"
    for i, player in enumerate(top_players, 1):
        leaderboard += f"{i}. {player[1]} - ฿{player[2]} (Level {player[5]})\n"
    
    bot.reply_to(message, leaderboard)

# Start the bot
bot.polling()
