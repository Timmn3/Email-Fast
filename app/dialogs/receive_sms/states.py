from aiogram.fsm.state import StatesGroup, State


class CountryMenu(StatesGroup):
    select_country = State()
    enter_country = State()
    enter_country_error = State()


class ServiceMenu(StatesGroup):
    select_service = State()
    service_info = State()
    enter_service = State()
    enter_service_error = State()
    not_enough_balance = State()

