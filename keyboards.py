"""Module that consists of of markups for specific messages.
"""
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup
import config

def create_game() -> InlineKeyboardMarkup:
    """This method is used to create initial markup.

        :returns: Game start inline markup

        :rtype: aiogram.types.InlineKeyboardMarkup
    """
    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text='Присоединиться к игре', callback_data='join'))
    markup.row(InlineKeyboardButton(text='Ливнуть', callback_data='discard'))
    markup.row(InlineKeyboardButton(text='Начать игру', callback_data='start'))
    return markup.as_markup()

def settings() -> InlineKeyboardMarkup:
    """This method is used to make settings markup.

        :returns: Game settings inline markup

        :rtype: aiogram.types.InlineKeyboardMarkup
    """
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

def settings_turn(day: bool) -> InlineKeyboardMarkup:
    """This method is used to make turns length markup.

        :param bool day: Are settings for day turn

        :returns: Turns length inline markup

        :rtype: aiogram.types.InlineKeyboardMarkup
    """
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

def golosovanie(players: dict) -> InlineKeyboardMarkup:
    """This method is used to make voting markup.

        :param dict players: Dictionary with pairs player ID: player username

        :returns: Voting inline markup

        :rtype: aiogram.types.InlineKeyboardMarkup
    """
    markup = InlineKeyboardBuilder()
    for playerid, playername in players.items():
        markup.row(InlineKeyboardButton(text=playername, callback_data=f'vote {playerid}'))
    return markup.as_markup()