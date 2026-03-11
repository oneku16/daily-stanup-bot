import logging
import uuid

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.application.use_cases import get_or_create_user, publish_standup, save_standup_report
from app.config import settings
from app.domain.value_objects import StandupAnswers
from app.infrastructure.repositories import SettingsRepository, UserRepository
from app.interface.fsm import StandupStates

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("standup"))
async def cmd_standup(message: Message, session, state: FSMContext, bot: Bot) -> None:
    is_admin = message.from_user.id in settings.bot.admin_ids
    user = await get_or_create_user(
        session,
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        is_admin=is_admin,
    )
    await state.update_data(user_id=str(user.id))
    await state.set_state(StandupStates.yesterday)
    await message.answer("What did you do yesterday?")


@router.message(StandupStates.yesterday, F.text)
async def step_yesterday(message: Message, state: FSMContext) -> None:
    await state.update_data(yesterday=message.text or "")
    await state.set_state(StandupStates.today)
    await message.answer("What are you going to do today?")


@router.message(StandupStates.today, F.text)
async def step_today(message: Message, state: FSMContext) -> None:
    await state.update_data(today=message.text or "")
    await state.set_state(StandupStates.issues)
    await message.answer("What kind of issues/blockers are you having?")


@router.message(StandupStates.issues, F.text)
async def step_issues(
    message: Message, state: FSMContext, session, bot: Bot
) -> None:
    data = await state.get_data()
    yesterday = data.get("yesterday", "")
    today = data.get("today", "")
    issues = message.text or ""
    user_id = data.get("user_id")
    if not user_id:
        await state.clear()
        await message.answer("Session expired. Please run /standup again.")
        return
    answers = StandupAnswers(yesterday=yesterday, today=today, issues=issues)
    report = await save_standup_report(session, uuid.UUID(user_id), answers)
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    if not user:
        await state.clear()
        await message.answer("Error: user not found.")
        return
    formatted = await publish_standup(session, report, user)
    settings_repo = SettingsRepository(session)
    entity = await settings_repo.get_or_create_default()
    await state.clear()

    channel_id = entity.target_channel_id
    if not channel_id:
        logger.warning("Standup completed but target channel not configured")
        await message.answer(
            "Standup submitted. Post to channel skipped — admin should set channel with /setchannel."
        )
        return

    try:
        kwargs = {"chat_id": int(channel_id), "text": formatted}
        if entity.standup_topic_id is not None:
            kwargs["message_thread_id"] = int(entity.standup_topic_id)
        await bot.send_message(**kwargs)
        await message.answer("Standup submitted and published to the channel.")
    except Exception as e:
        logger.exception("Failed to post standup to channel %s: %s", channel_id, e)
        await message.answer(
            "Standup submitted. Failed to post to channel — ensure the bot is added to the channel as admin with permission to post messages."
        )


__all__ = ["router"]
