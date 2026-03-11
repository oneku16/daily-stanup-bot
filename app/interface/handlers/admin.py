from datetime import date, timedelta
import re

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.types import Message

from app.application.use_cases import get_bot_settings, get_history_summary, update_bot_settings
from app.config import settings as app_settings
from app.infrastructure.repositories import UserRepository
from app.interface.scheduler import reschedule_standup_job

router = Router()


@router.message(Command("settime"))
async def cmd_settime(message: Message, session, scheduler) -> None:
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    if not user or not user.is_admin:
        await message.answer("Only admins can set the standup time.")
        return
    text = message.text or ""
    parts = text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(
            "Usage: /settime HH:MM (e.g. /settime 10:00)"
        )
        return
    match = re.match(r"^(\d{1,2}):(\d{2})$", parts[1].strip())
    if not match:
        await message.answer("Invalid time. Use HH:MM (e.g. 10:00).")
        return
    hour, minute = int(match.group(1)), int(match.group(2))
    if hour < 0 or hour > 23 or minute < 0 or minute > 59:
        await message.answer("Invalid time.")
        return
    from datetime import time
    new_time = time(hour, minute)
    await update_bot_settings(session, standup_time=new_time)
    reschedule_standup_job(scheduler, new_time)
    tz = app_settings.bot.standup_timezone
    await message.answer(
        f"Standup time set to {hour:02d}:{minute:02d} ({tz}). Reminders will run at this time."
    )


@router.message(Command("setchannel"))
async def cmd_setchannel(message: Message, session, bot) -> None:
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    if not user or not user.is_admin:
        await message.answer("Only admins can set the target channel.")
        return
    text = message.text or ""
    parts = text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(
            "Usage: /setchannel <channel_id>\n\n"
            "1. Add this bot to your channel as administrator with \"Post messages\" permission.\n"
            "2. Channel ID is a number like -1001234567890. Get it by forwarding any message from the channel to @RawDataBot — it will show the chat id."
        )
        return
    try:
        channel_id = int(parts[1].strip())
    except ValueError:
        await message.answer("Channel ID must be a number (e.g. -1001234567890).")
        return
    await update_bot_settings(session, target_channel_id=channel_id)
    try:
        kwargs = {"chat_id": channel_id, "text": "Standup bot: channel connected. Standup reports will be posted here."}
        s = await get_bot_settings(session)
        if s.standup_topic_id is not None:
            kwargs["message_thread_id"] = s.standup_topic_id
        await bot.send_message(**kwargs)
        await message.answer(f"Target channel set to {channel_id}. Test message sent — standup reports will be posted there.")
    except Exception as e:
        await message.answer(
            f"Channel ID saved as {channel_id}, but the bot could not post a test message. "
            "Ensure the bot is in the channel as admin with \"Post messages\" permission. Error: " + str(e)
        )


@router.message(Command("settopic"))
async def cmd_settopic(message: Message, session, bot) -> None:
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    if not user or not user.is_admin:
        await message.answer("Only admins can set the standup topic.")
        return
    text = message.text or ""
    parts = text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(
            "Usage: /settopic <topic_id>\n\n"
            "For a forum/supergroup, the topic (thread) ID is the number of the topic. "
            "Reply to a message in the topic and forward it to @RawDataBot to see message_thread_id."
        )
        return
    try:
        topic_id = int(parts[1].strip())
    except ValueError:
        await message.answer("Topic ID must be a number (e.g. 1627).")
        return
    await update_bot_settings(session, standup_topic_id=topic_id)
    await message.answer(f"Standup topic ID set to {topic_id}. Reports will be posted to this topic.")


@router.message(Command("history"))
async def cmd_history(message: Message, session) -> None:
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    if not user or not user.is_admin:
        await message.answer("Only admins can view history.")
        return
    text = message.text or ""
    parts = text.split(maxsplit=1)
    if len(parts) < 2:
        d = date.today() - timedelta(days=1)
    else:
        try:
            from datetime import datetime
            d = datetime.strptime(parts[1].strip(), "%d-%m-%Y").date()
        except ValueError:
            await message.answer("Use format: /history DD-MM-YYYY (e.g. /history 10-03-2025)")
            return
    summary = await get_history_summary(session, d)
    if not summary.reports:
        await message.answer(f"No standup reports for {d.strftime('%d-%m-%Y')}.")
        return
    lines = []
    for r in summary.reports:
        lines.append(
            f"{r.username}\n{r.full_name}\n{r.reported_at_str}\n"
            f"Yesterday: {r.yesterday}\nToday: {r.today}\nIssues: {r.issues}"
        )
    body = "\n\n===========\n\n".join(lines)
    await message.answer(f"Standup report for {d.strftime('%d-%m-%Y')}:\n\n{body}")


@router.message(Command("settings"))
async def cmd_settings(message: Message, session) -> None:
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    if not user or not user.is_admin:
        await message.answer("Only admins can view settings.")
        return
    s = await get_bot_settings(session)
    ch = str(s.target_channel_id) if s.target_channel_id else "not set"
    topic = str(s.standup_topic_id) if s.standup_topic_id is not None else "not set"
    tz = app_settings.bot.standup_timezone
    await message.answer(
        f"Standup time: {s.standup_time.strftime('%H:%M')} ({tz})\n"
        f"Target channel ID: {ch}\n"
        f"Standup topic ID: {topic}"
    )


__all__ = ["router"]
