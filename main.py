#!/usr/bin/python

# This is a simple echo bot using the decorator mechanism.
# It echoes any incoming text messages.

import telebot
from telebot import types
import markdown
import random

API_TOKEN = '7656064742:AAEd96MqdecxAd0nZcuqRJDmCWvLXbMp17U'

bot = telebot.TeleBot(API_TOKEN)

# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    with open('./help.txt', 'r', encoding='UTF-8') as help_file:
        help_text = help_file.readlines()
        help_text = ''.join(help_text)
    bot.reply_to(message, help_text, parse_mode='Markdown')

def parse_args(*args):
    '''
    /roll treshold cX nY dZ rV
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
def roll( 
    treshold: int,
    n_dices: int = 2,
    crit_value: int = 1,
    difficulty: int | None = None,
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
    if difficulty:
        if successes >= difficulty:
            result += '\n*ПРОЙДЕНО!*'
            momentum = successes - difficulty
            if momentum:
                result += f'\nСоздано Очков Импульса: {momentum}'
        else:
            result += '\n*ПРОВАЛ!*'
    if complications:
        result += f'\nПолучено затруднений: {complications}'

    result += f'\n\nПорог: {treshold}, Криты: {crit_value}, Сложность: {difficulty}\n{rolls}'
    return result


@bot.inline_handler(lambda query: len(query.query) > 0 and query.query[0].isdigit())
def query_text(inline_query):
    try:
        r = types.InlineQueryResultArticle('1', 'Roll', types.InputTextMessageContent(roll_dices_query(inline_query), parse_mode='Markdown'), description=inline_query.query)
        bot.answer_inline_query(inline_query.id, [r], cache_time=0)
    except Exception as e:
        print(e)

@bot.inline_handler(lambda query: len(query.query) > 0 and query.query == 'help')
def query_text(inline_query):
    try:
        r = types.InlineQueryResultArticle('1', 'Help', types.InputTextMessageContent('/help'), description='Get help')
        bot.answer_inline_query(inline_query.id, [r], cache_time=0)
    except Exception as e:
        print(e)

def roll_dices_query(query):
    args = query.query.split()
    result = roll(**parse_args(*args))
    #result = parse_args(*args)
    return result


@bot.message_handler(commands=['roll'])
def roll_dices(message):
    args = message.text.split()[1:]
    if not args:
        bot.reply_to(message, 'Укажи как минимум порог успеха!')
    try:
        result = roll(**parse_args(*args))
    except:
        bot.reply_to(message, 'Укажи число: порог успеха!')
        result = ""
    #result = parse_args(*args)
    bot.reply_to(message, result, parse_mode='Markdown')


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    #bot.reply_to(message, message.text)
    pass


bot.infinity_polling(allowed_updates=True)