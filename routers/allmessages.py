from aiogram import Router, F
from aiogram.filters import Command
from aiogram.methods.edit_message_text import EditMessageText
from aiogram.methods.answer_callback_query import AnswerCallbackQuery
from aiogram.methods.restrict_chat_member import RestrictChatMember
from aiogram.methods.send_message import SendMessage
from aiogram.types.message import Message
from aiogram.types.callback_query import CallbackQuery
import asyncio
import keyboards
import config
import copy
from random import shuffle, choice


router = Router()
router.message.filter(F.chat.type.in_(['group', 'supergroup']))

#todo:
#список игроков и список ролей при старте игры, шерифа и то что доктор может лечить себя и не может одного и того же 2 раза

gl = {}

class Group():
    def __init__(self):
        self.created = 0
        self.started = 0
        self.playerslist = {}
        self.players_roles = {}
        self.settings = {'day_turn': 7, 'night_turn': 30, 'meet_time': 7}
        self.createmsg = None
        self.settingsmsg = None
        self.game_adm = None
        self.night = 0
        self.timetochoosemaf = 0
        self.mafia_chosen = []
        self.doctor_chosen = None
        self.alive_players = {}
        self.votemsg = None
        self.votes = {}
        self.voters = []

async def roleDistrib(chatid: int | str):
    group = gl[chatid]
    members = list(group.playerslist.keys())
    memb_num = len(members)
    match memb_num:
        case 3:
            roles = ['Мафия', 'Шериф', 'Доктор']
        case 4:
            roles = ['Мирный', 'Мирный', 'Мафия', 'Доктор']
        case 5:
            roles = ['Мирный', 'Мирный', 'Мафия', 'Доктор', 'Дон']
        case 6:
            roles = ['Мирный', 'Мирный', 'Мафия', 'Доктор', 'Дон', 'Шериф']
        case 7:
            roles = ['Мирный', 'Мирный', 'Мирный', 'Мафия', 'Мафия', 'Дон', 'Шериф']
        case 8:
            roles = ['Мирный', 'Мирный', 'Мирный', 'Мафия', 'Мафия', 'Дон', 'Шериф', 'Доктор']
        case 9:
            roles = ['Мирный', 'Мирный', 'Мирный', 'Мирный', 'Мафия', 'Мафия', 'Дон', 'Шериф', 'Доктор']
        case 10:
            roles = ['Мирный', 'Мирный', 'Мирный', 'Мирный', 'Мафия', 'Мафия', 'Мафия', 'Дон', 'Шериф', 'Доктор']
    shuffle(members)
    group.players_roles['Мирные'] = []
    group.players_roles['Мафия'] = []
    group.players_roles['Дон'] = None
    group.players_roles['Шериф'] = None
    group.players_roles['Доктор'] = None
    mirn_num = roles.count('Мирный')
    maf_num = roles.count('Мафия')
    for i in range(mirn_num):
        group.players_roles['Мирные'].append(members[i])
        members.pop(i)
    for i in range(maf_num):
        group.players_roles['Мафия'].append(members[i])
        members.pop(i)
    d = dict(zip(roles[mirn_num+maf_num:], members))
    for key in d:
        group.players_roles[key] = d[key]
    group.alive_players = copy.deepcopy(group.players_roles)
    for pid in group.players_roles['Мирные']:
        await SendMessage(chat_id=pid, text='Ваша роль - Мирный.')
    for pid in group.players_roles['Мафия']:
        await SendMessage(chat_id=pid, text='Ваша роль - Мафия.')
    for el in config.all_roles[2:]:
        if group.players_roles[el]:
            await SendMessage(chat_id=group.players_roles[el], text=f'Ваша роль - {el}.')

async def meeting(chatid: int | str, members: list):
    group = gl[chatid]
    for playerid in members:
        await SendMessage(chat_id=chatid, text=f'@{group.playerslist[playerid]}, ваша очередь.')
        try:
            await RestrictChatMember(chat_id=chatid, user_id=playerid, permissions={'can_send_messages': True})
        except:
            pass
        await asyncio.sleep(group.settings['meet_time'])
        try:
            await RestrictChatMember(chat_id=chatid, user_id=playerid, permissions={'can_send_messages': False})
        except:
            pass

