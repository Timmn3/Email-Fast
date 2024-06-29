import operator

from aiogram_dialog import Window, DialogManager, Data
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.widgets.kbd import Cancel, Back, Button, ScrollingGroup, Select
from aiogram_dialog.widgets.text import Const, Format

from app.dialogs.personal_cabinet.selected import on_deposit_new
from app.dialogs.receive_sms import states
from app.dialogs.receive_sms.getters import get_countries, get_services, get_need_balance, get_other_service
from app.dialogs.receive_sms.selected import on_select_country, on_select_service, on_search_country, on_result_country, \
    on_search_service, on_result_service
from app.services import bot_texts as bt


def select_country_window():
    return Window(
        Const(bt.SELECT_COUNTRY),
        ScrollingGroup(
            Select(
                Format("{item.name}"),
                id="countries_select",
                item_id_getter=operator.attrgetter("country_id"),
                items="countries",
                on_click=on_select_country,
            ),
            id="countries_scroll",
            width=2,
            height=5
        ),
        Button(Const(bt.SEARCH_COUNTRY_BTN), id="search_country", on_click=on_search_country),
        state=states.CountryMenu.select_country,
        getter=get_countries
    )


def enter_country_window():
    return Window(
        Const(bt.ENTER_COUNTRY),
        TextInput(id="country_name", on_success=on_result_country),
        Back(Const(bt.BACK_BTN)),
        state=states.CountryMenu.enter_country
    )


def enter_country_error_window():
    return Window(
        Const(bt.ENTER_COUNTRY_ERROR),
        Button(Const(bt.ENTER_AGAIN_BTN), id="enter_again", on_click=on_search_country),
        Cancel(Const(bt.BACK_BTN)),
        state=states.CountryMenu.enter_country_error
    )


def select_service_window():
    return Window(
        Const(bt.SELECT_SERVICE),
        ScrollingGroup(
            Select(
                Format("{item[name]} {item[cost]}₽"),
                id="services_select",
                item_id_getter=operator.itemgetter("code"),
                items="services",
                on_click=on_select_service,
            ),
            id="services_scroll",
            width=2,
            height=5
        ),
        Button(Const(bt.SEARCH_SERVICE_BTN), id="search_service", on_click=on_search_service),
        Cancel(Const(bt.BACK_BTN)),
        state=states.ServiceMenu.select_service,
        getter=get_services
    )


def enter_service_window():
    return Window(
        Const(bt.ENTER_SERVICE),
        TextInput(id="service_name", on_success=on_result_service),
        Back(Const(bt.BACK_BTN)),
        state=states.ServiceMenu.enter_service
    )


def enter_service_error_window():
    return Window(
        Const(bt.ENTER_SERVICE_ERROR),
        Button(Const(bt.ENTER_AGAIN_BTN), id="enter_again", on_click=on_search_service),
        Select(
            Const(bt.OTHER_SERVICE_BTN),
            id="other_service",
            item_id_getter=operator.itemgetter("code"),
            items="services",
            on_click=on_select_service,
        ),
        Cancel(Const(bt.BACK_BTN)),
        state=states.ServiceMenu.enter_service_error,
        getter=get_other_service
    )


def not_enough_balance_window():
    return Window(
        Format(bt.NOT_ENOUGH_BALANCE),
        Button(Const(bt.DEPOSIT_BTN), id="deposit_btn", on_click=on_deposit_new),
        Back(Const(bt.BACK_BTN)),
        state=states.ServiceMenu.not_enough_balance,
        getter=get_need_balance
    )
