"""Module for handling updates from private chats.
"""
from aiogram import Router, F
from aiogram.methods.send_message import SendMessage
from aiogram.types.message import Message

router = Router()
router.message.filter(F.chat.type.in_(['private']))

async def makememblist(chatid: int | str, isDoctor: bool) -> list:
    """This method is used to make alive members list

        :param int | str chatid: ID of the chat where bot operates
        :param bool isDoctor: Is this list for a doctor

        :returns: The list of IDs of alive players

        :rtype: list
    """
    from routers.allmessages import gl
    group = gl[chatid]
    alive_members = []
    for el in group.alive_players['Мирные']:
        alive_members.append(el)
    for el in group.alive_players['Мафия']:
        alive_members.append(el)
    if group.alive_players['Дон']:
        alive_members.append(group.alive_players['Дон'])
    if group.alive_players['Шериф']:
        alive_members.append(group.alive_players['Шериф'])
    if not isDoctor:
        if group.alive_players['Доктор']:
            alive_members.append(group.alive_players['Доктор'])
    return alive_members

@router.message(F.text)
async def spreadTheWord(message: Message) -> None:
    """This method is used to handle private messages during night

        :param aiogram.types.message.Message message: Telegram Message object

        :returns: None
    """
    from routers.allmessages import gl
    userid = message.chat.id
    for key in gl:
        if userid in gl[key].playerslist:
            group = gl[key]
            if group.night == 1 and userid in group.alive_players['Мафия'] or userid == group.alive_players['Дон']:
                don = group.alive_players['Дон']
                maf_members = []
                for el in group.alive_players['Мафия']:
                    maf_members.append(el)
                if don:
                    maf_members.append(don)
                maf_members.remove(userid)
                if userid == don:
                    text = f'@{message.from_user.username} (Дон):\n'
                else:
                    text = f'@{message.from_user.username}:\n'
                text += message.text
                for playerid in maf_members:
                    await SendMessage(chat_id=playerid, text=text)
            elif group.night == 1 or group.timetochoosemaf == 1 and userid == group.alive_players['Доктор']:
                alive_members = await makememblist(key, True)
                for userid, username in group.playerslist.items():
                    if message.text == username and userid in alive_members:
                        await message.reply('Ваше решение принято. Вы можете его изменить до конца ночи.')
                        gl[key].doctor_chosen = userid
                    else:
                        await message.reply('Такого участника не найдено или он уже мёртв..')
            elif group.timetochoosemaf == 1 and userid == group.alive_players['Дон']:
                alive_members = await makememblist(key, False)
                for userid, username in group.playerslist.items():
                    if message.text == username and userid in alive_members:
                        await message.reply('Ваше решение принято. Вы можете его изменить до конца ночи.')
                        gl[key].mafia_chosen.append(userid)
                    else:
                        await message.reply('Такого участника не найдено или он уже мёртв.')
            elif group.timetochoosemaf == 1 and not group.alive_players['Дон'] and userid in group.alive_players['Мафия']:
                alive_members = await makememblist(key, False)
                for userid, username in group.playerslist.items():
                    if message.text == username and userid in alive_members:
                        await message.reply('Ваше решение принято. Вы можете его изменить до конца ночи.')
                        gl[key].mafia_chosen.append(userid)
                    else:
                        await message.reply('Такого участника не найдено или он уже мёртв.')
