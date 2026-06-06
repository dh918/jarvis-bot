import os
import telebot
import google.generativeai as genai

BOT_TOKEN = os.environ.get('BOT_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

bot = telebot.TeleBot(BOT_TOKEN)

JARVIS_PROMPT = """You are Jarvis, an advanced AI assistant. 
You are smart, helpful, and speak like a professional assistant.
Always be helpful and answer clearly."""

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Hello! I am Jarvis, your personal AI assistant. How can I help you today?")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        chat = model.start_chat()
        response = chat.send_message(JARVIS_PROMPT + "\nUser: " + message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, "Sorry, I encountered an error. Please try again.")

bot.polling()
