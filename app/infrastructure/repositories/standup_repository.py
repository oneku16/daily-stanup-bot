import uuid
from datetime import date, datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities import StandupReport, User
from app.domain.value_objects import StandupAnswers
from app.infrastructure.schema.models import StandupReportModel, UserModel


def _report_to_entity(m: StandupReportModel) -> StandupReport:
    return StandupReport(
        id=m.id,
        user_id=m.user_id,
        yesterday=m.yesterday,
        today=m.today,
        issues=m.issues,
        reported_at=m.reported_at,
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


class StandupReportRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, user_id: uuid.UUID, answers: StandupAnswers) -> StandupReport:
        model = StandupReportModel(
            user_id=user_id,
            yesterday=answers.yesterday,
            today=answers.today,
            issues=answers.issues,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return _report_to_entity(model)

    async def get_reports_for_date(self, d: date) -> list[tuple[StandupReport, User]]:
        start = datetime.combine(d, datetime.min.time(), tzinfo=timezone.utc)
        end = datetime.combine(d, datetime.max.time(), tzinfo=timezone.utc)
        result = await self._session.execute(
            select(StandupReportModel)
            .options(selectinload(StandupReportModel.user))
            .where(
                StandupReportModel.reported_at >= start,
                StandupReportModel.reported_at <= end,
            )
        )
        rows = result.scalars().all()
        out: list[tuple[StandupReport, User]] = []
        for m in rows:
            report = _report_to_entity(m)
            u = m.user
            user = User(
                id=u.id,
                telegram_id=u.telegram_id,
                username=u.username,
                first_name=u.first_name,
                last_name=u.last_name,
                is_admin=u.is_admin,
                created_at=u.created_at,
                updated_at=u.updated_at,
            )
            out.append((report, user))
        return out


__all__ = ["StandupReportRepository"]
