import dispatcher
import asyncio

async def main() -> None:
    """Main function that starts the bot.

        :returns: None
    """
    dp = dispatcher.dp
    bot = dispatcher.bot
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())