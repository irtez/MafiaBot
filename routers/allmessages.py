from aiogram import Router, F
from aiogram.filters import Command
from aiogram.methods.edit_message_text import EditMessageText
from aiogram.methods.answer_callback_query import AnswerCallbackQuery
from aiogram.methods.send_message import SendMessage
from aiogram.types.message import Message
from aiogram.types.callback_query import CallbackQuery
import keyboards
import config


router = Router()
router.message.filter(F.chat.type.in_(['group', 'supergroup']))

gl = {}

async def editCreateMsg(chatid: int | str, mode: str):
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

async def editSettingsMsg(chatid: int | str, mode: str):
    text = '<b>Добавленные роли:</b>\n'
    for role in gl[chatid]['settings']['roles']:
        text += role + '\n'
    text += f"\n<b>Время хода днём:</b> {gl[chatid]['settings']['day_turn']} секунд\n"
    text += f"<b>Время хода ночью:</b> {gl[chatid]['settings']['night_turn']} секунд\n"
    text += f"<b>Минимальное количество игроков:</b> {gl[chatid]['settings']['min_players']}\n\n"

    if mode == 'main':
        text += 'Выберите настройки для игры:'
        kb = keyboards.settings()
    elif mode == 'change_roles':
        text += 'Выберите роли: '
        kb = keyboards.settings_roles(gl[chatid]['settings']['roles'])
    elif mode == 'change_dayturn':
        text += 'Выберите длительность хода днём:'
        kb = keyboards.settings_turn()
    elif mode == 'change_nightturn':
        text += 'Выберите длительность хода ночью:'
        kb = keyboards.settings_turn(False)
    await EditMessageText(text=text, chat_id=chatid, message_id=gl[chatid]['settingsmsg'], reply_markup=kb)

async def initGroup(chatid: int | str):
    if not chatid in gl:
        gl[chatid] = {}
        gl[chatid]['settings'] = {'roles': ['Мирный', 'Мафия'], 'day_turn': 45, 'night_turn': 100, 'min_players': 2}
        gl[chatid]['created'] = 0
        gl[chatid]['started'] = 0
        gl[chatid]['playerslist'] = {}

@router.message(Command('start'))
async def start(message: Message):
    await initGroup(chatid=message.chat.id)
    await message.answer('хуй')

@router.message(Command('settings'))
async def settings(message: Message):
    await initGroup(chatid=message.chat.id)
    msg = await message.answer(text='Выберите настройки для игры: ', reply_markup=keyboards.settings())
    gl[message.chat.id]['settingsmsg'] = msg.message_id
    await editSettingsMsg(message.chat.id, 'main')

@router.message(Command('create'))
async def create(message: Message):
    await initGroup(chatid=message.chat.id)
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

@router.callback_query(F.data.contains('change_'))
async def call_change(call: CallbackQuery):
    chatid = call.message.chat.id
    if call.data == 'change_roles':
        await editSettingsMsg(chatid, 'change_roles')
    elif call.data == 'change_dayturn':
        await editSettingsMsg(chatid, 'change_dayturn')
    elif call.data == 'change_nightturn':
        await editSettingsMsg(chatid, 'change_nightturn')
    elif call.data == 'change_backtomain':
        await editSettingsMsg(chatid, 'main')
    elif 'change_role_' in call.data:
        role = config.all_roles[int(call.data.split('_')[2])]
        if role in gl[chatid]['settings']['roles']:
            gl[chatid]['settings']['roles'].remove(role)
        else:
            gl[chatid]['settings']['roles'].append(role)
        gl[chatid]['settings']['min_players'] = len(gl[chatid]['settings']['roles']) + 2
        await editSettingsMsg(chatid, 'change_roles')
    elif 'turn_' in call.data:
        time = call.data.split('_')[1][0:-4]
        sec = int(call.data.split('_')[2])
        gl[chatid]['settings'][f'{time}_turn'] = sec
        await editSettingsMsg(chatid, f'change_{time}turn')
        

@router.callback_query()
async def call(call: CallbackQuery):
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
            if len(gl[call.message.chat.id]['playerslist']) >= gl[call.message.chat.id]['settings']['min_players']:
                gl[call.message.chat.id]['created'] = 0
                gl[call.message.chat.id]['started'] = 1
                await editCreateMsg(call.message.chat.id, 'started')
                gl[call.message.chat.id].pop('createmsg')
            else:
                await AnswerCallbackQuery(callback_query_id=call.id, text='Количество игроков ниже минимального.', show_alert=True)
        else:
            await AnswerCallbackQuery(callback_query_id=call.id, text='Вы не можете начать игру.', show_alert=True)


