import telebot
import os
import re
import yaml
from yaml.loader import SafeLoader
from telebot import apihelper, types
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from unidecode import unidecode
from conversation import Conversation, UnexpectedResponse
apihelper.ENABLE_MIDDLEWARE = True

token = os.environ["TELEGRAM_BOT_TOKEN"]

bot = telebot.TeleBot(token, parse_mode=None) 


sessions = {}

bot_user = bot.get_me()

bot_name = bot_user.username

def build_command_url(command):
  return f"https://t.me/{bot_name}?trail={command}"


def normalize_to_command(text):
    return unidecode(text).replace(" ", "_")


def build_keyboard_options(talk_options = []):
    markup = ReplyKeyboardMarkup()

    buttons = []
    for option in talk_options:
        buttons.append(KeyboardButton(option))

    markup.add(*buttons)
    return markup

def build_inline_keyboard_options(talk_options = []):
    markup = InlineKeyboardMarkup()

    buttons = []
    for option in talk_options:
        buttons.append(InlineKeyboardButton(option, callback_data=option))

    markup.add(*buttons)
    return markup

def extract_arg(arg):
    return arg.split()[1:]

def process_script_part(section, chat_id):

    for talk in section.get("talks", []):
        bot.send_message(chat_id, talk)

    question = section.get("question", None)
    if question:
        awnsers = section.get("awnsers", None)
        if awnsers:
            markup_options = build_inline_keyboard_options(section.get("awnsers"))
            # for awnser in awnsers:
            #     question += f"\n<a href=\"{build_command_url(normalize_to_command(awnser))}\" >{awnser}</a>"
            bot.send_message(chat_id, question, reply_markup=markup_options, parse_mode="HTML")
        else:
            bot.send_message(chat_id, question)


@bot.message_handler(commands=['trail'])
def yourCommand(message):
    status = extract_arg(message.text)
    bot.send_message(message.chat.id, status)


@bot.message_handler(commands=['start'])
def start_handler(message):
    global sessions
    sender = message.json["from"]
    
    conversation = Conversation("index", {
        "user_id": sender["id"],
        "first_name": sender["first_name"]
    })

    sessions[sender["id"]] = conversation
    sections = conversation.get_sections()
    for section in sections:
        process_script_part(section, message.chat.id)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global sessions
    # if has a expected response
    sender = call.json["from"]
    conversation = sessions[sender["id"]]
    chat_id = call.json["message"]["chat"]["id"]
    try:
        if conversation.handle_response(call.data):
            bot.answer_callback_query(call.id, "Ok, understood")
            sections = conversation.get_sections()

            for section in sections:
                process_script_part(section, chat_id)
        else:
            bot.answer_callback_query(call.id, "i dont understand")
    except UnexpectedResponse as e:
        bot.send_message(chat_id, "sorry, i can't undestand it, can you type it in another way ?")
        
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    global sessions
    # get data from user
    sender = message.json["from"]
    conversation = sessions[sender["id"]]
    chat_id = message.chat.id
    try:
        acceptable_response = conversation.handle_response(message.text)
        if acceptable_response:
            sections = conversation.get_sections()

            for section in sections:
                process_script_part(section, chat_id)
        else:
            bot.send_message(chat_id, "sorry, i can't follow you")
            
    except UnexpectedResponse as e:
        bot.send_message(chat_id, "sorry, i can't undestand it, can you type it in another way ?")
        
bot.infinity_polling()