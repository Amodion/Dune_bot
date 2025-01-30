#!/usr/bin/python

# This is a simple echo bot using the decorator mechanism.
# It echoes any incoming text messages.

import telebot
import markdown
import random

API_TOKEN = '7656064742:AAEd96MqdecxAd0nZcuqRJDmCWvLXbMp17U'

bot = telebot.TeleBot(API_TOKEN)

help_text = '''
Привет! Я ДюнаБот, буду бросать для тебя кубики!

Я создан для игры только по системе Дюна: Приключения в Империи!
Это 2d20 система, так что будем бросать только d20! С правилами можешь ознакомится в Основной Книге Правил!

Как я работаю:

Основная команда всегда начинается на */roll T*
где **T** - число, обычно от 8 до 16, порог успеха.
Просто напиши так и я скажу, сколько ты получил успехов!
Это обязательный минимум, но можно последовательно добавить еще параметры.
Полный синтаксис выглядит вот так:

*/roll T nX cY dZ rV !*

  *T* - порог успеха
  *X* - число кубиков, если не указано, то будет 2
  *Y* - значение при котором засчитывается критический успех. По умолчанию 1.
  *Z* - сложность проверки, если указана, то я скажу, прошел ли ты ее и сколько создал Импульса, если создал.
  *V* - Минималное число, при котором ты получишь затруднение. По умолчанию 20

Маленькие буквы n, c, d, r - это обязательные "флаги" перед соответствующими числовыми значениями.

Флаг "!" обозначает, что на бросок потрачено очко Решимости и один кубик сразу будет стоять на 1.

Примеры:

/roll 14 - бросок 2х кубиков с порогом 14. Выведет только количество успехов.

/roll 14 c5 - бросок 2х кубиков с порогом 14, с учетом специализаии криты будут на 5 и ниже. Выведет только количество успехов.

/roll 13 n3 ! - бросок 3х кубиков с порогом 14. На бросок потрачено Очко Решимости, первы кубик автоматически будет стоять на 1 в результате.
'''


# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
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
    result = f'*Успехов: {successes}!* ({rolls})'
    if difficulty:
        if successes >= difficulty:
            result += '\n*Проверка пройдена!*'
            momentum = successes - difficulty
            if momentum:
                result += f' Создано Очков Импульса: {momentum}'
        else:
            result += '\n*Проверка не пройдена!*'
    if complications:
        result += f'\nПолучено затруднений: {complications}'
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


bot.infinity_polling()