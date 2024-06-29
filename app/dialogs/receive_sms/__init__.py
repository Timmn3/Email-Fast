from aiogram_dialog import Dialog

from app.dialogs.receive_sms import windows


def select_countries_dialogs():
    return [
        Dialog(
            windows.select_country_window(),
            windows.enter_country_window(),
            windows.enter_country_error_window()
        )
    ]


def select_services_dialogs():
    return [
        Dialog(
            windows.select_service_window(),
            windows.enter_service_window(),
            windows.enter_service_error_window(),
            windows.not_enough_balance_window()
        )
    ]
