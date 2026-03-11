from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import Message

from app.application.use_cases import get_or_create_user
from app.config import settings

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, session, bot: Bot) -> None:
    is_admin = message.from_user.id in settings.bot.admin_ids
    user = await get_or_create_user(
        session,
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        is_admin=is_admin,
    )
    await message.answer(
        "Hi! I'm the standup bot. Use /standup to submit your daily standup. "
        "Admins can configure schedule and view history."
    )


__all__ = ["router"]
