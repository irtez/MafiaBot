from aiogram import Router
from aiogram.filters import Command
from aiogram.methods.edit_message_text import EditMessageText
from aiogram.methods.answer_callback_query import AnswerCallbackQuery
from aiogram.methods.send_message import SendMessage
import keyboards
import config


router = Router()

gl = {}

async def editCreateMsg(chatid, mode):
    text='Для присоединения к игре и запуска воспользуйтесь кнопками ниже.\n\n'

    if mode == 'player':
        
        if len(gl[chatid]['playerslist']) == 0:
            text += 'Список игроков пуст.'
        else:
            text += 'Список игроков:\n'
            i = 1
            for el in gl[chatid]['playerslist'].values():
                text += f"{i}. @{el}\n"
                i += 1
        kb = keyboards.create_game()
    elif mode == 'started':
        text = 'Игра запущена.'
        kb = None
    
    await EditMessageText(text=text, chat_id=chatid, message_id=gl[chatid]['createmsg'], reply_markup=kb)


@router.message(Command('start'))
async def start(message):
    if not message.chat.id in gl:
        gl[message.chat.id] = {}
    await message.answer('хуй')

@router.message(Command('create'))
async def create(message):
    if not message.chat.id in gl:
        gl[message.chat.id] = {}
    if 'created' in gl[message.chat.id] or 'started' in gl[message.chat.id]:
        if gl[message.chat.id]['created'] == 1:
            await message.answer('Лобби уже создано.')
            return
        if gl[message.chat.id]['started'] == 1:
            await message.answer('Игра уже начата.')
            return
    gl[message.chat.id]['game_adm'] = message.from_user.id
    gl[message.chat.id]['playerslist'] = {}
    msg = await message.answer(text='Для присоединения к игре и запуска воспользуйтесь кнопками ниже.', reply_markup=keyboards.create_game())
    gl[message.chat.id]['createmsg'] = msg.message_id
    gl[message.chat.id]['created'] = 1

@router.callback_query()
async def call(call):
    if call.data == 'join':
        try:
            await SendMessage(chat_id=call.from_user.id, text=f'Вы присоединились к игре в "{call.message.chat.title}".')
        except:
            await AnswerCallbackQuery(callback_query_id=call.id, text='Сначала запустите бота в личных сообщениях.')
            return
        if call.from_user.id not in gl[call.message.chat.id]['playerslist']:
            gl[call.message.chat.id]['playerslist'][call.from_user.id] = call.from_user.username
        else:
            await AnswerCallbackQuery(callback_query_id=call.id, text='Вы уже присоединились.', show_alert=True)
        await editCreateMsg(call.message.chat.id, 'player')
    elif call.data == 'discard':
        if call.from_user.id in gl[call.message.chat.id]['playerslist']:
            gl[call.message.chat.id]['playerslist'].pop(call.from_user.id)
        else:
            await AnswerCallbackQuery(callback_query_id=call.id, text='Вы еще не присоединились.', show_alert=True)
        await editCreateMsg(call.message.chat.id, 'player')
    elif call.data == 'start':
        if call.from_user.id == gl[call.message.chat.id]['game_adm']:
            if len(gl[call.message.chat.id]['playerslist']) >= config.min_players:
                gl[call.message.chat.id]['created'] = 0
                gl[call.message.chat.id]['started'] = 1
                await editCreateMsg(call.message.chat.id, 'started')
                gl[call.message.chat.id].pop('createmsg')
            else:
                await AnswerCallbackQuery(callback_query_id=call.id, text='Количество игроков ниже минимального.', show_alert=True)
        else:
            await AnswerCallbackQuery(callback_query_id=call.id, text='Вы не можете начать игру.', show_alert=True)


