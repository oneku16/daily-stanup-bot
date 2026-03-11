import uuid
from datetime import date, time
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dtos import BotSettingsDto, HistorySummaryDto, StandupReportDto
from app.domain.entities import StandupReport, User
from app.domain.value_objects import StandupAnswers
from app.infrastructure.repositories import (
    SettingsRepository,
    StandupReportRepository,
    UserRepository,
)


async def get_or_create_user(
    session: AsyncSession,
    telegram_id: int,
    username: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    is_admin: bool = False,
) -> User:
    repo = UserRepository(session)
    return await repo.upsert(
        telegram_id=telegram_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
        is_admin=is_admin,
    )


async def save_standup_report(
    session: AsyncSession, user_id: uuid.UUID, answers: StandupAnswers
) -> StandupReport:
    repo = StandupReportRepository(session)
    return await repo.create(user_id, answers)


def _format_report_line(report: StandupReport, user: User) -> str:
    from datetime import datetime
    ts = report.reported_at or report.created_at
    dt_str = ts.strftime("%d-%m | %H:%M") if isinstance(ts, datetime) else ""
    return (
        f"{user.mention}\n"
        f"{user.full_name}\n"
        f"{dt_str}\n"
        f"Yesterday: {report.yesterday}\n"
        f"Today: {report.today}\n"
        f"Issues: {report.issues}"
    )


async def publish_standup(
    session: AsyncSession, report: StandupReport, user: User
) -> str:
    return _format_report_line(report, user)


async def get_bot_settings(session: AsyncSession) -> BotSettingsDto:
    repo = SettingsRepository(session)
    entity = await repo.get_or_create_default()
    return BotSettingsDto(
        standup_time=entity.standup_time,
        target_channel_id=entity.target_channel_id,
        standup_topic_id=entity.standup_topic_id,
    )


async def update_bot_settings(
    session: AsyncSession,
    standup_time: Optional[time] = None,
    target_channel_id: Optional[int] = None,
    standup_topic_id: Optional[int] = None,
) -> BotSettingsDto:
    repo = SettingsRepository(session)
    entity = await repo.update(
        standup_time=standup_time,
        target_channel_id=target_channel_id,
        standup_topic_id=standup_topic_id,
    )
    return BotSettingsDto(
        standup_time=entity.standup_time,
        target_channel_id=entity.target_channel_id,
        standup_topic_id=entity.standup_topic_id,
    )


async def get_history_summary(session: AsyncSession, d: date) -> HistorySummaryDto:
    repo = StandupReportRepository(session)
    pairs = await repo.get_reports_for_date(d)
    reports: list[StandupReportDto] = []
    for report, user in pairs:
        ts = report.reported_at or report.created_at
        from datetime import datetime
        dt_str = ts.strftime("%d-%m | %H:%M") if isinstance(ts, datetime) else ""
        reports.append(
            StandupReportDto(
                username=user.mention,
                full_name=user.full_name,
                reported_at_str=dt_str,
                yesterday=report.yesterday,
                today=report.today,
                issues=report.issues,
            )
        )
    return HistorySummaryDto(reports=reports)


__all__ = [
    "get_or_create_user",
    "save_standup_report",
    "publish_standup",
    "get_bot_settings",
    "update_bot_settings",
    "get_history_summary",
]
