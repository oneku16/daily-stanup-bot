from datetime import datetime, timezone
from uuid import uuid4

from app.domain.entities import User
from app.domain.value_objects import StandupAnswers


def test_user_full_name() -> None:
    now = datetime.now(timezone.utc)
    u = User(
        id=uuid4(),
        telegram_id=123,
        username="joe",
        first_name="Joe",
        last_name="Doe",
        is_admin=False,
        created_at=now,
        updated_at=now,
    )
    assert u.full_name == "Joe Doe"
    assert u.mention == "@joe"


def test_standup_answers() -> None:
    a = StandupAnswers(yesterday="a", today="b", issues="c")
    assert a.yesterday == "a"
    assert a.today == "b"
    assert a.issues == "c"
