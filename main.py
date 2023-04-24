import telebot
import os
from dotenv import load_dotenv


load_dotenv()
API_KEY = os.environ["API_KEY"]

bot = telebot.TeleBot(API_KEY)


@bot.message_handler(commands=["Greet"])
def greete(message):
    bot.reply_to(message, "Hi")


@bot.message_handler(commands=["hello"])
def greete(message):
    bot.send_message(message.chat.id, "Hello")


bot.polling()
