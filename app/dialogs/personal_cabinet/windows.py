from aiogram import F
from aiogram_dialog import Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Cancel, Back, Button, Url
from aiogram_dialog.widgets.text import Const, Format

from app import dependencies
from app.dialogs.personal_cabinet import states, keyboards
from app.dialogs.personal_cabinet.getters import get_user_info, get_deposit_prices
from app.dialogs.personal_cabinet.selected import on_deposit_price, on_other_price, on_deposit, on_enter_other_price
from app.services import bot_texts as bt


def personal_cabinet_window():
    return Window(
        Format(bt.PERSONAL_CABINET),
        Button(Const(bt.DEPOSIT_BTN), id='deposit', on_click=on_deposit),
        Url(Const(bt.SUPPORT_BTN), url=Const(dependencies.SUPPORT_URL)),
        state=states.PersonalMenu.user_info,
        getter=get_user_info
    )


def deposit_window():
    return Window(
        Const(bt.SELECT_DEPOSIT_PRICE),
        keyboards.prices_kb(on_deposit_price),
        Button(Const(bt.OTHER_DEPOSIT_PRICE_BTN), id='other_price', on_click=on_other_price, when=~F['bonus']),
        Button(Const(bt.OTHER_DEPOSIT_PRICE_BTN + ' (+10%)'), id='other_price', on_click=on_other_price, when=F['bonus']),
        Back(Const(bt.BACK_BTN)),
        state=states.PersonalMenu.deposit,
        getter=get_deposit_prices
    )


def enter_amount_window():
    return Window(
        Const(bt.ENTER_DEPOSIT_AMOUNT),
        TextInput(id='enter_deposit_amount', on_success=on_enter_other_price),
        Back(Const(bt.BACK_BTN)),
        state=states.PersonalMenu.enter_amount
    )


# def deposit_choose_window():
#     return Window(
#         Const(bt.SELECT_DEPOSIT_METHOD),
#         Button(Const(bt.METHOD_BANK_CARD_BTN), id='bank_card', on_click=on_deposit_method),
#         Button(Const(bt.METHOD_SBP_BTN), id='sbp', on_click=on_deposit_method, when=F['dialog_data']['price'] >= 300),
#         Button(Const(bt.METHOD_CRYPTO_BTN), id='crypto', on_click=on_deposit_method, when=F['dialog_data']['price'] >= 300),
#         Button(Const(bt.METHOD_OTHER_BTN), id='other', on_click=on_deposit_method),
#         Button(Const(bt.BACK_BTN), id='back', on_click=on_deposit),
#         state=states.PersonalMenu.deposit_choose_method
#     )
