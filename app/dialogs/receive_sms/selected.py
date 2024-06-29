from datetime import datetime, timedelta

import asyncio
from aiogram import types
from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities import Context
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Select, Button
from tortoise import timezone
from tortoise.exceptions import OperationalError
from tortoise.transactions import in_transaction

from app.db import models
from app.dialogs.receive_sms.states import ServiceMenu, CountryMenu
from app.services.low_balance import check_low_balance, send_low_balance_alert
from app.services.sms_receive import SmsReceive
from app.services import bot_texts as bt


async def on_select_country(c: types.CallbackQuery, widget: Select, manager: DialogManager, country_id: str):
    await manager.start(ServiceMenu.select_service, data={"country_id": country_id})


async def on_search_country(c: types.CallbackQuery, widget: Button, manager: DialogManager):
    await manager.switch_to(CountryMenu.enter_country)


async def on_result_country(m: types.Message, widget: TextInput, manager: DialogManager, country_name: str):
    countries = await models.Country.search_countries(country_name)
    if len(countries) == 0:
        await manager.switch_to(CountryMenu.enter_country_error)
        return

    ctx = manager.current_context()
    ctx.dialog_data['search_name'] = country_name
    await manager.switch_to(CountryMenu.select_country)


async def send_service_info(country_id: int, service_code: str, c: types.CallbackQuery, manager: DialogManager = None):
    sms = SmsReceive()
    services = await sms.get_services_by_country_id(country_id=country_id)
    service = next(filter(lambda x: x['code'] == service_code, services), None)
    if service is None:
        return

    cost = float(service['cost'])
    user = await models.User.get_user(c.from_user.id)
    if user.balance < cost:
        if manager:
            ctx = manager.current_context()
            ctx.dialog_data['country_id'] = country_id
            ctx.dialog_data['service_code'] = service_code
            ctx.dialog_data['service_cost'] = cost
            await manager.switch_to(ServiceMenu.not_enough_balance)
            return
        else:
            await c.answer(text=bt.NOT_ENOUGH_BALANCE_ALERT, show_alert=True)

    phone_number_data = await sms.get_phone_number(country_id=country_id, service_code=service_code)
    if 'activationId' not in phone_number_data:
        print(phone_number_data, flush=True)
        await c.answer(text=bt.NOT_NUMBERS_ALERT, show_alert=True)
        return

    activation_id = int(phone_number_data['activationId'])
    phone_number = phone_number_data['phoneNumber']
    activation_time = datetime.strptime(phone_number_data['activationTime'], "%Y-%m-%d %H:%M:%S")
    activation_expire_at = timezone.make_aware(activation_time)
    country = await models.Country.get_country_by_id(country_id=country_id)
    service = await models.Service.get_service(code=service_code)

    low_balance = await check_low_balance(user, cost)

    activation = await models.Activation.add_activation(
        user=user,
        activation_id=activation_id,
        country=country,
        service=service,
        cost=cost,
        phone_number=phone_number,
        activation_expire_at=activation_expire_at + timedelta(minutes=10),
    )

    user.balance -= cost
    await user.save(update_fields=['balance'])

    if manager:
        await manager.reset_stack()

    mk = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text=bt.CANCEL_SERVICE_BTN, callback_data=f"cancel_service:{activation.id}")
            ]
        ]
    )
    await c.message.edit_text(
        text=bt.SERVICE_INFO.format(
            service=service.name,
            phone=phone_number,
        ),
        reply_markup=mk
    )

    await asyncio.sleep(2)
    if low_balance:
        await send_low_balance_alert(user)


async def on_select_service(c: types.CallbackQuery, widget: Select, manager: DialogManager, service_code: str):
    ctx = manager.current_context()
    country_id = int(ctx.start_data.get("country_id"))
    await send_service_info(country_id, service_code, c, manager)


async def on_search_service(c: types.CallbackQuery, widget: Button, manager: DialogManager):
    await manager.switch_to(ServiceMenu.enter_service)


async def on_result_service(m: types.Message, widget: TextInput, manager: DialogManager, service_name: str):
    services = await models.Service.search_service(service_name)
    ctx = manager.current_context()
    country_id = int(ctx.start_data.get("country_id"))
    ctx.dialog_data['country_id'] = country_id

    if len(services) == 0:
        await manager.switch_to(ServiceMenu.enter_service_error)
        return

    ctx.dialog_data['search_service_name'] = service_name
    await manager.switch_to(ServiceMenu.select_service)
