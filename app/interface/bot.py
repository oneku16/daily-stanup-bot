from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import settings
from app.interface.handlers import router
from app.interface.middlewares import BotMiddleware, DbSessionMiddleware


def create_bot() -> tuple[Bot, Dispatcher]:
    bot = Bot(
        token=settings.bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp.message.middleware(BotMiddleware(bot))
    dp.message.middleware(DbSessionMiddleware())
    dp.include_router(router)
    return bot, dp


__all__ = ["create_bot"]
