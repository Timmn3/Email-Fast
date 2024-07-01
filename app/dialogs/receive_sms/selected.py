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


# Функция для обработки выбора страны
async def on_select_country(c: types.CallbackQuery, widget: Select, manager: DialogManager, country_id: str):
    """
    Обрабатывает выбор страны пользователем и переводит на меню выбора сервиса.

    :param c: Объект CallbackQuery от aiogram.
    :param widget: Виджет Select от aiogram_dialog.
    :param manager: Менеджер диалогов от aiogram_dialog.
    :param country_id: Идентификатор выбранной страны.
    """
    await manager.start(ServiceMenu.select_service, data={"country_id": country_id})
    # print('on_select_country')


# Функция для обработки нажатия кнопки поиска страны
async def on_search_country(c: types.CallbackQuery, widget: Button, manager: DialogManager):
    """
    Обрабатывает нажатие кнопки поиска страны и переводит на меню ввода страны.

    :param c: Объект CallbackQuery от aiogram.
    :param widget: Виджет Button от aiogram_dialog.
    :param manager: Менеджер диалогов от aiogram_dialog.
    """
    await manager.switch_to(CountryMenu.enter_country)
    # print('on_search_country')


# Функция для обработки результата поиска страны
async def on_result_country(m: types.Message, widget: TextInput, manager: DialogManager, country_name: str):
    """
    Обрабатывает результат поиска страны по введенному названию.

    :param m: Объект Message от aiogram.
    :param widget: Виджет TextInput от aiogram_dialog.
    :param manager: Менеджер диалогов от aiogram_dialog.
    :param country_name: Название страны, введенное пользователем.
    """
    # print('on_result_country')
    countries = await models.Country.search_countries(country_name)
    if len(countries) == 0:
        await manager.switch_to(CountryMenu.enter_country_error)
        return

    ctx = manager.current_context()
    ctx.dialog_data['search_name'] = country_name
    await manager.switch_to(CountryMenu.select_country)


# Функция для отправки информации о сервисе
async def send_service_info(country_id: int, service_code: str, c: types.CallbackQuery, manager: DialogManager = None):
    """
    Отправляет информацию о сервисе пользователю и обрабатывает активацию номера.

    :param country_id: Идентификатор страны.
    :param service_code: Код сервиса.
    :param c: Объект CallbackQuery от aiogram.
    :param manager: Менеджер диалогов от aiogram_dialog (опционально).
    """
    # print('send_service_info')

    # Создаем экземпляр класса для получения SMS
    sms = SmsReceive()

    # Получаем список сервисов для указанной страны
    services = await sms.get_services_by_country_id(country_id=country_id)

    # Ищем нужный сервис по коду
    service = next(filter(lambda x: x['code'] == service_code, services), None)

    # Если сервис не найден, выходим из функции
    if service is None:
        return

    # Получаем стоимость сервиса
    cost = float(service['cost'])

    # Получаем информацию о пользователе
    user = await models.User.get_user(c.from_user.id)

    # Проверяем, достаточно ли у пользователя средств на балансе
    if user.balance < cost:
        if manager:
            # Если используется менеджер диалогов, сохраняем данные и переключаемся на состояние "недостаточно средств"
            ctx = manager.current_context()
            ctx.dialog_data['country_id'] = country_id
            ctx.dialog_data['service_code'] = service_code
            ctx.dialog_data['service_cost'] = cost
            await manager.switch_to(ServiceMenu.not_enough_balance)
            return
        else:
            # Если менеджер диалогов не используется, показываем предупреждение
            await c.answer(text=bt.NOT_ENOUGH_BALANCE_ALERT, show_alert=True)

    # Получаем номер телефона для активации
    phone_number_data = await sms.get_phone_number(country_id=country_id, service_code=service_code)

    # Если не удалось получить номер телефона, показываем предупреждение и выходим из функции
    if 'activationId' not in phone_number_data:
        print(phone_number_data, flush=True)
        await c.answer(text=bt.NOT_NUMBERS_ALERT, show_alert=True)
        return

    # Извлекаем данные активации
    activation_id = int(phone_number_data['activationId'])
    phone_number = phone_number_data['phoneNumber']
    activation_time = datetime.strptime(phone_number_data['activationTime'], "%Y-%m-%d %H:%M:%S")
    activation_expire_at = timezone.make_aware(activation_time)

    # Получаем информацию о стране и сервисе из базы данных
    country = await models.Country.get_country_by_id(country_id=country_id)
    service = await models.Service.get_service(code=service_code)

    # Проверяем, низкий ли баланс у пользователя после списания средств
    low_balance = await check_low_balance(user, cost)

    # Добавляем запись об активации в базу данных
    activation = await models.Activation.add_activation(
        user=user,
        activation_id=activation_id,
        country=country,
        service=service,
        cost=cost,
        phone_number=phone_number,
        activation_expire_at=activation_expire_at + timedelta(minutes=10),
    )

    # Списываем средства с баланса пользователя
    user.balance -= cost
    await user.save(update_fields=['balance'])

    # Если используется менеджер диалогов, сбрасываем стек состояний
    if manager:
        await manager.reset_stack()

    # Создаем клавиатуру с кнопкой для отмены сервиса
    mk = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text=bt.CANCEL_SERVICE_BTN, callback_data=f"cancel_service:{activation.id}")
            ]
        ]
    )

    # Отправляем пользователю информацию о сервисе и номер телефона
    await c.message.edit_text(
        text=bt.SERVICE_INFO.format(
            service=service.name,
            phone=phone_number,
        ),
        reply_markup=mk
    )

    # Ждем 2 секунды перед отправкой уведомления о низком балансе, если это необходимо
    await asyncio.sleep(2)
    if low_balance:
        await send_low_balance_alert(user)


