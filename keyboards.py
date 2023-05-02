from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
import config
#from aiogram.utils.keyboard import ReplyKeyboardBuilder
#from aiogram.types.reply_keyboard_markup import ReplyKeyboardMarkup
#from aiogram.types import KeyboardButton

def create_game():
    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text='Присоединиться к игре', callback_data='join'))
    markup.row(InlineKeyboardButton(text='Ливнуть', callback_data='discard'))
    markup.row(InlineKeyboardButton(text='Начать игру', callback_data='start'))
    return markup.as_markup()

def settings():
    markup = InlineKeyboardBuilder()
    #markup.row(InlineKeyboardButton(text='Выбрать роли для игры', callback_data='change_roles'))
    markup.row(InlineKeyboardButton(text='Изменить время хода днём', callback_data='change_dayturn'))
    markup.row(InlineKeyboardButton(text='Изменить время хода ночью', callback_data='change_nightturn'))
    return markup.as_markup()

"""
def settings_roles(current_roles: list):
    markup = InlineKeyboardBuilder()
    i = 0
    for role in config.all_roles:
        if role not in ['Мирный', 'Мафия']:
            s = 'добавить' if role not in current_roles else 'убрать'
            markup.row(InlineKeyboardButton(text=f'{role} {s}', callback_data=f'change_role_{i}'))
        i += 1
    markup.row(InlineKeyboardButton(text='Назад', callback_data='change_backtomain'))
    return markup.as_markup()
"""

def settings_turn(day = True):
    markup = InlineKeyboardBuilder()
    mint = 10 if day else 30
    maxt = 51 if day else 121
    step = 10 if day else 15
    s = 'day' if day else 'night'
    for i in range(mint, maxt):
        if i % step == 0:
            markup.add(InlineKeyboardButton(text=i, callback_data=f'change_{s}turn_{i}'))
    markup.row(InlineKeyboardButton(text='Назад', callback_data='change_backtomain'))
    return markup.as_markup()

def golosovanie(players: dict):
    markup = InlineKeyboardBuilder()
    for playerid, playername in players:
        markup.row(InlineKeyboardButton(text=playername, callback_data=f'vote {playerid}'))
    return markup.as_markup()