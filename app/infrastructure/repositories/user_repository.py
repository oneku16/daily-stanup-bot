from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import User
from app.infrastructure.schema.models import UserModel


def _to_entity(m: UserModel) -> User:
    return User(
        id=m.id,
        telegram_id=m.telegram_id,
        username=m.username,
        first_name=m.first_name,
        last_name=m.last_name,
        is_admin=m.is_admin,
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        result = await self._session.execute(
            select(UserModel).where(UserModel.telegram_id == telegram_id)
        )
        row = result.scalar_one_or_none()
        return _to_entity(row) if row else None

    async def get_all(self) -> list[User]:
        result = await self._session.execute(select(UserModel))
        return [_to_entity(m) for m in result.scalars().all()]

    async def upsert(
        self,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        is_admin: bool = False,
    ) -> User:
        existing = await self.get_by_telegram_id(telegram_id)
        if existing:
            result = await self._session.execute(
                select(UserModel).where(UserModel.telegram_id == telegram_id)
            )
            model = result.scalar_one()
            model.username = username
            model.first_name = first_name
            model.last_name = last_name
            model.is_admin = is_admin
            await self._session.flush()
            await self._session.refresh(model)
            return _to_entity(model)
        model = UserModel(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            is_admin=is_admin,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return _to_entity(model)


__all__ = ["UserRepository"]
