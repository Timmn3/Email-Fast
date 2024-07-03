from datetime import datetime, timedelta
import math
import asyncio
from aiogram import types
from aiogram_dialog import DialogManager, StartMode
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
async def on_select_country_new(c: types.CallbackQuery, widget: Select, manager: DialogManager, country_index: str):
    """
    Обрабатывает выбор страны и сервиса.

    :param c: Объект CallbackQuery от aiogram.
    :param widget: Виджет Select от aiogram_dialog.
    :param manager: Менеджер диалогов от aiogram_dialog.
    :param country_index: Индекс выбранной страны.
    """
    # Извлекаем service_code из текущего контекста
    ctx = manager.current_context()
    service_code = ctx.start_data.get('service_code')

    # Извлекаем список стран с ценами из контекста
    countries_with_prices = ctx.start_data.get('countries_with_prices', [])

    # Преобразуем индекс в целое число
    country_index = int(country_index)

    # Проверяем, что индекс находится в пределах списка
    if 0 <= country_index < len(countries_with_prices):
        selected_country = countries_with_prices[country_index]
        country_name = selected_country['country']
        price = selected_country['price']
        country_id = await models.Country.get_country_id_by_name(country_name)
        # print(f"Service Code: {service_code}, country_id: {country_id}, Country: {country_name}, Price: {price}")
        await send_service_on_country(country_id=country_id, service_code=service_code, price=price, c=c)

    else:
        print(f"Country with index {country_index} not found.")


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
    countries = await models.Country.search_countries(country_name)
    if len(countries) == 0:
        await manager.switch_to(CountryMenu.enter_country_error)
        return

    ctx = manager.current_context()
    ctx.dialog_data['search_name'] = country_name
    await manager.switch_to(CountryMenu.select_country)


# Функция для отправки информации о сервисе
async def send_service_on_country(country_id: int, service_code: str, price: float,
                                  c: types.CallbackQuery, manager: DialogManager = None):
    """
    Отправляет информацию о сервисе пользователю и обрабатывает активацию номера.

    :param country_id: Идентификатор страны.
    :param service_code: Код сервиса.
    :param c: Объект CallbackQuery от aiogram.
    :param manager: Менеджер диалогов от aiogram_dialog (опционально).
    """
    sms = SmsReceive()

    # Получаем информацию о пользователе
    user = await models.User.get_user(c.from_user.id)

    # Проверяем, достаточно ли у пользователя средств на балансе
    if user.balance < price:
        await c.answer(text=bt.NOT_ENOUGH_BALANCE_ALERT, show_alert=True)
        return

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
    low_balance = await check_low_balance(user, price)

    # Добавляем запись об активации в базу данных
    activation = await models.Activation.add_activation(
        user=user,
        activation_id=activation_id,
        country=country,
        service=service,
        cost=price,
        phone_number=phone_number,
        activation_expire_at=activation_expire_at + timedelta(minutes=10),
    )

    # Списываем средства с баланса пользователя
    user.balance -= price
    await user.save(update_fields=['balance'])

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
    # Если используется менеджер диалогов, сбрасываем стек состояний
    await manager.reset_stack()

    # Ждем 2 секунды перед отправкой уведомления о низком балансе, если это необходимо
    await asyncio.sleep(2)
    if low_balance:
        await send_low_balance_alert(user)


# Функция для отправки информации о сервисе
async def send_country_info(service_code: str, c: types.CallbackQuery, manager: DialogManager = None):
    """
    Отправляет информацию о сервисе пользователю и обрабатывает активацию номера.

    :param service_code: Код сервиса.
    :param c: Объект CallbackQuery от aiogram.
    :param manager: Менеджер диалогов от aiogram_dialog (опционально).
    """

    # Создаем экземпляр класса для получения SMS
    sms = SmsReceive()

    # Получаем список стран для указанного сервиса
    services = await sms.get_top_country(service=service_code)
    # Извлекаем список стран с ценами и увеличиваем цену на 30%
    countries_with_prices = [{"country": service["country"], "price": math.ceil(float(service["price"]) * 1.3)}
                             for service in services.values()]

    # Сортируем список стран по цене от меньшего к большему
    sorted_countries_with_prices = sorted(countries_with_prices, key=lambda x: x['price'])

    # Получаем словарь с именами стран
    country_name_mapping = await models.Country.get_country_name_mapping()

    # Заменяем идентификаторы стран на их имена
    for country in sorted_countries_with_prices:
        country["country"] = country_name_mapping.get(country["country"], "Unknown Country")

    # Передача данных через параметр data
    await manager.start(CountryMenu.select_country, mode=StartMode.NORMAL,
                        data={"countries_with_prices": sorted_countries_with_prices, "service_code": service_code})


# Функция для обработки выбора сервиса
async def on_select_service_old(c: types.CallbackQuery, widget: Select, manager: DialogManager, service_code: str):
    """
    Обрабатывает выбор сервиса пользователем и отправляет информацию о сервисе.

    :param c: Объект CallbackQuery от aiogram.
    :param widget: Виджет Select от aiogram_dialog.
    :param manager: Менеджер диалогов от aiogram_dialog.
    :param service_code: Код выбранного сервиса.
    """
    # print('on_select_service')
    ctx = manager.current_context()
    print(service_code)
    # country_id = int(ctx.start_data.get("country_id"))
    # await send_service_info(country_id, service_code, c, manager)


# Функция для обработки выбора сервиса
async def on_select_service(c: types.CallbackQuery, widget: Select, manager: DialogManager, service_code: str):
    """
    Обрабатывает выбор сервиса пользователем и отправляет информацию о сервисе.

    :param c: Объект CallbackQuery от aiogram.
    :param widget: Виджет Select от aiogram_dialog.
    :param manager: Менеджер диалогов от aiogram_dialog.
    :param service_code: Код выбранного сервиса.
    """
    await send_country_info(service_code, c, manager)


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