async def night(chatid: int | str) -> (int | str):
    killed = None
    group = gl[chatid]
    group.night = 1
    doc = group.alive_players['Доктор']
    if doc:
        await SendMessage(chat_id=doc, text='<b>Пора выбирать, кого спасти этой ночью.</b>\nУ вас есть 10 секунд. '
                          'Вы можете менять своё решение на протяжении этого времени.')
    await asyncio.sleep(group.settings['night_turn']-10)
    don = group.alive_players['Дон']
    group.night = 0
    group.timetochoosemaf = 1
    if don:
        await SendMessage(chat_id=don, text='<b>Пора выбирать, кого убивать этой ночью.</b>\nУ вас есть 10 секунд. '
                          'Вы можете менять своё решение на протяжении этого времени.')
    else:
        for playerid in group.alive_players['Мафия']:
            await SendMessage(chat_id=playerid, text='<b>Пора выбирать, кого убивать этой ночью.</b>\nУ вас есть 10 секунд. '
                          'Вы можете менять своё решение на протяжении этого времени.\nТак как Дона нет в игре,'
                          ' умрет тот, за кого мафия отдаст больше голосов. В случае равенства голосов никто не умрёт.')
    await asyncio.sleep(10)
    group.timetochoosemaf = 0
    group = gl[chatid]
    print('maf and doc chose: ', group.mafia_chosen, '; ', group.doctor_chosen)
    repeats = {x: group.mafia_chosen.count(x) for x in group.mafia_chosen}
    max_votes = max(repeats.values())
    sum = 0
    for key in repeats:
        if repeats[key] == max_votes:
            sum += 1
    if sum == 1:
        killedid = [k for k, v in repeats.items() if v == max_votes][0]
    if killedid != group.doctor_chosen:
        killed = killedid
    return killed

async def lastWord(chatid: int | str, killed: int | str):
    group = gl[chatid]
    try:
        await RestrictChatMember(chat_id=chatid, user_id=killed, permissions={'can_send_messages': True})
    except:
        pass
    await asyncio.sleep(20)
    try:
        await RestrictChatMember(chat_id=chatid, user_id=killed, permissions={'can_send_messages': False})
    except:
        pass
    await SendMessage(chat_id=chatid, text='Время для последнего слова истекло.')
    if killed in group.alive_players['Мирные']:
        group.alive_players['Мирные'].remove(killed)
    if killed in group.alive_players['Мафия']:
        group.alive_players['Мафия'].remove(killed)
    if killed == group.alive_players['Доктор']:
        group.alive_players['Доктор'] = None
    if killed == group.alive_players['Дон']:
        group.alive_players['Дон'] = None
    if killed == group.alive_players['Шериф']:
        group.alive_players['Шериф'] = None

async def winCheck(chatid: int | str):
    group = gl[chatid]
    sherif = 1 if group.alive_players['Шериф'] else 0
    doc = 1 if group.alive_players['Доктор'] else 0
    don = 1 if group.alive_players['Дон'] else 0
    if sum(group.alive_players['Мирные']) + sherif + doc <= sum(group.alive_players['Мафия']) + don:
        await SendMessage(chat_id=chatid, text='Игра окончена. Победила мафия.')
        return True
    if sum(group.alive_players['Мафия']) + don == 0:
        await SendMessage(chat_id=chatid, text='Игра окончена. Победили мирные жители.')
        return True
    return False
    
async def dayDiscuss(chatid: int | str, members: list):
    group = gl[chatid]
    for playerid in members:
        await SendMessage(chat_id=chatid, text=f'@{group.playerslist[playerid]}, ваша очередь.')
        try:
            await RestrictChatMember(chat_id=chatid, user_id=playerid, permissions={'can_send_messages': True})
        except:
            pass
        await asyncio.sleep(group.settings['day_turn'])
        try:
            await RestrictChatMember(chat_id=chatid, user_id=playerid, permissions={'can_send_messages': False})
        except:
            pass

