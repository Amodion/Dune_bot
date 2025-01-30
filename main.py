#!/usr/bin/python

# This is a simple echo bot using the decorator mechanism.
# It echoes any incoming text messages.

import telebot
import random

API_TOKEN = '7656064742:AAEd96MqdecxAd0nZcuqRJDmCWvLXbMp17U'

bot = telebot.TeleBot(API_TOKEN)


# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, """\
Hi there, I am DuneBot.
I am here to echo your kind words back to you. Just say anything nice and I'll say the exact same thing to you!\
""")

def roll(treshold: int, n_dices: int = 2, crit_value: int = 1, difficulty: int | None = None) -> str:
    rolls = [random.randint(1, 20) for _ in range(n_dices)]
    successes = 0
    for result in rolls:
        if result <= crit_value:
            successes += 2
        elif result <= treshold:
            successes += 1
    result = f'*Успехов: {successes}!* ({rolls})'
    if difficulty:
        if successes >= difficulty:
            result += '\n*Првоерка пройдена!*'
            momentum = successes - difficulty
            if momentum:
                result += f' Создано Очков Импульса: {momentum}'
        else:
            result += '\n*Првоерка не пройдена!*'
    return result


@bot.message_handler(commands=['roll'])
def roll_dices(message):
    args = message.text.split()[1:]
    if not args:
        bot.send_message(message.from_user.id, 'Укажи как минимум порог успеха!')
    result = roll(*map(int, args))
    bot.reply_to(message, result, parse_mode='Markdown')


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.reply_to(message, message.text)


bot.infinity_polling()