# Функция для обработки выбора сервиса
async def on_select_service(c: types.CallbackQuery, widget: Select, manager: DialogManager, service_code: str):
    """
    Обрабатывает выбор сервиса пользователем и отправляет информацию о сервисе.

    :param c: Объект CallbackQuery от aiogram.
    :param widget: Виджет Select от aiogram_dialog.
    :param manager: Менеджер диалогов от aiogram_dialog.
    :param service_code: Код выбранного сервиса.
    """
    # print('on_select_service')
    ctx = manager.current_context()
    country_id = int(ctx.start_data.get("country_id"))
    await send_service_info(country_id, service_code, c, manager)


# Функция для обработки нажатия кнопки поиска сервиса
async def on_search_service(c: types.CallbackQuery, widget: Button, manager: DialogManager):
    """
    Обрабатывает нажатие кнопки поиска сервиса и переводит на меню ввода сервиса.

    :param c: Объект CallbackQuery от aiogram.
    :param widget: Виджет Button от aiogram_dialog.
    :param manager: Менеджер диалогов от aiogram_dialog.
    """
    await manager.switch_to(ServiceMenu.enter_service)
    # print('on_search_service')


# Функция для обработки результата поиска сервиса
async def on_result_service(m: types.Message, widget: TextInput, manager: DialogManager, service_name: str):
    """
    Обрабатывает результат поиска сервиса по введенному названию.

    :param m: Объект Message от aiogram.
    :param widget: Виджет TextInput от aiogram_dialog.
    :param manager: Менеджер диалогов от aiogram_dialog.
    :param service_name: Название сервиса, введенное пользователем.
    """
    # print('on_result_service')
    services = await models.Service.search_service(service_name)
    ctx = manager.current_context()
    country_id = int(ctx.start_data.get("country_id"))
    ctx.dialog_data['country_id'] = country_id

    if len(services) == 0:
        await manager.switch_to(ServiceMenu.enter_service_error)
        return

    ctx.dialog_data['search_service_name'] = service_name
    await manager.switch_to(ServiceMenu.select_service)
