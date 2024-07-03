# ========================= Messages =========================

MAIN_MENU = """
Привет👋🏻 

Выбери нужное действие⤵️
"""

SELECT_COUNTRY = 'Выберите страну⤵️'
SELECT_SERVICE = 'Выберите сервис⤵️'

ENTER_COUNTRY = "Введите наименование страны на русском языке⤵️"
ENTER_SERVICE = "Введите название необходимого сервиса"

ENTER_COUNTRY_ERROR = "Страна не найдена. Проверьте правильность ввода"
ENTER_SERVICE_ERROR = """
Данный сервис не найден. 

Проверьте правильность ввода, либо выберите <b>«Другой сервис»</b>
"""

SERVICE_INFO = """
<b>Ваш номер⤵️</b>
<code>+{phone}</code>

<b>Сервис:</b> {service}

Ожидаем SMS...

<i>- Номер удалится автоматически через 10 минут, если на него не придет сообщение.
- Срок жизни номера 20 минут.</i>
"""

SERVICE_CANCEL = """
<b>⛔️Номер отменен</b>

💰Деньги вернулись на баланс.
"""

NOT_ENOUGH_BALANCE = """
<b>Недостаточно средств</b>

Для оплаты требуется <code>{cost}</code> руб.

Ваш баланс: <code>{balance}</code> руб.
"""

NOT_ENOUGH_BALANCE_ALERT = "Недостаточно средств"

MY_EMAIL = """
<b>Ваш почтовый ящик⤵️</b>
{email}

<i>Ожидаем письмо...</i>

⚠️ Срок жизни почтового ящика - <b>30 минут.</b>
"""

MY_RENT_EMAIL = """
<b>Ваш почтовый ящик⤵️</b>
{email}

<i>Ожидаем письмо...</i>

⚠️ Арендован до: <b>{expire_at}</b>
"""

CONFIRM_RENT_EMAIL = """
<b>Вы собираетесь арендовать почтовый ящик ⤵️</b>
{dialog_data[email]}

Срок: <b>{dialog_data[rent_text]}</b>
Стоимость: <b>{dialog_data[cost]}₽</b>
"""

CONFIRM_EXTEND_EMAIL = """
<b>Вы собираетесь продлить почтовый ящик:</b>
{email}

Срок: <b>{rent_text}</b>
Стоимость: <b>{cost}₽</b>
"""

RENT_EMAIL_SUCCESS = """
Почтовый ящик <b>{dialog_data[email]}</b> успешно арендован!
Срок: {dialog_data[rent_text]}
"""

EXTEND_EMAIL_SUCCESS = """
Вы успешно продлили почтовый ящик <b>{email}</b> на <b>{rent_text}</b>
"""

PAID_EMAIL_INFO = """
<b>Почтовый ящик:</b> {email}

Арендован до: <b>{expire_at}</b>
"""

CREATING_EMAIL = "<b>Создание почтового ящика...</b>"

PERSONAL_CABINET = """
<b>ID:</b> <code>{user_id}</code>

<b>Мой кошелек:</b> <code>{balance}₽</code>
<b>Мой партнерский счет:</b> <code>{ref_balance}₽</code>
"""

SELECT_DEPOSIT_PRICE = "Выберите сумму пополнения⤵️"
SELECT_DEPOSIT_METHOD = "Выберите способ пополнения⤵️"
ENTER_DEPOSIT_AMOUNT = "Введите сумму пополнения"

PAYMENT_INFO_MSG = """
<b>Оплата счета №{payment_id}</b>

<b>Сумма:</b> <code>{amount}₽</code>
<b>Способ оплаты:</b> <code>{method}</code>

<i>Для оплаты нажмите кнопку <b>"Оплатить"</b></i>
"""

PAYMENT_SUCCESS = """
<b>Ваш баланс пополнен на <code>{amount}₽</code></b>
"""

