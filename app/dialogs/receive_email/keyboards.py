from aiogram_dialog.widgets.kbd import Group, Button
from aiogram_dialog.widgets.text import Const
from app.services import bot_texts as bt


def rent_email_kb(on_click):
    return Group(
        Button(Const(bt.RENT_EMAIL_WEEK_BTN), id='rent_email_week', on_click=on_click),
        Button(Const(bt.RENT_EMAIL_MONTH_BTN), id='rent_email_month', on_click=on_click),
        Button(Const(bt.RENT_EMAIL_TWO_MONTHS_BTN), id='rent_email_two_months', on_click=on_click),
        Button(Const(bt.RENT_EMAIL_SIX_MONTHS_BTN), id='rent_email_six_months', on_click=on_click),
        Button(Const(bt.RENT_EMAIL_YEAR_BTN), id='rent_email_year', on_click=on_click),
        id='rent_email_kb',
        width=1
    )
