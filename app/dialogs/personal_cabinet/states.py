from aiogram.fsm.state import StatesGroup, State


class PersonalMenu(StatesGroup):
    user_info = State()
    deposit = State()
    deposit_choose_method = State()
    enter_amount = State()

