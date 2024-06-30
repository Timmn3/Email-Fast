from typing import Union

from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Select, Button

from app.db import models
from app.dialogs.personal_cabinet.states import PersonalMenu
from app.services import bot_texts as bt
from app.services.freekassa import generate_fk_link
from app.services.keyboards import payment_kb
from app.services.lava import LavaApi


async def on_deposit(c: types.CallbackQuery, widget: Button, manager: DialogManager):
    """
    Обработчик для кнопки "Пополнить баланс".
    Переключает состояние диалога на меню пополнения баланса.

    :param c: Объект CallbackQuery.
    :param widget: Объект Button.
    :param manager: Объект DialogManager.
    """
    await manager.switch_to(PersonalMenu.deposit)


async def on_deposit_new(c: types.CallbackQuery, widget: Button, manager: DialogManager):
    """
    Обработчик для кнопки "Новое пополнение".
    Переключает состояние диалога на меню пополнения баланса с сохранением текущих данных.

    :param c: Объект CallbackQuery.
    :param widget: Объект Button.
    :param manager: Объект DialogManager.
    """
    ctx = manager.current_context()
    await manager.start(PersonalMenu.deposit, data=ctx.dialog_data)


async def on_deposit_state(c: types.CallbackQuery, widget: Button, manager: DialogManager):
    """
    Обработчик для кнопки "пополнение с установленным значением".
    Переключает состояние диалога на меню пополнения баланса с сохранением текущих данных.

    :param c: Объект CallbackQuery.
    :param widget: Объект Button.
    :param manager: Объект DialogManager.
    """
    ctx = manager.current_context()
    price = ctx.dialog_data['cost']
    ctx.dialog_data['price'] = price
    await send_payment_keyboard(c, manager=manager)


async def on_deposit_price(c: types.CallbackQuery, widget: Select, manager: DialogManager, price_id: str):
    """
    Обработчик для выбора суммы пополнения.
    Отправляет клавиатуру для выбора способа оплаты.

    :param c: Объект CallbackQuery.
    :param widget: Объект Select.
    :param manager: Объект DialogManager.
    :param price_id: Идентификатор выбранной суммы.
    """
    price = bt.prices_data[int(price_id) - 1]['price']
    ctx = manager.current_context()
    ctx.dialog_data['price'] = price
    await send_payment_keyboard(c, manager=manager, price=price)


async def on_other_price(c: types.CallbackQuery, widget: Button, manager: DialogManager):
    """
    Обработчик для кнопки "Другая сумма".
    Переключает состояние диалога на ввод суммы пополнения.

    :param c: Объект CallbackQuery.
    :param widget: Объект Button.
    :param manager: Объект DialogManager.
    """
    await manager.switch_to(PersonalMenu.enter_amount)


async def on_enter_other_price(m: types.Message, widget: TextInput, manager: DialogManager, price_text: str):
    """
    Обработчик для ввода другой суммы пополнения.
    Проверяет корректность введенной суммы и отправляет клавиатуру для выбора способа оплаты.

    :param m: Объект Message.
    :param widget: Объект TextInput.
    :param manager: Объект DialogManager.
    :param price_text: Введенная сумма пополнения.
    """
    if not price_text.isdigit():
        await m.answer(text='Сумма должна быть числом')
        await manager.switch_to(PersonalMenu.enter_amount)
        return

    price = int(price_text)
    if price < 10:
        await m.answer(text='Минимальная сумма - 10₽')
        await manager.switch_to(PersonalMenu.enter_amount)
        return

    ctx = manager.current_context()
    ctx.dialog_data['price'] = price
    await send_payment_keyboard(m, manager=manager, price=price)


async def send_payment_keyboard(m: Union[types.Message, types.CallbackQuery], manager: DialogManager = None,
                                price: float = None):
    """
    Отправляет клавиатуру для выбора способа оплаты.

    :param m: Объект Message или CallbackQuery.
    :param manager: Объект DialogManager.
    :param price: Сумма пополнения.
    """
    if manager:
        # Если передан менеджер диалогов, получаем текущий контекст
        ctx = manager.current_context()
        # Извлекаем сумму пополнения из данных диалога
        price = float(ctx.dialog_data['price'])
        # Получаем данные для продолжения диалога
        continue_data = ctx.start_data
    else:
        # Если менеджер не передан, данные для продолжения отсутствуют
        continue_data = None

    # Получаем пользователя по его ID
    user = await models.User.get_user(m.from_user.id)
    # Создаем экземпляр API для Lava
    lava = LavaApi()
    # Создаем запись о платеже в базе данных
    lava_payment = await models.Payment.create_payment(
        user=user,
        method=models.PaymentMethod.LAVA,
        amount=price,
        continue_data=continue_data
    )
    # Формируем идентификатор заказа
    order_id = f'sms_email_:{lava_payment.id}'
    # Создаем счет на оплату через Lava API
    response = await lava.create_invoice(price, order_id=order_id)
    # Извлекаем идентификатор счета из ответа API
    invoice_id = response['data']['id']
    # Сохраняем идентификатор счета и заказа в базе данных
    lava_payment.invoice_id = invoice_id
    lava_payment.order_id = order_id
    await lava_payment.save()
    # Получаем URL для оплаты через Lava
    lava_url = response['data']['url']

    # Создаем запись о платеже для FreeKassa
    payment = await models.Payment.create_payment(
        user=user,
        method=models.PaymentMethod.FREEKASSA,
        amount=price,
        continue_data=continue_data
    )
    # Генерируем ссылки для оплаты через FreeKassa
    sbp_url = generate_fk_link(price, payment.id, method_id=42)
    other_url = generate_fk_link(price, payment.id)
    if manager:
        # Сбрасываем стек диалогов, если передан менеджер
        await manager.reset_stack()
    # Создаем клавиатуру с кнопками для выбора способа оплаты
    builder = InlineKeyboardBuilder()
    builder.button(text=bt.METHOD_BANK_CARD_BTN, web_app=types.WebAppInfo(url=lava_url))
    if price >= 300:
        # Добавляем кнопки для оплаты через SBP и криптовалюту, если сумма >= 300
        builder.button(text=bt.METHOD_SBP_BTN, web_app=types.WebAppInfo(url=sbp_url))
        builder.button(text=bt.METHOD_CRYPTO_BTN, web_app=types.WebAppInfo(url=other_url))
    # Добавляем кнопку для других способов оплаты
    builder.button(text=bt.METHOD_OTHER_BTN, web_app=types.WebAppInfo(url=other_url))
    builder.adjust(1)

    if isinstance(m, types.Message):
        # Отправляем сообщение с клавиатурой, если m является объектом Message
        await m.answer(text=bt.SELECT_DEPOSIT_METHOD, reply_markup=builder.as_markup())
    else:
        # Редактируем текст сообщения с клавиатурой, если m является объектом CallbackQuery
        await m.message.edit_text(text=bt.SELECT_DEPOSIT_METHOD, reply_markup=builder.as_markup())