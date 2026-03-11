from aiogram.fsm.state import State, StatesGroup


class StandupStates(StatesGroup):
    yesterday = State()
    today = State()
    issues = State()
