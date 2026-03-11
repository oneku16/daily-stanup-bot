from datetime import time
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.settings_entity import BotSettingsEntity
from app.infrastructure.schema.models import SettingsModel


def _to_entity(m: SettingsModel) -> BotSettingsEntity:
    return BotSettingsEntity(
        id=m.id,
        standup_time=m.standup_time,
        target_channel_id=m.target_channel_id,
        standup_topic_id=m.standup_topic_id,
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


class SettingsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_or_create_default(self) -> BotSettingsEntity:
        result = await self._session.execute(select(SettingsModel).limit(1))
        row = result.scalar_one_or_none()
        if row:
            return _to_entity(row)
        model = SettingsModel(standup_time=time(10, 0), target_channel_id=None, standup_topic_id=None)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return _to_entity(model)

    async def update(
        self,
        standup_time: Optional[time] = None,
        target_channel_id: Optional[int] = None,
        standup_topic_id: Optional[int] = None,
    ) -> BotSettingsEntity:
        entity = await self.get_or_create_default()
        result = await self._session.execute(
            select(SettingsModel).where(SettingsModel.id == entity.id)
        )
        model = result.scalar_one()
        if standup_time is not None:
            model.standup_time = standup_time
        if target_channel_id is not None:
            model.target_channel_id = target_channel_id
        if standup_topic_id is not None:
            model.standup_topic_id = standup_topic_id
        await self._session.flush()
        await self._session.refresh(model)
        return _to_entity(model)


__all__ = ["SettingsRepository"]
