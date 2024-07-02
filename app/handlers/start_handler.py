from datetime import timedelta
from typing import Union

import asyncio
from aiogram import types, F, Router
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_dialog import DialogManager, StartMode

from app.db import models
from app.dialogs.bot_menu import states
from app.dialogs.personal_cabinet.selected import send_payment_keyboard
from app.dialogs.personal_cabinet.states import PersonalMenu
from app.dialogs.receive_email.states import ReceiveEmailMenu
from app.dialogs.receive_sms.selected import send_country_info
from app.dialogs.receive_sms.states import CountryMenu, ServiceMenu
from app.services import bot_texts as bt
from app.services.keyboards import start_kb
from app.services.low_balance import check_low_balance, send_low_balance_alert
from app.services.need_subscribe import check_subscribe, send_subscribe_msg
from app.services.qr_code import generate_qr_code
from app.services.sms_receive import SmsReceive
from app.services.temp_mail import TempMail

router = Router()


@router.message(F.text == '/id')
async def get_id(message: types.Message):
    await message.answer(text=str(message.chat.id))


@router.callback_query(F.data == 'start')
@router.message(Command('start'))
async def start(message: Union[types.Message, types.CallbackQuery], dialog_manager: DialogManager,
                command: CommandObject):
    user = await models.User.get_user(message.from_user.id)
    if not user:
        refer_id = command.args
        if refer_id and refer_id.isdigit():
            refer_id = int(refer_id)
            refer = await models.User.get_or_none(telegram_id=refer_id)
            user = await models.User.add_user(message.from_user, refer)
        else:
            user = await models.User.add_user(message.from_user)

    if isinstance(message, types.CallbackQuery):
        await message.message.delete()

    else:
        start_arg = command.args
        if start_arg and start_arg.startswith('free_'):
            payment_link = await models.PaymentLink.get_payment_link(start_arg)
            if payment_link:
                if len(payment_link.user_id_list) >= payment_link.limit:
                    await message.answer(text='Лимит активаций исчерпан')
                    return

                elif message.from_user.id in payment_link.user_id_list:
                    await message.answer(text='Вы уже активировали эту ссылку')
                    return

                payment_link.user_id_list.append(user.telegram_id)
                await payment_link.save(update_fields=['user_id_list'])
                user.balance += payment_link.amount
                await user.save(update_fields=['balance'])
                await message.answer(text=f'Вам начислено {payment_link.amount}₽')
                return

    sub = await check_subscribe(user)
    if not sub:
        await send_subscribe_msg(user)
        return

    await message.answer(text=bt.MAIN_MENU, reply_markup=start_kb())


@router.callback_query(F.data == 'check_subscribe')
async def check_subscribe_handler(call: types.CallbackQuery):
    user = await models.User.get_user(call.from_user.id)
    sub = await check_subscribe(user)
    if sub:
        await call.message.delete()
        await call.message.answer(text=bt.MAIN_MENU, reply_markup=start_kb())
    else:
        await call.answer(text='Вы не подписаны на канал', show_alert=True)


@router.message(Command("get_sms"))
@router.message(F.text == bt.RECEIVE_SMS_BTN)
async def receive_sms(message: types.Message, dialog_manager: DialogManager):
    user = await models.User.get_user(message.from_user.id)
    sub = await check_subscribe(user)
    if not sub:
        await send_subscribe_msg(user)
        return
    # изменил CountryMenu.select_country на ServiceMenu.select_service
    await dialog_manager.start(ServiceMenu.select_service, mode=StartMode.RESET_STACK)


@router.message(Command("get_email"))
@router.message(F.text == bt.RECEIVE_EMAIL_BTN)
@router.callback_query(F.data == 'receive_email')
async def receive_email(message: Union[types.Message, types.CallbackQuery], dialog_manager: DialogManager):
    user = await models.User.get_user(message.from_user.id)
    if not user:
        return

    sub = await check_subscribe(user)
    if not sub:
        await send_subscribe_msg(user)
        return

    mails = await models.Mail.filter(user=user, is_paid_mail=False, is_active=True).all()
    if len(mails) > 0:
        mail = mails[-1]

    else:
        if isinstance(message, types.CallbackQuery):
            temp_mail = message.message
            await temp_mail.edit_text(text=bt.CREATING_EMAIL)
        else:
            temp_mail = await message.answer(text=bt.CREATING_EMAIL)

        tm = TempMail()
        email = await tm.generate_email()
        mail = await models.Mail.add_mail(user, email)
        await temp_mail.delete()

    await dialog_manager.start(ReceiveEmailMenu.receive_email,
                               data={"mail_id": mail.id},
                               mode=StartMode.RESET_STACK)


