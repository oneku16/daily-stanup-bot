from dataclasses import dataclass
from datetime import time
from typing import Optional
import uuid
from datetime import datetime


@dataclass
class BotSettingsEntity:
    id: uuid.UUID
    standup_time: time
    target_channel_id: Optional[int]
    standup_topic_id: Optional[int]
    created_at: datetime
    updated_at: datetime
