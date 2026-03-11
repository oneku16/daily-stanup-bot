import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    id: uuid.UUID
    telegram_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    is_admin: bool
    created_at: datetime
    updated_at: datetime

    @property
    def full_name(self) -> str:
        parts = [self.first_name or "", self.last_name or ""]
        return " ".join(p for p in parts if p).strip() or str(self.telegram_id)

    @property
    def mention(self) -> str:
        return f"@{self.username}" if self.username else self.full_name


@dataclass
class StandupReport:
    id: uuid.UUID
    user_id: uuid.UUID
    yesterday: str
    today: str
    issues: str
    reported_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