@router.message(Command("account"))
@router.message(F.text == bt.PERSONAL_CABINET_BTN)
async def personal_cabinet(message: types.Message, dialog_manager: DialogManager):
    user = await models.User.get_user(message.from_user.id)
    sub = await check_subscribe(user)
    if not sub:
        await send_subscribe_msg(user)
        return

    await dialog_manager.start(PersonalMenu.user_info, mode=StartMode.RESET_STACK)


@router.callback_query(F.data.startswith('mail:'))
async def mail_info(call: types.CallbackQuery):
    mail_id = int(call.data.split(':')[1])
    mail = await models.Mail.get_or_none(id=mail_id)
    if not mail:
        await call.answer()
        return

    msg_text = bt.PAID_EMAIL_INFO.format(email=mail.email, expire_at=mail.expire_at.strftime('%d.%m.%Y'))
    mk = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text=bt.RECEIVE_MY_EMAIL_BTN, callback_data=f'receive_my_mail:{mail.id}'),
            ],
            [
                types.InlineKeyboardButton(text=bt.EXTEND_EMAIL_BTN, callback_data=f'extend_email:{mail.id}')
            ],
            [
                types.InlineKeyboardButton(text=bt.BACK_BTN, callback_data='my_rent_emails')
            ]
        ]
    )
    await call.message.edit_text(text=msg_text, reply_markup=mk)


@router.callback_query(F.data == 'my_rent_emails')
async def my_rent_emails(call: types.CallbackQuery):
    user = await models.User.get_user(call.from_user.id)
    if not user:
        return

    mails = await models.Mail.filter(user=user, is_paid_mail=True).all()
    if len(mails) == 0:
        await call.answer(text='У вас нет арендованных почтовых ящиков', show_alert=True)
        return

    builder = InlineKeyboardBuilder()
    for mail in mails:
        builder.add(types.InlineKeyboardButton(text=mail.email, callback_data=f'mail:{mail.id}'))

    builder.button(text=bt.BACK_BTN, callback_data='receive_email')
    builder.adjust(1)

    await call.message.edit_text(text='Выберите почтовый ящик', reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith('receive_my_mail:'))
async def receive_my_mail(call: types.CallbackQuery):
    mail_id = int(call.data.split(':')[1])
    mail = await models.Mail.get_or_none(id=mail_id)
    if not mail:
        await call.answer()
        return

    mk = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text=bt.BACK_BTN, callback_data=f'mail:{mail.id}')
            ]
        ]
    )
    msg_text = bt.MY_RENT_EMAIL.format(email=mail.email, expire_at=mail.expire_at.strftime('%d.%m.%Y'))
    await call.message.edit_text(text=msg_text, reply_markup=mk)


@router.callback_query(F.data.startswith('extend_email:'))
async def extend_email(call: types.CallbackQuery):
    mail_id = int(call.data.split(':')[1])

    builder = InlineKeyboardBuilder()
    builder.button(text=bt.RENT_EMAIL_WEEK_BTN, callback_data=f'extend_email_week:{mail_id}')
    builder.button(text=bt.RENT_EMAIL_MONTH_BTN, callback_data=f'extend_email_month:{mail_id}')
    builder.button(text=bt.RENT_EMAIL_TWO_MONTHS_BTN, callback_data=f'extend_email_two_months:{mail_id}')
    builder.button(text=bt.RENT_EMAIL_SIX_MONTHS_BTN, callback_data=f'extend_email_six_months:{mail_id}')
    builder.button(text=bt.RENT_EMAIL_YEAR_BTN, callback_data=f'extend_email_year:{mail_id}')
    builder.button(text=bt.BACK_BTN, callback_data=f'mail:{mail_id}')
    builder.adjust(1)
    await call.message.edit_reply_markup(reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith('extend_email_'))
async def extend_email_confirm(call: types.CallbackQuery, state: FSMContext):
    data = call.data.split(':')[0]
    rent_data = {
        'extend_email_week': (99, 7, '1 неделя'),
        'extend_email_month': (199, 30, '1 месяц'),
        'extend_email_two_months': (369, 61, '2 месяца'),
        'extend_email_six_months': (599, 183, '6 месяцев'),
        'extend_email_year': (999, 365, '1 год'),
    }
    user = await models.User.get_user(call.from_user.id)
    if user.balance < rent_data[data][0]:
        await call.answer(text='Недостаточно средств', show_alert=True)
        return

    mail_id = int(call.data.split(':')[1])
    mail = await models.Mail.get_or_none(id=mail_id)
    msg_text = bt.CONFIRM_EXTEND_EMAIL.format(
        email=mail.email,
        rent_text=rent_data[data][2],
        cost=rent_data[data][0]
    )
    mk = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text=bt.CONFIRM_BTN, callback_data=f'confirm_{data}:{mail_id}')
            ],
            [
                types.InlineKeyboardButton(text=bt.BACK_BTN, callback_data=f'mail:{mail_id}')
            ]
        ]
    )
    await call.message.edit_text(text=msg_text, reply_markup=mk)


