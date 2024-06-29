import asyncio
from math import ceil

from app import dependencies
from app.db import models
from app.services.sms_activate_async import SMSActivateAPIAsync


class SmsReceive:
    def __init__(self):
        self.sa = SMSActivateAPIAsync(api_key=dependencies.SMS_ACTIVATE_KEY)
        # self.sa = SMSActivateAPIAsync(api_key='8b16d24393b6c2256f458502b4A0A015')
        self.sa.debug_mode = False

    async def get_balance(self):
        return await self.sa.getBalance()

    async def get_countries(self):
        countries_data = await self.sa.getCountries()
        countries = []
        for country_id, country_data in countries_data.items():
            countries.append({
                'id': country_id,
                'name': country_data['rus']
            })
            await asyncio.sleep(0)

        return countries

    async def get_services(self):
        services_data = await self.sa.getRentServicesAndCountries()
        print(services_data, flush=True)
        services = []
        for service_code, service_data in services_data['services'].items():
            services.append({
                'code': service_code,
                'search_names': service_data['search_name']
            })
            await asyncio.sleep(0)

        return services

    async def get_services_by_country_id(self, country_id: int):
        services_data = await self.sa.getPrices(country=country_id)
        services = []
        for service_code, service_data in services_data[str(country_id)].items():
            cost = ceil(float(service_data['cost']) * 1.3)
            services.append({
                'code': service_code,
                'cost': cost,
                'count': service_data['count']
            })
            await asyncio.sleep(0)

        return services

    async def get_phone_number(self, country_id: int, service_code: str):
        return await self.sa.getNumber(service=service_code, country=country_id)

    async def get_activation_status(self, activation_id: int):
        return await self.sa.getStatus(id=activation_id)

    async def set_activation_status(self, activation_id: int, status: models.ActivationCode):
        return await self.sa.setStatus(id=activation_id, status=status.value)

    async def get_number_status(self):
        return await self.sa.getNumbersStatus()
