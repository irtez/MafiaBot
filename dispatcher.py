from aiogram import Bot, Dispatcher
from config import token
import routers.allmessages as allmsg
from aiogram.fsm.storage.memory import MemoryStorage

bot = Bot(token=token)

dp = Dispatcher(storage = MemoryStorage())
dp.include_router(allmsg.router)
