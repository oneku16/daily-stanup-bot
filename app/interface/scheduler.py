import logging
from datetime import time
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.config import settings
from app.infrastructure.database import async_session_factory
from app.infrastructure.repositories import SettingsRepository, UserRepository

logger = logging.getLogger(__name__)


def _standup_trigger(hour: int, minute: int):
    tz = ZoneInfo(settings.bot.standup_timezone)
    return CronTrigger(hour=hour, minute=minute, timezone=tz)


def reschedule_standup_job(scheduler: AsyncIOScheduler, standup_time: time) -> None:
    scheduler.reschedule_job(
        "standup_reminder",
        trigger=_standup_trigger(standup_time.hour, standup_time.minute),
    )
    logger.info(
        "Standup job rescheduled to %02d:%02d %s",
        standup_time.hour,
        standup_time.minute,
        settings.bot.standup_timezone,
    )


def setup_scheduler(bot) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()

    async def send_standup_reminder() -> None:
        logger.info("Standup reminder triggered")
        async with async_session_factory() as session:
            user_repo = UserRepository(session)
            users = await user_repo.get_all()
            await session.commit()
        if not users:
            logger.warning("Standup reminder: no users to notify")
            return
        logger.info("Standup reminder: sending to %d users", len(users))
        for u in users:
            try:
                await bot.send_message(
                    u.telegram_id,
                    "Time for your daily standup! Use /standup to submit.",
                )
            except Exception as e:
                logger.warning("Standup reminder: failed to send to %s: %s", u.telegram_id, e)

    async def register_daily_job() -> None:
        async with async_session_factory() as session:
            settings_repo = SettingsRepository(session)
            entity = await settings_repo.get_or_create_default()
            await session.commit()
        hour, minute = entity.standup_time.hour, entity.standup_time.minute
        scheduler.add_job(
            send_standup_reminder,
            _standup_trigger(hour, minute),
            id="standup_reminder",
            replace_existing=True,
        )
        logger.info(
            "Standup job scheduled for %02d:%02d %s",
            hour,
            minute,
            settings.bot.standup_timezone,
        )

    return scheduler, register_daily_job


__all__ = ["setup_scheduler", "reschedule_standup_job"]