async def golosovanie(chatid: int | str) -> int:
    votedid = None
    group = gl[chatid]
    members = []
    for el in group.alive_players['Мирные']:
        members.append(el)
    for el in group.alive_players['Мафия']:
        members.append(el)
    if group.alive_players['Шериф']:
        members.append(group.alive_players['Шериф'])
    if group.alive_players['Дон']:
        members.append(group.alive_players['Дон'])
    if group.alive_players['Доктор']:
        members.append(group.alive_players['Доктор'])
    for playerid in members:
        group.votes[playerid] = 0
    await editVoteMsg(chatid, 'main')
    await asyncio.sleep(20)
    max_votes = max(group.votes.values())
    sum = 0
    for key in group.votes:
        if group.votes[key] == max_votes:
            sum += 1
    if sum == 1:
        votedid = [k for k, v in group.votes.items() if v == max_votes][0]
    return votedid

async def editVoteMsg(chatid: int | str, mode: str):
    group = gl[chatid]
    text = '<b>Распределение голосов:</b>\n'
    members = []
    for el in group.alive_players['Мирные']:
        members.append(el)
    for el in group.alive_players['Мафия']:
        members.append(el)
    if group.alive_players['Шериф']:
        members.append(group.alive_players['Шериф'])
    if group.alive_players['Дон']:
        members.append(group.alive_players['Дон'])
    if group.alive_players['Доктор']:
        members.append(group.alive_players['Доктор'])
    shuffle(members)
    md = {}
    for member in members:
        md[member] = group.playerslist[member]
    if mode == 'main':
        for playerid in list(md.keys()):
            text += f"@{md[playerid]}: {group.votes[playerid]}\n"
        kb = keyboards.golosovanie(md)
    elif mode == 'finished':
        for playerid in list(md.keys()):
            text += f"@{md[playerid]}: {group.votes[playerid]}\n"
        text += '<b>Голосование завершено.</b>'
        kb = None
    await EditMessageText(text=text, chat_id=chatid, message_id=group.votemsg, reply_markup=kb)

@router.callback_query(F.data.contains('vote'))
async def call_kill(call: CallbackQuery):
    chatid = call.message.chat.id
    group = gl[chatid]
    callerid = call.from_user.id
    if callerid in group.alive_players['Мирные'] or callerid in group.alive_players['Мафия']\
        or callerid == group.alive_players['Дон'] or callerid == group.alive_players['Шериф']\
        or callerid == group.alive_players['Доктор']:
        if not callerid in group.voters:
            group.voters.append(callerid)
            voted = int(call.data.split()[1])
            group.votes[voted] += 1
            await SendMessage(chat_id=chatid, text=f"@{call.from_user.username} отдаёт свой голос за {group.playerslist[voted]}.")
            await editVoteMsg(chatid, 'main')
        else:
            await AnswerCallbackQuery(callback_query_id=call.id, text='Вы уже проголосовали.', show_alert=True)

async def unmuteAll(chatid: int | str) -> None:
    group = gl[chatid]
    for playerid in (group.playerslist.keys()):
        try:
            await RestrictChatMember(chat_id=chatid, user_id=playerid, permissions={'can_send_messages': True})
        except:
            pass

