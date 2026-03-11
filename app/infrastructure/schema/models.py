import uuid
from datetime import datetime, time
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, String, Text, Time, func
from sqlalchemy.dialects.postgresql import BIGINT, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.schema.base import BaseModel

if TYPE_CHECKING:
    from app.infrastructure.schema.models import UserModel

class UserModel(BaseModel):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(BIGINT, unique=True, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_admin: Mapped[bool] = mapped_column(default=False)
    reports: Mapped[list["StandupReportModel"]] = relationship(
        "StandupReportModel", back_populates="user"
    )


class StandupReportModel(BaseModel):
    __tablename__ = "standup_reports"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    yesterday: Mapped[str] = mapped_column(Text, nullable=False)
    today: Mapped[str] = mapped_column(Text, nullable=False)
    issues: Mapped[str] = mapped_column(Text, nullable=False)
    reported_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="reports")


class SettingsModel(BaseModel):
    __tablename__ = "settings"

    standup_time: Mapped[time] = mapped_column(Time, nullable=False)
    target_channel_id: Mapped[Optional[int]] = mapped_column(BIGINT, nullable=True)
    standup_topic_id: Mapped[Optional[int]] = mapped_column(BIGINT, nullable=True)


__all__ = ["UserModel", "StandupReportModel", "SettingsModel"]
