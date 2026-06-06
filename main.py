import os
import telebot
import google.generativeai as genai

BOT_TOKEN = os.environ.get('BOT_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Hello! I am Jarvis, your personal AI assistant. How can I help you?")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        response = model.generate_content("You are Jarvis, a helpful AI assistant. User says: " + message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, "Sorry, try again!")

bot.infinity_polling()
