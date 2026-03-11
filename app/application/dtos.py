from dataclasses import dataclass
from datetime import date, time
from typing import Optional


@dataclass
class StandupReportDto:
    username: str
    full_name: str
    reported_at_str: str
    yesterday: str
    today: str
    issues: str


@dataclass
class HistorySummaryDto:
    reports: list[StandupReportDto]


@dataclass
class BotSettingsDto:
    standup_time: time
    target_channel_id: Optional[int]
    standup_topic_id: Optional[int]
