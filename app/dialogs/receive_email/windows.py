import operator

from aiogram import F
from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Cancel, Back, Button
from aiogram_dialog.widgets.text import Const, Format

from app.dialogs.personal_cabinet.selected import on_deposit_new
from app.dialogs.receive_email import states
from app.dialogs.receive_email.getters import get_email_info, get_balance
from app.dialogs.receive_email.keyboards import rent_email_kb
from app.dialogs.receive_email.selected import on_change_email, on_rent_email, on_rent_email_item, \
    on_confirm_rent_email, on_back_mail, on_my_rent_emails
from app.services import bot_texts as bt


def receive_email_window():
    return Window(
        Format(bt.MY_EMAIL),
        Button(Const(bt.CHANGE_EMAIL_BTN), id='change_email', on_click=on_change_email),
        Button(Const(bt.RENT_EMAIL_BTN), id='rent_email', on_click=on_rent_email),
        Button(
            Const(bt.MY_RENT_EMAILS_BTN),
            id='my_rent_emails_btn',
            on_click=on_my_rent_emails,
            when=F['paid_mails_count'] > 0
        ),
        state=states.ReceiveEmailMenu.receive_email,
        getter=get_email_info
    )


def rent_email_window():
    return Window(
        Format(bt.MY_EMAIL),
        rent_email_kb(on_rent_email_item),
        Button(Const(bt.BACK_BTN), id='back_rent', on_click=on_back_mail),
        state=states.ReceiveEmailMenu.rent_email,
        getter=get_email_info
    )


def confirm_rent_email_window():
    return Window(
        Format(bt.CONFIRM_RENT_EMAIL),
        Button(Const(bt.CONFIRM_BTN), id='confirm_btn', on_click=on_confirm_rent_email),
        Back(Const(bt.BACK_BTN)),
        state=states.ReceiveEmailMenu.rent_email_confirm
    )


def not_enough_balance_window():
    return Window(
        Format(bt.NOT_ENOUGH_BALANCE),
        Button(Const(bt.DEPOSIT_BTN), id='deposit_btn', on_click=on_deposit_new),
        Back(Const(bt.BACK_BTN)),
        state=states.ReceiveEmailMenu.not_enough_balance,
        getter=get_balance
    )


def rent_email_success_window():
    return Window(
        Format(bt.RENT_EMAIL_SUCCESS),
        Button(Const(bt.MY_RENT_EMAILS_BTN), id='my_rent_emails_btn', on_click=on_my_rent_emails),
        state=states.ReceiveEmailMenu.rent_email_success
    )