AFFILIATE_PROGRAM_TEXT = """
🤝<b>Партнёрская программа</b>

Приводи друзей и зарабатывай 10% с их пополнений, пожизненно!

⬇️<b>Твоя реферальная ссылка:</b>
└ {link}

🏅Статистика:
├ Лично приглашённых: <b>{ref_count}</b>
├ Количество оплат: <b>{payment_count}</b>
├ Всего заработано: <b>{ref_balance_total}₽</b>
└ Доступно к выводу: <b>{ref_balance}₽</b>
"""

SHARE_BOT_TEXT = """

Пользователь {mention} приглашает вас в сервис приема СМС и Email сообщений.
{link}"""

WITHDRAW_TEXT = """
Вы можете вывести средства на банковскую карту, либо на баланс бота для оплаты наших услуг.
"""
ENTER_WITHDRAW_AMOUNT = "Введите сумму вывода"
ENTER_WITHDRAW_CARD = "Отправьте реквизиты банковской карты"

WITHDRAW_INFO = """
<b>Вывод средств</b>

<b>Сумма:</b> <code>{amount}₽</code>
<b>Реквизиты:</b> <code>{requisites}</code>

<i>Для подтверждения вывода нажмите кнопку <b>"Подтвердить"</b></i>
"""


ADMIN_STAT = """
<b>Количество пользователей:</b> {users_count}
<b>За сегодня:</b> {users_count_today}

<b>Получено:</b> {received_count}
<b>SMS</b> - {received_sms_count}
<b>Email</b> - {received_email_count}

<b>За сегодня:</b> {received_count_today}
<b>SMS</b> - {received_sms_count_today}
<b>Email</b> - {received_email_count_today}

<b>Арендованных Email:</b> {rent_email_count}
<b>За сегодня:</b> {rent_email_count_today}

<b>Пополнений:</b> {payments_count}
<b>Повторные оплаты:</b> {payments_repeat_count}
<b>Пополнений за сегодня:</b> {payments_count_today} ({payments_amount_today} руб.)
"""

AFFILIATE_STAT = """
<b>Партнерская статистика:</b>

<code>{stat}</code>
"""

LOW_BALANCE_ALERT = """
⚠️Заканчивается баланс!

Успей пополнить в течение 24 часов и получи на счёт +10% от суммы пополнения ⤵️
"""

NOT_NUMBERS_ALERT = "Для данного сервиса нет доступных номеров. Попробуйте позже"

# Для продолжения подпишитесь на наш канал
SUBSCRIBE_CHANNEL = """
Для продолжения подпишитесь на наш канал
"""


# ========================= Buttons =========================

# Default
CONFIRM_BTN = '✅Подтвердить'
DECLINE_BTN = '❌Отклонить'
CONTINUE_BTN = '🔁Продолжить'
BACK_BTN = '« Назад'

# Start menu
RECEIVE_SMS_BTN = '📲Принять SMS'
RECEIVE_EMAIL_BTN = '📩Принять Email'
PERSONAL_CABINET_BTN = '👤Личный кабинет'
AFFILIATE_PROGRAM_BTN = '💰Партнерская программа'

# Country menu
SEARCH_COUNTRY_BTN = '🔎Поиск страны'
ENTER_AGAIN_BTN = 'Ввести заново'

# Service menu
SEARCH_SERVICE_BTN = '🔎Поиск сервиса'
OTHER_SERVICE_BTN = 'Другой сервис'
CANCEL_SERVICE_BTN = '↩️Отменить аренду номера'

# Personal cabinet
DEPOSIT_BTN = '💵Пополнить баланс'
SUPPORT_BTN = '🙋‍♂️Поддержка'

# Receive email
CHANGE_EMAIL_BTN = '🔄Сменить почтовый ящик'
RENT_EMAIL_BTN = '📬Арендовать почтовый ящик'
MY_RENT_EMAILS_BTN = '📨Мои ящики'

# Rent email
RENT_EMAIL_WEEK_BTN = 'Неделя, 99₽'
RENT_EMAIL_MONTH_BTN = 'Месяц, 199₽'
RENT_EMAIL_TWO_MONTHS_BTN = '2 месяца, 369₽'
RENT_EMAIL_SIX_MONTHS_BTN = '6 месяцев, 599₽'
RENT_EMAIL_YEAR_BTN = 'Год, 999₽'

