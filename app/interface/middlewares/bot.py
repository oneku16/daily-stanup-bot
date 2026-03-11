from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import Bot, BaseMiddleware
from aiogram.types import TelegramObject


class BotMiddleware(BaseMiddleware):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        data["bot"] = self.bot
        return await handler(event, data)


__all__ = ["BotMiddleware"]
