import logging
from datetime import datetime, timedelta

from aiogram.filters import ExceptionTypeFilter
from aiogram_dialog import DialogManager, StartMode, ShowMode
from aiogram_dialog.api.exceptions import UnknownIntent, UnknownState
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio

from aiogram import Dispatcher

from app.db.database import init_db
from app.dependencies import bot
from app.dialogs import setup_dialogs
from app.dialogs.bot_menu.states import BotMenu
from app.handlers import start_handler, affiliate_program, admin_handler, bot_handler
from app.services.notify_admins import notify_wakeup_bot
from app.services.periodic_tasks import check_sms, check_email, update_countries_and_services, check_payment
from app.services.set_bot_commands import set_default_commands
from app.services import bot_texts as bt


async def on_unknown_intent(event, dialog_manager: DialogManager):
    await dialog_manager.start(
        BotMenu.start, mode=StartMode.RESET_STACK, show_mode=ShowMode.AUTO,
    )


async def on_unknown_state(event, dialog_manager: DialogManager):
    await dialog_manager.start(
        BotMenu.start, mode=StartMode.RESET_STACK, show_mode=ShowMode.AUTO,
    )


async def main(dp: Dispatcher):
    main_routers = [
        admin_handler.router,
        start_handler.router,
        affiliate_program.router,
    ]
    dp.errors.register(
        on_unknown_intent,
        ExceptionTypeFilter(UnknownIntent),
    )
    dp.errors.register(
        on_unknown_state,
        ExceptionTypeFilter(UnknownState),
    )

    dp.include_routers(bot_handler.router, *main_routers)
    setup_dialogs(dp)

    await set_default_commands(bot)
    await init_db()
    await notify_wakeup_bot(bot)

    scheduler = AsyncIOScheduler()
    set_scheduled_jobs(scheduler)
    scheduler.start()

    await dp.start_polling(bot)


def set_scheduled_jobs(scheduler, *args, **kwargs):
    scheduler.add_job(check_sms, "interval", seconds=10, max_instances=3)
    scheduler.add_job(check_email, "interval", seconds=10, max_instances=3)
    scheduler.add_job(check_payment, "interval", seconds=10, max_instances=3)
    # scheduler.add_job(update_countries_and_services, "interval", minutes=30,
    #                   next_run_time=datetime.now() + timedelta(seconds=10), max_instances=3)


class SkipSpecificLogFilter(logging.Filter):
    def filter(self, record):
        return not (
            "Execution of job" in record.getMessage() and
            "skipped: maximum number of running instances reached" in record.getMessage()
        )


if __name__ == '__main__':
    from app.dependencies import dp

    # Настройка логирования
    logger = logging.getLogger('apscheduler')
    logger.setLevel(logging.WARNING)
    handler = logging.StreamHandler()
    handler.addFilter(SkipSpecificLogFilter())
    logger.addHandler(handler)

    asyncio.run(main(dp))