# Personal cabinet
OTHER_DEPOSIT_PRICE_BTN = 'Другая сумма'

METHOD_BANK_CARD_BTN = 'Банковская карта'
METHOD_SBP_BTN = 'СБП (Переводом)'
METHOD_CRYPTO_BTN = 'Криптовалюта'
METHOD_OTHER_BTN = 'Другие способы'

PAY_BTN = 'Оплатить'


# Affiliate program
SHARE_LINK_BTN = 'Поделиться ссылкой'
WITHDRAW_BTN = 'Вывод средств'

ON_BANK_CARD_BTN = 'На банковскую карту'
ON_BALANCE_BTN = 'На баланс бота'

# My emails
RECEIVE_MY_EMAIL_BTN = '✉️Принять Email'
EXTEND_EMAIL_BTN = '📬Продлить аренду'

# Subscribe channel
SUBSCRIBE_CHANNEL_BTN = '↗️Перейти и подписаться'
READY_SUBSCRIBE_CHANNEL_BTN = '✅Я подписался'


# ========================= Data =========================
prices_data = [
    {'id': 1, 'price': 100},
    {'id': 2, 'price': 250},
    {'id': 3, 'price': 500},
    {'id': 4, 'price': 1000}
]

CHANNEL_LINK = 'https://t.me/neuronbo'


