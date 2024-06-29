from datetime import datetime, timedelta
from enum import Enum, IntEnum

from aiogram import types
from tortoise.models import Model
from tortoise import fields, timezone


class StatusResponse(IntEnum):
    STATUS_WAIT_CODE = 1
    STATUS_WAIT_RETRY = 2
    STATUS_WAIT_RESEND = 3
    STATUS_CANCEL = 4
    STATUS_OK = 5


class ActivationResponse(Enum):
    ACCESS_READY = 1
    ACCESS_RETRY_GET = 2
    ACCESS_ACTIVATION = 3
    ACCESS_CANCEL = 4


class ActivationCode(Enum):
    SUCCESS = 1
    RETRY_GET = 3
    FINISH = 6
    CANCEL = 8


class PaymentMethod(Enum):
    LAVA = 'lava'
    PAYOK = 'payok'
    FREEKASSA = 'freekassa'


class User(Model):
    class Meta:
        table = "users"
        table_description = "Users"
        ordering = ["id"]

    id: int = fields.BigIntField(pk=True)
    telegram_id: int = fields.BigIntField(unique=True)
    full_name: str = fields.CharField(max_length=128)
    username: str = fields.CharField(max_length=64, null=True)
    mention: str = fields.CharField(max_length=64, null=True)
    balance: float = fields.FloatField(default=0)
    ref_balance: float = fields.FloatField(default=0)
    total_ref_earnings: float = fields.FloatField(default=0)
    refer_id: int = fields.BigIntField(null=True)
    bonus_end_at: datetime = fields.DatetimeField(null=True)
    in_channel: bool = fields.BooleanField(default=False)
    last_check_in: datetime = fields.DatetimeField(null=True)
    created_at: datetime = fields.DatetimeField(auto_now_add=True)

    @classmethod
    async def add_user(cls, user: types.User, refer: types.User = None):
        user = await cls.create(
            telegram_id=user.id,
            full_name=user.full_name,
            username=user.username,
            mention=f'@{user.username}' if user.username else user.full_name,
            refer_id=refer.id if refer else None
        )
        return user

    @classmethod
    async def get_user(cls, telegram_id: int):
        return await cls.get_or_none(telegram_id=telegram_id)

    def __str__(self):
        return self.mention


class Country(Model):
    class Meta:
        table = "countries"
        table_description = "Countries"
        ordering = ["id"]

    id: int = fields.IntField(pk=True)
    country_id: int = fields.IntField(unique=True, index=True)
    name: str = fields.CharField(max_length=128, unique=True)

    def to_dict(self):
        return {
            'country_id': self.country_id,
            'name': self.name
        }

    @classmethod
    async def add_country(cls, country_id: int, name: str):
        country = await cls.create(
            country_id=country_id,
            name=name
        )
        return country

    @classmethod
    async def get_country_by_id(cls, country_id: int):
        return await cls.get_or_none(country_id=country_id)

    @classmethod
    async def get_country_id_list(cls):
        return await cls.all().values_list('country_id', flat=True)

    @classmethod
    async def search_countries(cls, search_name: str):
        return await cls.filter(name__icontains=search_name).all()

    def __str__(self):
        return self.name


class Service(Model):
    class Meta:
        table = "services"
        table_description = "Services"
        ordering = ["id"]

    id: int = fields.IntField(pk=True)
    code: str = fields.CharField(max_length=128, unique=True, index=True)
    name: str = fields.CharField(max_length=128, null=True)
    search_names: str = fields.TextField(null=True)
    used_count: int = fields.IntField(default=0)

    @classmethod
    async def add_service(cls, code: str, name: str, search_names: str):
        service = await cls.create(
            code=code,
            name=name,
            search_names=search_names
        )
        return service

    @classmethod
    async def get_service(cls, code: str):
        return await cls.get_or_none(code=code)

    @classmethod
    async def search_service(cls, search_name: str):
        return await cls.filter(search_names__icontains=search_name).all()

    @classmethod
    async def get_codes_list(cls):
        return await cls.all().values_list('code', flat=True)


class Mail(Model):
    class Meta:
        table = "mails"
        table_description = "Mails"
        ordering = ["id"]

    id: int = fields.BigIntField(pk=True)
    user: User = fields.ForeignKeyField('models.User', related_name='mails')
    email: str = fields.CharField(max_length=128, unique=True, index=True)
    old_messages_id: list = fields.JSONField(default=[])
    is_paid_mail: bool = fields.BooleanField(default=False)
    is_active: bool = fields.BooleanField(default=True)
    created_at: datetime = fields.DatetimeField(auto_now_add=True)
    expire_at: datetime = fields.DatetimeField()

    @classmethod
    async def add_mail(cls, user: User, email: str):
        expire_at = timezone.now() + timedelta(minutes=30)
        mail = await cls.create(
            user=user,
            email=email,
            expire_at=expire_at
        )
        return mail

    @classmethod
    async def get_mail(cls, mail_id: str):
        return await cls.get_or_none(id=mail_id)

    @classmethod
    async def get_user_mails(cls, user: User):
        return await cls.filter(user=user).all()

    @classmethod
    async def get_expired_mails(cls):
        return await cls.filter(expire_at__lte=timezone.now()).all()


