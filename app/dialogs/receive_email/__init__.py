from aiogram_dialog import Dialog

from app.dialogs.receive_email import windows


def receive_email_dialogs():
    return [
        Dialog(
            windows.rent_email_window(),
            windows.receive_email_window(),
            windows.confirm_rent_email_window(),
            windows.not_enough_balance_window(),
            windows.rent_email_success_window()
        )
    ]
