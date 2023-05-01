import dispatcher
import asyncio

async def main():
    dp = dispatcher.dp
    bot = dispatcher.bot
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())