import os
import telebot
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
import logging

# ==========================================
# 1. SETUP YOUR KEYS HERE
# ==========================================
TELEGRAM_BOT_TOKEN = "8807689593:AAHox8yJhujOm6TD8h7Y6OsnNoF8ANtnlEE"
GEMINI_API_KEY = "AQ.Ab8RN6IljqNqtd_Cx3UP89gPmKzTdxST-QJZKxYCllouJzgEDw"

# ==========================================
# 2. AUTONOMOUS RESEARCHER MODULE
# ==========================================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def deep_research(query: str) -> str:
    """
    Use this tool to search the internet for up-to-date factual information, news, or current events.
    """
    logging.info(f"Jarvis is searching the web for: {query}")
    ddgs = DDGS()
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    try:
        # We use backend="lite" to bypass basic rate limits that cause the NoneType error
        raw_results = ddgs.text(query, max_results=2, backend="lite")
        
        # If DuckDuckGo blocks us, handle it gracefully without crashing
        if raw_results is None:
            return "Web search rate-limited by DuckDuckGo. Please let the user know."
            
        results = list(raw_results)
        
        if not results:
            return "No results found on the web."
            
        compiled_research = f"RESEARCH RESULTS FOR: '{query}'\n\n"
        
        for idx, result in enumerate(results, 1):
            url = result.get('href', '')
            compiled_research += f"Source {idx}: {result.get('title')}\nURL: {url}\n"
            
            try:
                resp = requests.get(url, headers=headers, timeout=5)
                soup = BeautifulSoup(resp.text, 'html.parser')
                for element in soup(["script", "style", "nav", "footer", "header"]):
                    element.decompose()
                text = soup.get_text(separator=' ', strip=True)
                
                if len(text) > 3000:
                    text = text[:3000] + "... [Truncated]"
                compiled_research += f"Content: {text}\n\n"
            except Exception as e:
                compiled_research += f"Could not read webpage content.\n\n"
                
        logging.info("Web search complete.")
        return compiled_research
        
    except Exception as e:
        return f"Search failed with error: {str(e)}"

# ==========================================
# 3. AI & BOT INITIALIZATION
# ==========================================
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    tools=[deep_research],
    system_instruction="You are JARVIS, an advanced AI assistant. If the user asks about current events, news, or facts you don't know, automatically use the deep_research tool to find the answer on the internet. Keep responses helpful, smart, and slightly witty like Iron Man's JARVIS."
)

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
user_sessions = {}

def get_chat_session(user_id):
    if user_id not in user_sessions:
        user_sessions[user_id] = model.start_chat(enable_automatic_function_calling=True)
    return user_sessions[user_id]

# ==========================================
# 4. TELEGRAM MESSAGE HANDLERS
# ==========================================
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Good day, Sir. I am JARVIS. My systems are online, and I am now connected to the live internet. How may I assist you today?")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_id = message.from_user.id
    user_text = message.text
    bot.send_chat_action(message.chat.id, 'typing')
    
    try:
        chat_session = get_chat_session(user_id)
        response = chat_session.send_message(user_text)
        bot.reply_to(message, response.text)
    except Exception as e:
        logging.error(f"Error processing message: {e}")
        bot.reply_to(message, "My apologies, Sir. I encountered an error while processing that request.")

if __name__ == "__main__":
    print("JARVIS SYSTEM ONLINE. Waiting for messages on Telegram...")
    bot.infinity_polling()