async def game_main(chatid: int | str):
    group = gl[chatid]
    await roleDistrib(chatid)
    members = list(group.playerslist.keys())
    shuffle(members)
    await SendMessage(chat_id=chatid, text='Распределение ролей окончено, проверьте личные сообщения с ботом.'
                      ' Через 5 секунд начнется знакомство.')
    for playerid in members:
        try:
            await RestrictChatMember(chat_id=chatid, user_id=playerid, permissions={'can_send_messages': False})
        except:
            pass
    await asyncio.sleep(5)
    await SendMessage(chat_id=chatid, text=f"Начинается знакомство. Каждому даётся {group.settings['meet_time']} секунд.")
    await meeting(chatid, members)
    while True:
        await SendMessage(chat_id=chatid, text=f"Начинается ночь длительностью {group.settings['night_turn']} секунд.\n"
                        "Члены мафии могут писать боту в ЛС, сообщения будут пересылаться остальным.")
        killed = await night(chatid)
        group.mafia_chosen = []
        group.doctor_chosen = None
        if killed:
            await SendMessage(chat_id=chatid, text=f'Этой ночью умер @{group.playerslist[killed]}.')
            gameover = await winCheck(chatid)
            if gameover:
                group.started = 0
                await unmuteAll(chatid)
                return
            await SendMessage(chat_id=chatid, text='Вам даётся 20 секунд на последнее слово.')
            await lastWord(chatid, killed)
            members.remove(killed)
        else:
            await SendMessage(chat_id=chatid, text='Этой ночью никто не был убит.')
        await SendMessage(chat_id=chatid, text="Начинается дневное обсуждение. Каждому игроку даётся"
                        f" {group.settings['day_turn']} секунд.")
        await dayDiscuss(chatid, members)
        await SendMessage(chat_id=chatid, text='Дневное обсуждение закончилось. Начинается голосование длительностью 20 секунд.'
                          '\n<b>Переголосовать нельзя.</b>')
        msg = await SendMessage(chat_id=chatid, text='Распределение голосов:')
        group.votemsg = msg.message_id
        voted = await golosovanie(chatid)
        group.voters = []
        if voted:
            await SendMessage(chat_id=chatid, text=f'В результате голосования был повешен @{group.playerslist[voted]}.')
            gameover = await winCheck(chatid)
            if gameover:
                group.started = 0
                await unmuteAll(chatid)
                return
            await SendMessage(chat_id=chatid, text='Вам даётся 20 секунд на последнее слово.')
            await lastWord(chatid, voted)
            members.remove(voted)
        else:
            await SendMessage(chat_id=chatid, text='В результате голосования никто не был повешен.')

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
    #text = '<b>Добавленные роли:</b>\n'
    #for role in group.settings['roles']:
    #    text += role + '\n'
    text = f"\n<b>Время хода днём:</b> {group.settings['day_turn']} секунд\n"
    text += f"<b>Время хода ночью:</b> {group.settings['night_turn']} секунд\n"
    #text += f"<b>Минимальное количество игроков:</b> {group.settings['min_players']}\n\n"

    if mode == 'main':
        text += 'Выберите настройки для игры:'
        kb = keyboards.settings()
    #elif mode == 'change_roles':
    #    text += 'Выберите роли: '
    #    kb = keyboards.settings_roles(group.settings['roles'])
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
    await message.answer(message.chat.type)

@router.message(Command('mute'))
async def mute(message: Message):
    try:
        await RestrictChatMember(chat_id=message.chat.id, user_id=message.from_user.id, permissions={'can_send_messages': False})
    except BaseException as e:
        print(e)
    await asyncio.sleep(1)
    try:
        await RestrictChatMember(chat_id=message.chat.id, user_id=message.from_user.id, permissions={'can_send_messages': True})
    except BaseException as e:
        print(e)

@router.message(Command('unmute'))
async def unmute(message: Message):
    ids = [273454910, 1727815289]
    for p in ids:
        try:
            await RestrictChatMember(chat_id=message.chat.id, user_id=p, permissions={'can_send_messages': True})
        except BaseException as e:
            print(e)


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
    #if call.data == 'change_roles':
    #    await editSettingsMsg(chatid, 'change_roles')
    if call.data == 'change_dayturn':
        await editSettingsMsg(chatid, 'change_dayturn')
    elif call.data == 'change_nightturn':
        await editSettingsMsg(chatid, 'change_nightturn')
    elif call.data == 'change_backtomain':
        await editSettingsMsg(chatid, 'main')
    #elif 'change_role_' in call.data:
    #    role = config.all_roles[int(call.data.split('_')[2])]
    #    if role in group.settings['roles']:
    #        group.settings['roles'].remove(role)
    #    else:
    #        group.settings['roles'].append(role)
    #    roles = group.settings['roles']
    #    if 'Доктор' in roles:
    #        mp = 4
    #    await editSettingsMsg(chatid, 'change_roles')
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
            if len(group.playerslist) >= config.min_players\
                    and len(group.playerslist) <= 10:
                group.created = 0
                group.started = 1
                await editCreateMsg(call.message.chat.id, 'started')
                group.createmsg = None
                asyncio.create_task(coro=game_main(call.message.chat.id), name='Game')
            else:
                await AnswerCallbackQuery(callback_query_id=call.id, text='Количество игроков ниже минимального.', show_alert=True)
        else:
            await AnswerCallbackQuery(callback_query_id=call.id, text='Вы не можете начать игру.', show_alert=True)
