import flask
from flask import Flask, request
import telebot
from telebot import apihelper, types, TeleBot
import urllib3
import logging
import os
import random

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

proxy_url = "http://proxy.server:3128"

apihelper.proxy = {'http': proxy_url, 'https': proxy_url}

secret = os.getenv("SECRET")

API_TOKEN = os.getenv("API_TOKEN")

bot = TeleBot(API_TOKEN, threaded=False)
bot.set_webhook(url="https://Amodion.pythonanywhere.com/{}".format(secret), max_connections=1)


app = Flask(__name__)

# Загрузка текста help
with open('/home/Amodion/dunebotwebhook/help.txt', 'r', encoding='UTF-8') as help_file:
    help_text = help_file.readlines()
    help_text = ''.join(help_text)

# Обработка обращенй к боту
@app.route('/{}'.format(secret), methods=["POST"])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)


# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, help_text, parse_mode='Markdown')

# Обработка команды для броска в строке
@bot.inline_handler(lambda query: len(query.query) > 0 and query.query[0].isdigit())
def query_text(inline_query):
    try:
        description = description_from_query(inline_query)
        r = types.InlineQueryResultArticle('1', 'Roll', types.InputTextMessageContent(roll_dices_query(inline_query), parse_mode='Markdown'), description=description)
        bot.answer_inline_query(inline_query.id, [r], cache_time=0)
    except Exception as e:
        print(e)

# Обработка команды help в строке
@bot.inline_handler(lambda query: len(query.query) > 0 and query.query.lower() == 'help')
def query_text_help(inline_query):
    try:
        r = types.InlineQueryResultArticle('1', 'Help', types.InputTextMessageContent(help_text, parse_mode='Markdown'), description='Get help')
        bot.answer_inline_query(inline_query.id, [r], cache_time=0)
    except Exception as e:
        print(e)

# Запусает бросок кубиков для запроса в строке
def roll_dices_query(query):
    args = query.query.split()
    result = roll(**parse_args(*args))
    return result

# Создание подсказок при создании запроса
def description_from_query(query):
    args = query.query.split()
    d = parse_args(*args)

    description = f'Порог успеха: {d["treshold"]}; '
    if 'crit_value' in d.keys():
        description += f'Криты на: {d["crit_value"]}; '
    else:
        description += 'c - криты; '
    
    if 'n_dices' in d.keys():
        description += f'Число кубиков: {d["n_dices"]}; '
    else:
        description += 'n - число кубиков; '
    
    if 'difficulty' in d.keys():
        description += f'Сложность: {d["difficulty"]}; '
    else:
        description += 'd - Сложность; '
    
    if 'complications_range' in d.keys():
        description += f'Затруднения на: {d["complications_range"]}; '
    else:
        description += 'r - затруднения; '

    if 'use_determination' in d.keys():
        description += f'Потрачена Решимость'
    else:
        description += f'! - Решимость'

    return description

# Обрабатывает обычную команду /roll
@bot.message_handler(commands=['roll'])
def roll_dices(message):
    print('Roll command get text: ', message.text)
    if message.text:
        args = message.text.split()[1:]
        result = roll(**parse_args(*args))
        bot.reply_to(message, result, parse_mode='Markdown')

# Парсит аргемнты для броска кубиков. Валидация тут? Pydantic?
def parse_args(*args):
    '''
    /roll treshold cX nY dZ rV ! - расшифровка в help.txt
    '''
    d = {'treshold': int(args[0])}
    for arg in args[1:]:
        if 'c' in arg:
            d['crit_value'] = int(arg[1:])
        if 'n' in arg:
            d['n_dices'] = int(arg[1:])
        if 'd' in arg:
            d['difficulty'] = int(arg[1:])
        if 'r' in arg:
            d['complications_range'] = int(arg[1:])
        if '!' in arg:
            d['use_determination'] = True
    return d

# TODO: Сделать Roll классом
# Делает бросок и возвращает сообщение с резульататми
def roll(
    treshold: int,
    n_dices: int = 2,
    crit_value: int = 1,
    difficulty = None, # : int | None
    complications_range: int = 20,
    use_determination: bool = False
    ) -> str:
    if use_determination:
        rolls = [1] + [random.randint(1, 20) for _ in range(n_dices - 1)]
    else:
        rolls = [random.randint(1, 20) for _ in range(n_dices)]
    successes = 0
    complications = 0
    for result in rolls:
        if result <= crit_value:
            successes += 2
        elif result <= treshold:
            successes += 1
        elif result >= complications_range:
            complications += 1
    result = f'*Успехов: {successes}!*'
    if type(difficulty) is int:
        if successes >= difficulty:
            result += '\n*ПРОЙДЕНО!*'
            momentum = successes - difficulty
            if momentum:
                result += f'\nСоздано Очков Импульса: {momentum}'
        else:
            result += '\n*ПРОВАЛ!*'
            if difficulty >= 3:
                result += '\nПолучи 1 Очко Развития!'
    if complications:
        result += f'\nПолучено затруднений: {complications}'

    result += f'\n\nПорог: {treshold}, Криты на: {crit_value}'
    if type(difficulty) is int:
        result += f', Сложность: {difficulty}'
    result += f'\nБросок: [{rolls}]'
    return result

