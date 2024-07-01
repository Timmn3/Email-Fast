import asyncio
from math import ceil

from app import dependencies
from app.db import models
from app.services.sms_activate_async import SMSActivateAPIAsync


class SmsReceive:
    """
    Класс для взаимодействия с API SMSActivate для получения и управления номерами телефонов.
    """

    def __init__(self):
        """
        Инициализация класса SmsReceive.
        """
        # Создаем экземпляр SMSActivateAPIAsync с API ключом
        self.sa = SMSActivateAPIAsync(api_key=dependencies.SMS_ACTIVATE_KEY)
        # self.sa = SMSActivateAPIAsync(api_key='8b16d24393b6c2256f458502b4A0A015')
        self.sa.debug_mode = False

    async def get_balance(self):
        """
        Получает баланс аккаунта в SMSActivate.

        :return: Баланс аккаунта.
        """
        return await self.sa.getBalance()

    async def get_countries(self):
        """
        Получает список стран, поддерживаемых SMSActivate.

        :return: Список стран с их идентификаторами и названиями.
        """
        countries_data = await self.sa.getCountries()
        countries = []
        for country_id, country_data in countries_data.items():
            countries.append({
                'id': country_id,
                'name': country_data['rus']
            })
            # Используем asyncio.sleep(0) для предотвращения блокировки
            await asyncio.sleep(0)

        return countries

    async def get_services(self):
        """
        Получает список сервисов и стран, поддерживаемых для аренды номеров.

        :return: Список сервисов с их кодами и именами для поиска.
        """
        services_data = await self.sa.getRentServicesAndCountries()
        # print(services_data, flush=True)
        services = []
        for service_code, service_data in services_data['services'].items():
            services.append({
                'code': service_code,
                'search_names': service_data['search_name']
            })
            # Используем asyncio.sleep(0) для предотвращения блокировки
            await asyncio.sleep(0)

        return services

    async def get_services_by_country_id(self, country_id: int):
        """
        Получает список сервисов для указанной страны.

        :param country_id: Идентификатор страны.
        :return: Список сервисов с их кодами, стоимостью и количеством доступных номеров.
        """
        services_data = await self.sa.getPrices(country=country_id)
        services = []
        for service_code, service_data in services_data[str(country_id)].items():
            # Округляем стоимость до ближайшего целого числа, умноженного на 1.3
            cost = ceil(float(service_data['cost']) * 1.3)
            services.append({
                'code': service_code,
                'cost': cost,
                'count': service_data['count']
            })
            # Используем asyncio.sleep(0) для предотвращения блокировки
            await asyncio.sleep(0)

        return services

    async def get_phone_number(self, country_id: int, service_code: str):
        """
        Получает номер телефона для указанной страны и сервиса.

        :param country_id: Идентификатор страны.
        :param service_code: Код сервиса.
        :return: Данные о номере телефона.
        """
        return await self.sa.getNumber(service=service_code, country=country_id)

    async def get_activation_status(self, activation_id: int):
        """
        Получает статус активации по идентификатору активации.

        :param activation_id: Идентификатор активации.
        :return: Статус активации.
        """
        return await self.sa.getStatus(id=activation_id)

    async def set_activation_status(self, activation_id: int, status: models.ActivationCode):
        """
        Устанавливает статус активации по идентификатору активации.

        :param activation_id: Идентификатор активации.
        :param status: Новый статус активации.
        :return: Результат установки статуса.
        """
        return await self.sa.setStatus(id=activation_id, status=status.value)

    async def get_number_status(self):
        """
        Получает статус номеров.

        :return: Статус номеров.
        """
        return await self.sa.getNumbersStatus()