from aiogram import Bot, Dispatcher
from bottoken import token
import routers.allmessages as allmsg
import routers.nightturn as night
from aiogram.fsm.storage.memory import MemoryStorage

bot = Bot(token=token, parse_mode='HTML')

dp = Dispatcher(storage = MemoryStorage())
dp.include_router(allmsg.router)
dp.include_router(night.router)