SERVICES = [
    "Вконтакте",
    "Whatsapp",
    "Viber",
    "Discord",
    "Twitch",
    "Банки",
    "Blizzard",
    "Faceit",
    "FunPay",
    "TikTok/Douyin",
    "Telegram",
    "Snapchat",
    "Facebook",
    "LinkedIN",
    "Instagram+Threads",
    "Одноклассники",
    "Badoo",
    "BIGO LIVE",
    "Tinder",
    "LoveRu",
    "МирЗнакомств",
    "Mylove",
    "AliExpress",
    "Яндекс",
    "KIO",
    "Google",
    "Netflix",
    "eBay",
    "PayPal",
    "Familia",
    "Payoneer",
    "Yahoo",
    "Skype",
    "Microsoft",
    "YouTube",
    "RuTube",
    "Gmail",
    "Mail.ru",
    "Wildberries",
    "OZON",
    "Steam",
    "Юла",
    "Avito",
    "Boosty",
    "Drom",
    "СберМегаМаркет",
    "hh",
    "Почта России",
    "Эльдорадо",
    "IVI",
    "Самокат",
    "Аптека Апрель",
    "СберАптека",
    "Лэтуаль",
    "Sunlight",
    "Metro",
    "LUKOIL-AZS",
    "Детский мир",
    "Apple",
    "X5ID",
    "Burger King",
    "Вкусно и Точка",
    "Dodopizza",
    "CoffeeLike",
    "Окей",
    "Dominos Pizza",
    "Шоколадница",
    "Магнит",
    "МВидео",
    "Maxim",
    "СпортМастер",
    "Lenta",
    "Lamoda",
    "Uralairlines",
    "Rbt",
    "BlaBlaCar",
    "ВкусВилл",
    "Uber",
    "Ашан",
    "MTS CashBack",
    "Twitter",
    "Alipay/Alibaba/1688",
    "KFC",
    "Rambler",
    "Amazon",
    "WeChat",
    "Mamba",
    "CDEK",
    "Bolt",
    "Delivery Club",
    "IQOS",
    "MEGA",
    "Wink",
    "Airbnb",
    "РСА",
    "myGLO",
    "MeetMe",
    "Uteka",
    "Weibo",
    "EscapeFromTarkov",
    "Tencent QQ",
    "Профи",
    "Pivko24",
    "KazanExpress",
    "Line messenger",
    "inDriver",
    "Tango",
    "Dostavista",
    "GalaxyChat",
    "ТОКИО-CITY",
    "Bilibili",
    "icq",
    "УлыбкаРадуги",
    "Wise",
    "RedBook",
    "Рив Гош",
    "Signal",
    "AOL",
    "Namars",
    "urent/jet/RuSharing",
    "constitutioner",
    "СушиВёсла",
    "Ollis",
    "VFS GLOBAL",
    "BRO",
    "BusyFly",
    "Podeli",
    "LigaPro",
    "Things",
    "iQIYI",
    "ЗдравСити",
    "DIKIDI",
    "nloto",
    "米画师Mihuashi",
    "Ортека",
    "Brevo",
    "МИГРАНТ СЕРВИС",
    "LadyMaria",
    "Yami",
    "Notifire",
    "Citymobil",
    "Zolushka",
    "Ximalaya",
    "Expressmoney",
    "SpaceWeb",
    "EnerGO",
    "ZaleyCash",
    "SynotTip",
    "Amasia",
    "Утконос",
    "Karusel",
    "Belwest",
    "Кузбасс Онлайн",
    "FarPost",
    "炙热星河",
    "UU163",
    "Bitrue",
    "MonetaRu",
    "Золотое Яблоко",
    "Голос",
    "Joyride",
    "Stormgain",
    "Энергобум",
    "Weverse",
    "TopDetal",
    "Zdorov",
    "Flowwow",
    "FreshKarta",
    "Домовой",
    "Switips",
    "Hermes",
    "MyLavash",
    "Лейка",
    "YouStar",
    "Vsesmart",
    "mosru",
    "TamTam",
    "Кораблик",
    "Megogo",
    "勇仕网络Ys4fun",
    "Huya",
    "PrivetMir",
    "PingCode",
    "Джилекс",
    "Sorare",
    "Consultant",
    "Uzum",
    "Royal Canin",
    "AptekiPlus",
    "Около",
    "Штолле",
    "Максавит",
    "CELEBe",
    "Taikang",
    "БлинБери",
    "Twilio",
    "LYKA",
    "SOKOLOV",
    "NimoTV",
    "ВсеИнструменты",
    "av100pro",
    "Radium",
    "YouDo",
    "SellMonitor",
    "Kwai",
    "PGbonus",
    "Cian",
    "AptekaRU",
    "Beget",
    "MarketGuru",
    "Careem",
    "Kaggle",
    "Dream11",
    "КухняНаРайоне",
    "Autoru",
    "ProtonMail",
    "Fiverr",
    "Bukalapak",
    "Фотострана",
    "Fruitz",
    "DewuPoison",
    "Idealista",
    "Hinge",
    "Naver",
    "Baidu",
    "OLX",
    "Grindr",
    "Nike",
    "KakaoTalk",
    "Yalla",
    "Zalo",
    "Happn",
    "Zoho",
    "OkCupid",
    "Bumble",
    "DiDi",
    "JDcom",
    "Sravni",
    "Xiaomi",
    "Ticketmaster",
    "Oldubil",
    "Cathay",
    "Craigslist",
    "Okko",
    "FoxFord",
    "Adidas",
    "CloudChat",
    "Mocospace",
    "163СOM",
    "Betfair",
    "Kamatera",
    "TenChat",
    "CallApp",
    "RegRu",
    "BitClout",
    "CommunityGaming",
    "Amway",
    "SticPay",
    "neftm",
    "Truecaller",
    "BeeBoo",
    "Gurmanika",
    "gpnbonus",
    "Zupee",
    "YAPPY",
    "premium.one",
    "Koshelek",
    "Бери заряд",
    "Clubhouse",
    "Author24",
    "Trip",
    "Perfluence",
    "Велобайк",
    "Likee",
    "Kia",
    "GORDAN",
    "TEAMORU",
    "Отзовик",
    "TANK",
    "START",
    "SamsungShop",
    "Şikayet var",
    "GMX",
    "mail.com",
    "Marlboro",
    "Cloud Manager",
    "Oriflame",
    "TheFork",
    "Bankera"
]