class Letter(Model):
    class Meta:
        table = "letters"
        table_description = "Letters"
        ordering = ["id"]

    id: int = fields.BigIntField(pk=True)
    user: User = fields.ForeignKeyField('models.User', related_name='letters')
    mail: Mail = fields.ForeignKeyField('models.Mail', related_name='letters')
    text: str = fields.TextField()
    created_at: datetime = fields.DatetimeField(auto_now_add=True)

    @classmethod
    async def add_letter(cls, user: User, mail: Mail, text: str):
        letter = await cls.create(
            user=user,
            mail=mail,
            text=text
        )
        return letter

    @classmethod
    async def get_letter(cls, letter_id: int):
        return await cls.get_or_none(id=letter_id)

    @classmethod
    async def get_user_letters(cls, user: User):
        return await cls.filter(user=user).all()



class Activation(Model):
    class Meta:
        table = "activations"
        table_description = "Activations"
        ordering = ["id"]

    id: int = fields.BigIntField(pk=True)
    user: User = fields.ForeignKeyField('models.User', related_name='activations')
    activation_id: int = fields.BigIntField(unique=True, index=True)
    country: Country = fields.ForeignKeyField('models.Country', related_name='activations')
    service: Service = fields.ForeignKeyField('models.Service', related_name='activations')
    cost: float = fields.FloatField()
    phone_number: str = fields.CharField(max_length=32)
    sms_text: str = fields.TextField(null=True)
    status: StatusResponse = fields.IntEnumField(StatusResponse, default=StatusResponse.STATUS_WAIT_CODE)
    created_at: datetime = fields.DatetimeField(auto_now_add=True)
    activation_expire_at: datetime = fields.DatetimeField(null=True)

    @classmethod
    async def add_activation(cls, user: User, activation_id: int, country: Country, cost: float,
                             service: Service, phone_number: str, activation_expire_at: datetime):
        activation = await cls.create(
            user=user,
            activation_id=activation_id,
            country=country,
            service=service,
            cost=cost,
            phone_number=phone_number,
            activation_expire_at=activation_expire_at
        )
        return activation

    @classmethod
    async def get_activation(cls, activation_id: int):
        return await cls.get_or_none(activation_id=activation_id)

    @classmethod
    async def get_user_activations(cls, user: User):
        return await cls.filter(user=user).all()

    @classmethod
    async def get_expired_activations(cls):
        return await cls.filter(activation_expire_at__lte=timezone.now(), status=StatusResponse.STATUS_WAIT_CODE).all().prefetch_related('user')

    @classmethod
    async def get_active_activations(cls):
        return await cls.filter(activation_expire_at__gt=timezone.now()).all()


class Payment(Model):
    class Meta:
        table = "payments"
        table_description = "Payments"
        ordering = ["id"]

    id: int = fields.BigIntField(pk=True)
    user: User = fields.ForeignKeyField('models.User', related_name='payments')
    method: PaymentMethod = fields.CharEnumField(PaymentMethod, max_length=16)
    amount: float = fields.FloatField()
    order_id: str = fields.CharField(max_length=128, unique=True, index=True, null=True)
    invoice_id: str = fields.CharField(max_length=128, unique=True, index=True, null=True)
    continue_data: dict = fields.JSONField(null=True)
    is_success: bool = fields.BooleanField(default=False)
    created_at: datetime = fields.DatetimeField(auto_now_add=True)

    @classmethod
    async def create_payment(cls, user: User, method: PaymentMethod, amount: float, continue_data: dict = None):
        payment = await cls.create(
            user=user,
            method=method,
            amount=amount,
            continue_data=continue_data
        )
        return payment

    @classmethod
    async def get_lava_payments(cls):
        return await cls.filter(method=PaymentMethod.LAVA, is_success=False,
                                created_at__gt=timezone.now() - timedelta(hours=5),
                                order_id__isnull=False).all().prefetch_related('user')


class Withdraw(Model):
    class Meta:
        table = "withdraws"
        table_description = "Withdraws"
        ordering = ["id"]

    id: int = fields.BigIntField(pk=True)
    user: User = fields.ForeignKeyField('models.User', related_name='withdraws')
    requisites: str = fields.TextField()
    amount: float = fields.FloatField()
    is_success: bool = fields.BooleanField(null=True)
    created_at: datetime = fields.DatetimeField(auto_now_add=True)

    @classmethod
    async def add_withdraw(cls, user: User, requisites: str, amount: float):
        withdraw = await cls.create(
            user=user,
            requisites=requisites,
            amount=amount
        )
        return withdraw

    @classmethod
    async def get_withdraw(cls, withdraw_id: int):
        return await cls.get_or_none(id=withdraw_id)


class PaymentLink(Model):
    class Meta:
        table = "payment_links"
        table_description = "PaymentLinks"
        ordering = ["id"]

    id: int = fields.BigIntField(pk=True)
    payment_link_id: str = fields.CharField(max_length=32, unique=True, index=True)
    user_id_list: list = fields.JSONField(default=[])
    amount: float = fields.FloatField()
    limit: int = fields.IntField()
    created_at: datetime = fields.DatetimeField(auto_now_add=True)

    @classmethod
    async def add_payment_link(cls, amount: float, limit: int, payment_link_id: str):
        payment_link = await cls.create(
            amount=amount,
            limit=limit,
            payment_link_id=payment_link_id
        )
        return payment_link

    @classmethod
    async def get_payment_link(cls, payment_link_id: str):
        return await cls.get_or_none(payment_link_id=payment_link_id)
