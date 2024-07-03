from math import floor

from aiogram.utils.keyboard import InlineKeyboardBuilder
from fastapi import FastAPI, Query
import uvicorn
from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response
from tortoise import timezone

from app import dependencies
from app.db import models
from app.db.database import init_db
from app.dependencies import bot
from app.services import bot_texts as bt


async def on_startup():
    await init_db()

# Создаем экземпляр FastAPI
app = FastAPI()

@app.on_event("startup")
async def startup_event():
    await init_db()


@app.get("/fk")
async def read_item(
        request: Request,
        MERCHANT_ID: str = Query(None),
        AMOUNT: str = Query(None),
        intid: str = Query(None),
        MERCHANT_ORDER_ID: str = Query(None),
        P_EMAIL: str = Query(None),
        P_PHONE: str = Query(None),
        CUR_ID: str = Query(None),
        payer_account: str = Query(None),
        us_field1: str = Query(None),
        us_field2: str = Query(None),
        SIGN: str = Query(None)
):
    allowed_ips = ['168.119.157.136', '168.119.60.227', '138.201.88.124', '178.154.197.79']
    if not request.client.host in allowed_ips:
        return PlainTextResponse("IP not allowed")

    if str(MERCHANT_ID) == str(dependencies.FK_SHOP_ID):
        payment = await models.Payment.get_or_none(id=int(MERCHANT_ORDER_ID))
        if not payment:
            return PlainTextResponse("NO")

        if payment.method != models.PaymentMethod.FREEKASSA:
            return

        if payment.amount != float(AMOUNT):
            return PlainTextResponse("NO")

        payment.is_success = True
        await payment.save()
        await payment.fetch_related('user')
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

        builder = InlineKeyboardBuilder()
        if payment.continue_data:
            builder.button(text=bt.CONTINUE_BTN, callback_data=f'continue_payment:{payment.id}')
        try:
            await bot.send_message(
                chat_id=payment.user.telegram_id,
                text=bt.PAYMENT_SUCCESS.format(amount=int(amount)),
                reply_markup=builder.as_markup()
            )
        except:
            pass

        return PlainTextResponse("YES")

    return PlainTextResponse("NO")


@app.post("/https://emailfast.info/payok")
async def payok(request: Request):
    data = await request.form()
    # print(data, flush=True)
    return Response(status_code=200)


uvicorn.run(app, host='emailfast.info', port=443, ssl_keyfile='private.key', ssl_certfile='certificate.crt')
