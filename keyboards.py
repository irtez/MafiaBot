from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
#from aiogram.utils.keyboard import ReplyKeyboardBuilder
#from aiogram.types.reply_keyboard_markup import ReplyKeyboardMarkup
#from aiogram.types import KeyboardButton

def create_game():
    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text='Присоединиться к игре', callback_data='join'))
    markup.row(InlineKeyboardButton(text='Ливнуть', callback_data='discard'))
    markup.row(InlineKeyboardButton(text='Начать игру', callback_data='start'))
    return markup.as_markup()