@router.callback_query(F.data.startswith('confirm_extend_email_'))
async def confirm_extend_email(call: types.CallbackQuery):
    mail_id = int(call.data.split(':')[1])
    mail = await models.Mail.get_or_none(id=mail_id)
    if not mail:
        await call.answer()
        return

    user = await models.User.get_user(call.from_user.id)
    if not user:
        return

    data = call.data.split(':')[0]
    rent_data = {
        'confirm_extend_email_week': (99, 7, '1 неделя'),
        'confirm_extend_email_month': (299, 30, '1 месяц'),
        'confirm_extend_email_two_months': (369, 61, '2 месяца'),
        'confirm_extend_email_six_months': (599, 183, '6 месяцев'),
        'confirm_extend_email_year': (999, 365, '1 год'),
    }
    if user.balance < rent_data[data][0]:
        await call.answer(text='Недостаточно средств', show_alert=True)
        return

    mail.expire_at += timedelta(days=rent_data[data][1])
    await mail.save(update_fields=['expire_at'])

    low_balance = await check_low_balance(user, rent_data[data][0])
    user.balance -= rent_data[data][0]
    await user.save(update_fields=['balance'])
    msg_text = bt.EXTEND_EMAIL_SUCCESS.format(
        email=mail.email,
        rent_text=rent_data[data][2]
    )
    await call.message.edit_text(text=msg_text)
    await call.answer()
    await asyncio.sleep(2)
    if low_balance:
        await send_low_balance_alert(user)


@router.callback_query(F.data.startswith('cancel_service:'))
async def cancel_service(call: types.CallbackQuery):
    activation_id = int(call.data.split(':')[1])
    activation = await models.Activation.get_or_none(id=activation_id)
    if not activation:
        await call.answer()
        return

    sms = SmsReceive()
    status = str(await sms.get_activation_status(activation.activation_id))
    if status == models.StatusResponse.STATUS_WAIT_CODE.name and activation.status == models.StatusResponse.STATUS_WAIT_CODE:
        cancel_status = str(await sms.set_activation_status(activation_id=activation.activation_id,
                                                            status=models.ActivationCode.CANCEL))
        if cancel_status == "EARLY_CANCEL_DENIED":
            await call.answer(text='Нельзя отменить номер в первые 2 минуты', show_alert=True)
            return

        if cancel_status != "ACCESS_CANCEL":
            await call.answer(text='Ошибка при отмене, попробуйте позже')
            return

        activation.activation_expire_at = None
        activation.status = models.StatusResponse.STATUS_CANCEL
        await activation.save()
        user = await models.User.get_user(telegram_id=call.from_user.id)
        user.balance += activation.cost
        await user.save()
        msg_text = bt.SERVICE_CANCEL
        await call.message.edit_text(text=msg_text)
    else:
        msg_text = 'Отмена больше не доступна'

    await call.message.edit_reply_markup()
    await call.answer(msg_text, show_alert=True)


@router.callback_query(F.data.startswith('continue_payment:'))
async def continue_payment(call: types.CallbackQuery, dialog_manager: DialogManager):
    payment_id = int(call.data.split(':')[1])
    payment = await models.Payment.get_or_none(id=payment_id)
    if not payment:
        await call.answer()
        return

    if 'email' in payment.continue_data:
        await dialog_manager.start(ReceiveEmailMenu.rent_email_confirm, data=payment.continue_data,
                                   mode=StartMode.RESET_STACK)

    else: # было (payment.continue_data['country_id'], payment.continue_data['service_code'], call, dialog_manager)
        await send_country_info(payment.continue_data['service_code'], call,
                                dialog_manager)


@router.callback_query(F.data.startswith('bonus_price:'))
async def bonus_price(call: types.CallbackQuery, dialog_manager: DialogManager):
    price = call.data.split(':')[1]
    user = await models.User.get_user(call.from_user.id)
    if not user:
        return

    if price == 'other':
        await call.message.edit_reply_markup()
        await dialog_manager.start(PersonalMenu.enter_amount, mode=StartMode.RESET_STACK)

    else:
        await send_payment_keyboard(call, price=float(price))
