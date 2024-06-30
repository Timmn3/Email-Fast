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
        ctx = manager.current_context()
        price = float(ctx.dialog_data['price'])
        continue_data = ctx.start_data
    else:
        continue_data = None

    user = await models.User.get_user(m.from_user.id)
    lava = LavaApi()
    lava_payment = await models.Payment.create_payment(
        user=user,
        method=models.PaymentMethod.LAVA,
        amount=price,
        continue_data=continue_data
    )
    order_id = f'sms_email_:{lava_payment.id}'
    response = await lava.create_invoice(price, order_id=order_id)
    invoice_id = response['data']['id']
    lava_payment.invoice_id = invoice_id
    lava_payment.order_id = order_id
    await lava_payment.save()
    lava_url = response['data']['url']

    payment = await models.Payment.create_payment(
        user=user,
        method=models.PaymentMethod.FREEKASSA,
        amount=price,
        continue_data=continue_data
    )
    sbp_url = generate_fk_link(price, payment.id, method_id=42)
    other_url = generate_fk_link(price, payment.id)
    if manager:
        await manager.reset_stack()
    builder = InlineKeyboardBuilder()
    builder.button(text=bt.METHOD_BANK_CARD_BTN, web_app=types.WebAppInfo(url=lava_url))
    if price >= 300:
        builder.button(text=bt.METHOD_SBP_BTN, web_app=types.WebAppInfo(url=sbp_url))
        builder.button(text=bt.METHOD_CRYPTO_BTN, web_app=types.WebAppInfo(url=other_url))
    builder.button(text=bt.METHOD_OTHER_BTN, web_app=types.WebAppInfo(url=other_url))
    builder.adjust(1)

    if isinstance(m, types.Message):
        await m.answer(text=bt.SELECT_DEPOSIT_METHOD, reply_markup=builder.as_markup())
    else:
        await m.message.edit_text(text=bt.SELECT_DEPOSIT_METHOD, reply_markup=builder.as_markup())

# async def on_deposit_method(c: types.CallbackQuery, widget: Button, manager: DialogManager):
#     ctx = manager.current_context()
#     price = float(ctx.dialog_data['price'])
#     method = widget.widget_id
#     user = await models.User.get_user(c.from_user.id)
#     if method == 'bank_card':
#         lava = LavaApi()
#         payment = await models.Payment.create_payment(
#             user=user,
#             method=models.PaymentMethod.LAVA,
#             amount=price
#         )
#         order_id = f'sms_email:{payment.id}'
#         response = await lava.create_invoice(price, order_id=order_id)
#         if response['status'] == 200:
#             invoice_id = response['data']['id']
#             payment.invoice_id = invoice_id
#             payment.order_id = order_id
#             await payment.save()
#             await manager.reset_stack()
#             msg_text = bt.PAYMENT_INFO_MSG.format(
#                 payment_id=payment.id,
#                 amount=price,
#                 method='Банковская карта'
#             )
#             await c.message.edit_text(
#                 text=msg_text,
#                 reply_markup=payment_kb(response['data']['url'])
#             )
#
#     elif method == 'sbp':
#         payment = await models.Payment.create_payment(
#             user=user,
#             method=models.PaymentMethod.FREEKASSA,
#             amount=price
#         )
#         url = generate_fk_link(price, payment.id, method_id=42)
#         await manager.reset_stack()
#         msg_text = bt.PAYMENT_INFO_MSG.format(
#             payment_id=payment.id,
#             amount=price,
#             method='СБП'
#         )
#         await c.message.edit_text(
#             text=msg_text,
#             reply_markup=payment_kb(url)
#         )
#
#     elif method == 'crypto' or method == 'other':
#         payment = await models.Payment.create_payment(
#             user=user,
#             method=models.PaymentMethod.FREEKASSA,
#             amount=price
#         )
#         url = generate_fk_link(price, payment.id)
#         await manager.reset_stack()
#         if method == 'crypto':
#             method_name = 'Криптовалюта'
#         else:
#             method_name = 'Другое'
#
#         msg_text = bt.PAYMENT_INFO_MSG.format(
#             payment_id=payment.id,
#             amount=price,
#             method=method_name
#         )
#         await c.message.edit_text(
#             text=msg_text,
#             reply_markup=payment_kb(url)
#         )
#
#     else:
#         await c.answer(text='Недоступно', show_alert=True)
