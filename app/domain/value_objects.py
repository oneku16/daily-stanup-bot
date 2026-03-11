from dataclasses import dataclass


@dataclass(frozen=True)
class StandupAnswers:
    yesterday: str
    today: str
    issues: str
