import hashlib

from app import dependencies


def generate_fk_link(amount: float, order_id: int, method_id: int = None):
    currency = 'RUB'
    sign = hashlib.md5(f'{dependencies.FK_SHOP_ID}:{amount}:{dependencies.FK_SECRET_KEY}:{currency}:{order_id}'.encode()).hexdigest()
    url = f'https://pay.freekassa.ru/?m={dependencies.FK_SHOP_ID}&oa={amount}&currency={currency}&o={order_id}&s={sign}'
    if method_id:
        url += f'&i={method_id}'
    return url
