import asyncio
import logging

from app.interface.bot import create_bot
from app.interface.middlewares import SchedulerMiddleware
from app.interface.scheduler import setup_scheduler

logging.basicConfig(level=logging.INFO)

__all__ = ["main"]


async def main() -> None:
    bot, dp = create_bot()
    scheduler, register_daily_job = setup_scheduler(bot)
    dp.message.middleware(SchedulerMiddleware(scheduler))
    await register_daily_job()
    scheduler.start()
    try:
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
