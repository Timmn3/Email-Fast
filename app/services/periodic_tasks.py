import asyncio
import json
from math import floor

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import ClientSession
from tortoise import timezone

from app import dependencies
from app.db import models
from app.dependencies import bot
from app.services.lava import LavaApi
from app.services.sms_receive import SmsReceive
from app.services.temp_mail import TempMail
from app.services import bot_texts as bt


async def check_payment():
    payments = await models.Payment.get_lava_payments()
    for payment in payments:
        lava = LavaApi()
        response = await lava.get_invoice_status(payment.order_id, payment.invoice_id)
        if response['status'] == 200:
            invoice = response['data']
            if invoice['status'] == 'success':
                payment.is_success = True
                await payment.save()
                if payment.user.bonus_end_at and payment.user.bonus_end_at > timezone.now():
                    amount = floor(payment.amount * 1.1)
                    payment.user.bonus_end_at = None
                else:
                    amount = payment.amount

                payment.user.balance += amount
                await payment.user.save()
                if payment.user.refer_id:
                    refer = await models.User.get_or_none(id=payment.user.refer_id)
                    if refer:
                        ref_bonus = int(dependencies.REF_BONUS) / 100
                        ref_sum = round(payment.amount * ref_bonus, 1)
                        refer.ref_balance += ref_sum
                        refer.total_ref_earnings += ref_sum
                        await refer.save()

                try:
                    builder = InlineKeyboardBuilder()
                    if payment.continue_data:
                        builder.button(text=bt.CONTINUE_BTN, callback_data=f'continue_payment:{payment.id}')

                    await bot.send_message(
                        chat_id=payment.user.telegram_id,
                        text=bt.PAYMENT_SUCCESS.format(amount=int(amount)),
                        reply_markup=builder.as_markup()
                    )
                except:
                    pass


async def check_sms():
    activations = await models.Activation.get_active_activations()
    sms = SmsReceive()
    for activation in activations:
        status = str(await sms.get_activation_status(activation.activation_id))
        if status.startswith(models.StatusResponse.STATUS_OK.name):
            activation.status = models.StatusResponse.STATUS_OK
            activation.sms_text = status.split(':')[1]
            activation.activation_expire_at = None
            await activation.save()
            await activation.fetch_related('user', 'service')
            msg_text = f"""
💬<b>Новое SMS</b> на номер: +{activation.phone_number}

Ваш код активации для <b>{activation.service.name}</b>:
<code>{activation.sms_text}</code>
"""
            await bot.send_message(
                chat_id=activation.user.telegram_id,
                text=msg_text
            )

    activations = await models.Activation.get_expired_activations()
    for activation in activations:
        activation.status = models.StatusResponse.STATUS_CANCEL
        await activation.save()
        activation.user.balance += activation.cost
        await activation.user.save()


async def check_email():
    expired_emails = await models.Mail.get_expired_mails()
    for mail in expired_emails:
        mail.is_active = False
        await mail.save()
        await asyncio.sleep(0)

    mails = await models.Mail.filter(is_active=True).all().prefetch_related('user')
    for mail in mails:
        tm = TempMail()
        login, domain = mail.email.split('@')
        message_ids = await tm.get_message_ids(login, domain)
        for message_id in message_ids:
            if not mail.is_paid_mail and len(mail.old_messages_id) > 10:
                return

            if message_id not in mail.old_messages_id:
                message = await tm.read_message(login, domain, message_id)
                mail.old_messages_id.append(message_id)
                await mail.save()
                await models.Letter.add_letter(
                    mail=mail,
                    user=mail.user,
                    text=message.text
                )
                msg_text = f'📩<b>Новое сообщение</b> на почту: <b>{mail.email}</b>\n\n<b>От кого:</b> {message.from_}\n<b>Тема:</b> {message.subject}\n\n{message.text}'

                await bot.send_message(
                    chat_id=mail.user.telegram_id,
                    text=msg_text
                )

            await asyncio.sleep(0)


async def get_services_names():
    data = {
        'act': 'getServicesList',
        'csrf': ''
    }
    url = 'https://sms-activate.org/api/api.php'
    async with ClientSession() as session:
        async with session.post(url=url, data=data) as response:
            data = json.loads(await response.text())

    services_dict = {}
    for service in data['data']:
        services_dict[service['code']] = service['name'].replace('<small>+переадресация</small>', '')
        await asyncio.sleep(0)

    return services_dict


async def update_countries_and_services():
    sms = SmsReceive()
    countries = await sms.get_countries()
    countries_db_ids = await models.Country.get_country_id_list()
    for country in countries:
        await models.Country.get_or_create(country_id=country["id"], name=country["name"])
        try:
            countries_db_ids.remove(int(country["id"]))
        except ValueError:
            pass

        await asyncio.sleep(0)

    for country_id in countries_db_ids:
        country = await models.Country.get_country_by_id(country_id)
        await country.delete()

    services = await sms.get_services()
    services_dict = await get_services_names()
    services_db_codes = await models.Service.get_codes_list()
    for service in services:
        service_obj = await models.Service.get_service(code=service["code"])
        if service_obj is None:
            await models.Service.add_service(
                code=service["code"],
                name=services_dict[service["code"]],
                search_names=service["search_names"]
            )
        else:
            service_obj.name = services_dict[service["code"]]
            service_obj.search_names = service["search_names"]
            await service_obj.save()

        try:
            services_db_codes.remove(service["code"])
        except ValueError:
            pass

        await asyncio.sleep(0)

    for service_code in services_db_codes:
        service = await models.Service.get_service(code=service_code)
        await service.delete()
