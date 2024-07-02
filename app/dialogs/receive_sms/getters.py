from aiogram_dialog import DialogManager
from app.db import models
from app.services.sms_receive import SmsReceive
from app.services import bot_texts as bt


async def get_countries_service(dialog_manager: DialogManager, **middleware_data):
    ctx = dialog_manager.current_context()
    countries_with_prices = ctx.start_data.get("countries_with_prices")
    service_code = ctx.start_data.get("service_code")

    if countries_with_prices is not None:
        countries = [{"id": idx, "country": item['country'], "price": item['price']} for idx, item in
                     enumerate(countries_with_prices)]
    else:
        countries = []

    data = {
        "countries": countries,
        "service_code": service_code
    }
    return data


async def get_services(dialog_manager: DialogManager, **middleware_data):
    ctx = dialog_manager.current_context()
    country_id = ctx.start_data.get("country_id")
    if country_id is None:
        return {"services": []}

    search_service_name = ctx.dialog_data.get("search_service_name")
    if search_service_name is not None:
        find_services = await models.Service.search_service(search_service_name)
        find_services_codes = list(map(lambda x: x.code, find_services))
    else:
        find_services_codes = None

    sms = SmsReceive()
    services = await sms.get_services_by_country_id(country_id=country_id)
    services_list = []
    for service in services:
        if service['count'] < 5:
            continue

        service_obj = await models.Service.get_service(code=service['code'])
        if service_obj is None:
            continue

        if find_services_codes is not None and service_obj.code not in find_services_codes:
            continue

        service_data = {
            'code': service['code'],
            'cost': service['cost'],
            'name': service_obj.name
        }

        services_list.append(service_data)

    data = {
        "services": services_list
    }
    return data


async def get_services_2(dialog_manager: DialogManager, **middleware_data):
    services_db = await models.Service.get_services()
    return services_db


async def get_other_service(dialog_manager: DialogManager, **middleware_data):
    ctx = dialog_manager.current_context()
    country_id = ctx.start_data.get("country_id")
    if country_id is None:
        return {"services": []}

    sms = SmsReceive()
    services = await sms.get_services_by_country_id(country_id=country_id)
    services_list = []
    for service in services:
        if service['code'] != 'ot':
            continue

        service_obj = await models.Service.get_service(code=service['code'])
        service_data = {
            'code': service['code'],
            'cost': service['cost'],
            'name': service_obj.name
        }

        services_list.append(service_data)
        break

    data = {
        "services": services_list
    }
    return data


async def get_need_balance(dialog_manager: DialogManager, **middleware_data):
    ctx = dialog_manager.current_context()
    service_cost = ctx.dialog_data.get("service_cost")
    user = await models.User.get_user(dialog_manager.event.from_user.id)
    data = {
        "cost": service_cost,
        "balance": user.balance
    }
    return data


async def get_all_services(dialog_manager: DialogManager, **middleware_data):
    ctx = dialog_manager.current_context()
    country_id = ctx.start_data.get("country_id")
    if country_id is None:
        return {"services": []}

    search_service_name = ctx.dialog_data.get("search_service_name")
    if search_service_name is not None:
        find_services = await models.Service.search_service(search_service_name)
        find_services_codes = list(map(lambda x: x.code, find_services))
    else:
        find_services_codes = None

    sms = SmsReceive()
    services = await sms.get_services_by_country_id(country_id=country_id)
    services_list = []
    for service in services:
        if service['count'] < 5:
            continue

        service_obj = await models.Service.get_service(code=service['code'])
        if service_obj is None:
            continue

        if find_services_codes is not None and service_obj.code not in find_services_codes:
            continue

        service_data = {
            'code': service['code'],
            'cost': service['cost'],
            'name': service_obj.name
        }

        services_list.append(service_data)

    data = {
        "services": services_list
    }
    return data
