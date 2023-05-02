from aiogram import Router, F
from aiogram.filters import Command
from aiogram.methods.edit_message_text import EditMessageText
from aiogram.methods.answer_callback_query import AnswerCallbackQuery
from aiogram.methods.send_message import SendMessage
from aiogram.types.message import Message
from aiogram.types.callback_query import CallbackQuery
import keyboards
import config
from random import shuffle


router = Router()
router.message.filter(F.chat.type.in_(['group', 'supergroup']))

gl = {}

class Group():
    def __init__(self):
        self.created = 0
        self.started = 0
        self.playerslist = {}
        self.players_roles = {}
        self.settings = {'roles': ['Мирный', 'Мафия'], 'day_turn': 45, 'night_turn': 100, 'min_players': 2}
        self.createmsg = None
        self.settingsmsg = None
        self.game_adm = None

async def roleDistrib(chatid: int | str):
    group = gl[chatid]
    roles = group.settings['roles']
    members = list(group.playerslist.keys())
    doc = True if 'Доктор' in roles else False
    don = True if 'Дон' in roles else False
    sherif = True if 'Шериф' in roles else False
    rand_list = list(range(len(members)))
    shuffle(rand_list)
    group.players_roles = {}
    if doc:
        group.players_roles['Доктор'] = members[rand_list[0]]
        rand_list.pop(0)
    if don:
        group.players_roles['Дон'] = members[rand_list[0]]
        rand_list.pop(0)
    if sherif:
        group.players_roles['Шериф'] = members[rand_list[0]]
        rand_list.pop(0)
    

    

    

async def editCreateMsg(chatid: int | str, mode: str):
    group = gl[chatid]
    text='Для присоединения к игре и запуска воспользуйтесь кнопками ниже.\n\n'
    if mode == 'player':
        if len(group.playerslist) == 0:
            text += 'Список игроков пуст.'
        else:
            text += 'Список игроков:\n'
            i = 1
            for el in group.playerslist.values():
                text += f"{i}. @{el}\n"
                i += 1
        kb = keyboards.create_game()
    elif mode == 'started':
        text = 'Игра запущена.'
        kb = None
    
    await EditMessageText(text=text, chat_id=chatid, message_id=group.createmsg, reply_markup=kb)

async def editSettingsMsg(chatid: int | str, mode: str):
    group = gl[chatid]
    text = '<b>Добавленные роли:</b>\n'
    for role in group.settings['roles']:
        text += role + '\n'
    text += f"\n<b>Время хода днём:</b> {group.settings['day_turn']} секунд\n"
    text += f"<b>Время хода ночью:</b> {group.settings['night_turn']} секунд\n"
    text += f"<b>Минимальное количество игроков:</b> {group.settings['min_players']}\n\n"

    if mode == 'main':
        text += 'Выберите настройки для игры:'
        kb = keyboards.settings()
    elif mode == 'change_roles':
        text += 'Выберите роли: '
        kb = keyboards.settings_roles(group.settings['roles'])
    elif mode == 'change_dayturn':
        text += 'Выберите длительность хода днём:'
        kb = keyboards.settings_turn()
    elif mode == 'change_nightturn':
        text += 'Выберите длительность хода ночью:'
        kb = keyboards.settings_turn(False)
    await EditMessageText(text=text, chat_id=chatid, message_id=group.settingsmsg, reply_markup=kb)

async def initGroup(chatid: int | str):
    if not chatid in gl:
        gl[chatid] = Group()

@router.message(Command('start'))
async def start(message: Message):
    await initGroup(chatid=message.chat.id)
    await message.answer('хуй')

@router.message(Command('settings'))
async def settings(message: Message):
    await initGroup(chatid=message.chat.id)
    group = gl[message.chat.id]
    if group.started == 1:
        message.answer('Нельзя менять настройки во время игры.')
        return
    msg = await message.answer(text='Выберите настройки для игры: ', reply_markup=keyboards.settings())
    group.settingsmsg = msg.message_id
    await editSettingsMsg(message.chat.id, 'main')

@router.message(Command('create'))
async def create(message: Message):
    await initGroup(chatid=message.chat.id)
    group = gl[message.chat.id]
    if group.created == 1:
        await message.answer('Лобби уже создано.')
        return
    if group.started == 1:
        await message.answer('Игра уже начата.')
        return
    group.game_adm = message.from_user.id
    group.playerslist = {}
    msg = await message.answer(text='Для присоединения к игре и запуска воспользуйтесь кнопками ниже.', reply_markup=keyboards.create_game())
    group.createmsg = msg.message_id
    group.created = 1

@router.callback_query(F.data.contains('change_'))
async def call_change(call: CallbackQuery):
    chatid = call.message.chat.id
    group = gl[chatid]
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
        if role in group.settings['roles']:
            group.settings['roles'].remove(role)
        else:
            group.settings['roles'].append(role)
        group.settings['min_players'] = len(group.settings['roles']) + 2
        await editSettingsMsg(chatid, 'change_roles')
    elif 'turn_' in call.data:
        time = call.data.split('_')[1][0:-4]
        sec = int(call.data.split('_')[2])
        group.settings[f'{time}_turn'] = sec
        await editSettingsMsg(chatid, f'change_{time}turn')
        

@router.callback_query()
async def call(call: CallbackQuery):
    group = gl[call.message.chat.id]
    if call.data == 'join':
        try:
            await SendMessage(chat_id=call.from_user.id, text=f'Вы присоединились к игре в чате "{call.message.chat.title}".')
        except:
            await AnswerCallbackQuery(callback_query_id=call.id, text='Сначала запустите бота в личных сообщениях.')
            return
        if call.from_user.id not in group.playerslist:
            group.playerslist[call.from_user.id] = call.from_user.username
        else:
            await AnswerCallbackQuery(callback_query_id=call.id, text='Вы уже присоединились.', show_alert=True)
        await editCreateMsg(call.message.chat.id, 'player')
    elif call.data == 'discard':
        if call.from_user.id in group.playerslist:
            group.playerslist.pop(call.from_user.id)
        else:
            await AnswerCallbackQuery(callback_query_id=call.id, text='Вы еще не присоединились.', show_alert=True)
        await editCreateMsg(call.message.chat.id, 'player')
    elif call.data == 'start':
        if call.from_user.id == group.game_adm:
            if len(group.playerslist) >= group.settings['min_players']\
                    and len(group.playerslist) <= 10:
                group.created = 0
                group.started = 1
                await editCreateMsg(call.message.chat.id, 'started')
                group.createmsg = None
                await roleDistrib(call.message.chat.id)
            else:
                await AnswerCallbackQuery(callback_query_id=call.id, text='Количество игроков ниже минимального.', show_alert=True)
        else:
            await AnswerCallbackQuery(callback_query_id=call.id, text='Вы не можете начать игру.', show_alert=True)
