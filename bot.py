import os
import telebot
import threading
from flask import Flask
from modules import checker, myqueues
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

TOKEN = os.getenv("BOT_API_KEY")
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# Create Flask app instance for the web service
app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to the YouTube Downloader Web Service!"

@app.route('/status')
def status():
    return "Bot is running and ready to serve requests."

# Start Flask server on a separate thread
def run_flask():
    app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)

# Start the bot and Flask in separate threads
def run_telegram_bot():
    bot.infinity_polling()

# Start both Flask and Telegram Bot services
if __name__ == "__main__":
    # Start Flask server in its own thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Start Telegram bot in its own thread
    bot_thread = threading.Thread(target=run_telegram_bot)
    bot_thread.daemon = True
    bot_thread.start()

    print("TelegramYTDLBot is running..\n")
    print("Web service is running at http://localhost:8080\n")

    # Keep the main thread alive
    flask_thread.join()
    bot_thread.join()

# Command handler for "/start"
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message, "Hello, I'm a <b>Simple Youtube Downloader!👋</b>\n\nTo get started, just type the /help command.")

# Command handler for "/help"
@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(
        message,
        """
        <b>Just send your youtube link and select the video quality.</b> 😉
  <i>
  Developer: @dev00111
  Source: <a href="https://github.com/hansanaD/TelegramYTDLBot">TelegramYTDLBot</a></i>
        """, disable_web_page_preview=True)

# Message handler to check for links
@bot.message_handler(func=lambda m: True)
def link_check(message):
    checker.linkCheck(bot=bot, message=message)

# Callback handler for video download quality selection
@bot.callback_query_handler(func=lambda call: [call.data == item for item in checker.showList])
def callback_query(call):
    data = call.data.split("#")
    receivedData = data[0]
    videoURL = data[1]
    
    bot.answer_callback_query(call.id, f"Selected {receivedData} to download.")
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

    myqueues.download_queue.put((call.message, videoURL, receivedData))
    queue_position = myqueues.download_queue.qsize()

    if queue_position == 0:
        bot.send_message(call.message.chat.id, f"Download has been added to the queue.")
    else:
        bot.send_message(call.message.chat.id, f"Download has been added to the queue at #{queue_position}.")

# Start download worker thread
download_thread = threading.Thread(target=myqueues.download_worker, args=(bot, myqueues.download_queue))
download_thread.daemon = True
download_thread.start()

print("TelegramYTDLBot is running..\n")
bot.infinity_polling()
